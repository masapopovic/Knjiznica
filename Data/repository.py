import psycopg2, psycopg2.extensions, psycopg2.extras, json, bcrypt
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki
import datetime
import os
from typing import List, Optional


import auth_public as auth_javnost  # uporabnik javnost
import auth as auth  # uporabnik jaz

from models import Clan, ClanDto, Knjiga, Avtor, BralnoSrecanje, Ocena, Izposoja, Rezervacija, KnjigaInAvtor, Udelezba

DB_PORT = os.environ.get('POSTGRES_PORT', 5432)


class Repo:
    def __init__(self, admin=False):
        """
        Če je admin=True, uporabi admin uporabnika, sicer javnost.
        """
        if admin:
            self.conn = psycopg2.connect(
                database=auth.db,
                host=auth.host,
                user=auth.user,
                password=auth.password,
                port=DB_PORT
            )
        else:
            self.conn = psycopg2.connect(
                database=auth_javnost.db,
                host=auth_javnost.host,
                user=auth_javnost.user,
                password=auth_javnost.password,
                port=DB_PORT
            )
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    def uvozi_knjige_iz_json(self, pot_do_json: str):
        with open(pot_do_json, 'r', encoding='utf-8') as f:
            podatki = json.load(f)

        for knjiga in podatki:
            # Preverimo ali avtor že obstaja
            self.cur.execute(
                "SELECT id_avtorja FROM avtor WHERE ime=%s AND priimek=%s",
                (knjiga['ime_avtorja'], knjiga['priimek_avtorja'])
            )
            avtor = self.cur.fetchone()
            if avtor:
                id_avtorja = avtor['id_avtorja']
            else:
                self.cur.execute(
                    "INSERT INTO avtor (ime, priimek) VALUES (%s, %s) RETURNING id_avtorja",
                    (knjiga['ime_avtorja'], knjiga['priimek_avtorja'])
                )
                id_avtorja = self.cur.fetchone()['id_avtorja']

            # Vstavimo knjigo 
            self.cur.execute(
                "INSERT INTO knjiga (naslov, razpolozljivost) VALUES (%s, %s) RETURNING id_knjige",
                (knjiga['naslov'], 'na voljo')
            )
            id_knjige = self.cur.fetchone()['id_knjige']

            # Povezovalna tabela knjiga_in_avtor
            self.cur.execute(
                "INSERT INTO knjiga_in_avtor (id_knjige, id_avtorja) VALUES (%s, %s)",
                (id_knjige, id_avtorja)
            )

            # obdelava žanrov
            for ime_zanra in knjiga['žanri']:
                # preverimo ali žanr že obstaja
                self.cur.execute(
                    "SELECT id_zanra FROM zanr WHERE ime_zanra = %s",
                    (ime_zanra,)
                )
                zanr = self.cur.fetchone()
                if zanr:
                    id_zanra = zanr['id_zanra']
                else:
                    # dodamo nov žanr
                    self.cur.execute(
                        "INSERT INTO zanr (ime_zanra) VALUES (%s) RETURNING id_zanra",
                        (ime_zanra,)
                    )
                    id_zanra = self.cur.fetchone()['id_zanra']

                # povežemo knjigo z žanrom
                self.cur.execute(
                    "INSERT INTO knjiga_in_zanr (id_knjige, id_zanra) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                    (id_knjige, id_zanra)
                )

        self.conn.commit()

    def dobi_clana_po_id(self, id_clana: int) -> Optional[Clan]:
        self.cur.execute(
            "SELECT * FROM clan WHERE id_clana = %s",
            (id_clana,)
        )
        row = self.cur.fetchone()
        if row:
            return Clan.from_dict(dict(row))
        return None

    
    def dobi_clana_po_uporabniskem_imenu(self, uporabnisko_ime: str) -> Optional[Clan]:
        self.cur.execute(
            "SELECT * FROM clan WHERE uporabnisko_ime = %s",
            (uporabnisko_ime,)
        )
        row = self.cur.fetchone()
        if row:
            return Clan.from_dict(dict(row))
        return None   


    def dodaj_clana(self, clan: Clan) -> Clan:
        self.cur.execute("""
            INSERT INTO clan (ime, priimek, uporabnisko_ime, geslo, email, status_clana)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id_clana
        """, (
            clan.ime,
            clan.priimek,
            clan.uporabnisko_ime,
            clan.password_hash,   
            clan.email,
            clan.status_clana
        ))
        clan.id_clana = self.cur.fetchone()["id_clana"]
        self.conn.commit()
        return clan


    # Ocene
    def dodaj_oceno(self, o: Ocena):
        self.cur.execute("""
                         INSERT INTO ocena (ocena, datum, komentar, id_clana, id_knjige)
                         VALUES (%s, %s, %s, %s, %s)
                         """, (
                             o.ocena, o.datum, o.komentar, o.id_clana, o.id_knjige
                             ))
        self.conn.commit()
        
        
    def povprecna_ocena_knjige(self, id_knjige: int) -> Optional[float]:
        self.cur.execute("""
            SELECT ROUND(AVG(ocena)::numeric, 2) AS povprecje
            FROM ocena
            WHERE id_knjige = %s
        """, (id_knjige,))
        row = self.cur.fetchone()
        return float(row['povprecje']) if row and row['povprecje'] is not None else None

    
    def dobi_ocene_po_naslovu_in_avtorju(
        self, 
        naslov_knjige: Optional[str] = None, 
        ime_avtorja: Optional[str] = None, 
        priimek_avtorja: Optional[str] = None
    ) -> List[Ocena]:
        """
        Vrne seznam ocen glede na naslov knjige in/ali ime in priimek avtorja.
        Če je katerikoli argument None, se ignorira pri iskanju.
        """
        query = """
        SELECT 
            o.id_ocene,
            o.ocena,
            o.datum,
            o.komentar,
            o.id_clana,
            o.id_knjige
        FROM ocena o
        JOIN knjiga k ON o.id_knjige = k.id_knjige
        JOIN knjiga_in_avtor ka ON k.id_knjige = ka.id_knjige
        JOIN avtor a ON ka.id_avtorja = a.id_avtorja
        WHERE 1=1
        """
        params = []
        
        if naslov_knjige:
            query += " AND LOWER(k.naslov) = LOWER(%s)"
            params.append(naslov_knjige)
        if ime_avtorja:
            query += " AND LOWER(a.ime) LIKE LOWER(%s)"
            params.append(f"%{ime_avtorja}%")
        if priimek_avtorja:
            query += " AND LOWER(a.priimek) LIKE LOWER(%s)"
            params.append(f"%{priimek_avtorja}%")
        
        query += " ORDER BY o.id_ocene ASC"
        
        self.cur.execute(query, params)
        return [Ocena.from_dict(dict(row)) for row in self.cur.fetchall()]

            


    #knjige po žanrih, avtorjih, naslovih ter povp. oceni
    def poisci_knjige(self, naslov: str = None, avtor: str = None, zanri: list[str] = None, min_ocena: int = None) -> list[Knjiga]:
        """
        Išče knjige glede na naslov, avtorja, žanre in minimalno povprečno oceno.
        Vrača vse ustrezne knjige.
        """
        query = """
            SELECT DISTINCT k.id_knjige, k.naslov, k.razpolozljivost
            FROM knjiga k
            LEFT JOIN knjiga_in_avtor ka ON k.id_knjige = ka.id_knjige
            LEFT JOIN avtor a ON ka.id_avtorja = a.id_avtorja
            LEFT JOIN knjiga_in_zanr kz ON k.id_knjige = kz.id_knjige
            LEFT JOIN zanr z ON kz.id_zanra = z.id_zanra
            LEFT JOIN ocena o ON k.id_knjige = o.id_knjige
            WHERE 1=1
        """
        params = []

        if naslov:
            query += " AND LOWER(k.naslov) LIKE LOWER(%s)"
            params.append(f"%{naslov}%")
        if avtor:
            query += " AND (LOWER(a.ime) LIKE LOWER(%s) OR LOWER(a.priimek) LIKE LOWER(%s))"
            params.extend([f"%{avtor}%", f"%{avtor}%"])
        if zanri:
            query += " AND LOWER(z.ime_zanra) = ANY(%s)"
            params.append(zanri)
        if min_ocena:
            query += " GROUP BY k.id_knjige HAVING AVG(o.ocena) >= %s"
            params.append(min_ocena)
        
        query += " ORDER BY k.razpolozljivost DESC"

        self.cur.execute(query, params)
        rows = self.cur.fetchall()
        return [Knjiga.from_dict(dict(row)) for row in rows]

    
    def dobi_knjigo_po_id(self, id_knjige: int):
        self.cur.execute("SELECT * FROM knjiga WHERE id_knjige = %s", (id_knjige,))
        return self.cur.fetchone()
    
    def dobi_avtorje_knjige(self, id_knjige: int):
        self.cur.execute("""
            SELECT a.ime, a.priimek
            FROM avtor a
            JOIN knjiga_in_avtor ka ON a.id_avtorja = ka.id_avtorja
            WHERE ka.id_knjige = %s
        """, (id_knjige,))
        return self.cur.fetchall()  # vrne seznam dict: [{'ime':..., 'priimek':...}, ...]


    #izposoja
    def dodaj_izposojo(self, id_clana: int, id_knjige: int):
        self.cur.execute(
            "INSERT INTO izposoja (id_clana, id_knjige) VALUES (%s, %s)",
            (id_clana, id_knjige)
        )

    def posodobi_razpolozljivost(self, id_knjige: int, razpolozljivost: str):
        self.cur.execute(
            "UPDATE knjiga SET razpolozljivost = %s WHERE id_knjige = %s",
            (razpolozljivost, id_knjige)
        )
        self.conn.commit()

    # Izposojene knjige
    def dobi_izposojene_knjige(self, id_clana: int) -> list[Knjiga]:
        self.cur.execute("""
            SELECT k.id_knjige, k.naslov, k.razpolozljivost, i.rok_vracila
            FROM izposoja i
            JOIN knjiga k ON i.id_knjige = k.id_knjige
            WHERE i.id_clana = %s AND i.vraceno = FALSE
        """, (id_clana,))
        rows = self.cur.fetchall()
        return [Knjiga.from_dict(dict(row)) for row in rows]
        
    #vračilo 
    def dodaj_vracilo(self, id_clana: int, id_knjige: int):
        self.cur.execute(
            "INSERT INTO vracila (id_clana, id_knjige) VALUES (%s, %s)",
            (id_clana, id_knjige)
        )



    #Bralno srecanje

    # Poišči srečanje po datumu in nazivu
    def isci_prihodnja_srecanja(self, naziv: str = None, datum: str = None) -> list[BralnoSrecanje]:
        query = """
            SELECT * FROM bralno_srecanje
            WHERE datum >= CURRENT_DATE
        """
        params = []

        if naziv:
            query += " AND LOWER(naziv_in_opis) LIKE LOWER(%s)"
            params.append(f"%{naziv}%")

        if datum:
            query += " AND datum::date = %s"
            params.append(datum)

        query += " ORDER BY datum ASC"

        self.cur.execute(query, params)
        rows = self.cur.fetchall()
        return [BralnoSrecanje.from_dict(dict(row)) for row in rows]


    # Preveri, ali je član že prijavljen
    def preveri_udelezbo(self, id_clana: int, id_srecanja: int):
        self.cur.execute(
            "SELECT 1 FROM udelezba WHERE id_clana = %s AND id_srecanja = %s",
            (id_clana, id_srecanja)
        )
        return self.cur.fetchone() is not None

    # Vstavi prijavo člana
    def dodaj_udelezbo(self, id_clana: int, id_srecanja: int):
        self.cur.execute(
            "INSERT INTO udelezba (id_clana, id_srecanja) VALUES (%s, %s)",
            (id_clana, id_srecanja)
        )
        self.conn.commit()

    #prihodnja srečanja
    def prikazi_prihodnja_srecanja(self) -> List[BralnoSrecanje]:
        """
        Vrne seznam vseh bralnih srečanj, ki še niso potekla.
        """
        self.cur.execute("""
            SELECT 
                id_srecanja,
                prostor,
                datum,
                naziv_in_opis,
                id_knjige
            FROM bralno_srecanje
            WHERE datum >= CURRENT_DATE
            ORDER BY datum ASC
        """)
        rows = self.cur.fetchall()
        return [BralnoSrecanje.from_dict(dict(row)) for row in rows]
    
    def prihodnja_srecanja_po_clanu(self, id_clana: int) -> list[BralnoSrecanje]:
        """
        Vrne seznam vseh prihodnjih bralnih srečanj, na katera je prijavljen določen član.
        """
        self.cur.execute("""
            SELECT bs.id_srecanja, bs.prostor, bs.datum, bs.naziv_in_opis, bs.id_knjige
            FROM bralno_srecanje bs
            JOIN udelezba u ON bs.id_srecanja = u.id_srecanja
            WHERE u.id_clana = %s AND bs.datum >= CURRENT_DATE
            ORDER BY bs.datum ASC
        """, (id_clana,))

        rows = self.cur.fetchall()
        return [BralnoSrecanje.from_dict(dict(row)) for row in rows]
    
    def najdi_nazive(self, fragment: str) -> list[str]:
        self.cur.execute("""
            SELECT DISTINCT naziv_in_opis
            FROM bralno_srecanje
            WHERE LOWER(naziv_in_opis) LIKE LOWER(%s)
            ORDER BY naziv_in_opis ASC
            LIMIT 10
        """, (f"%{fragment}%",))

        return [row['naziv_in_opis'] for row in self.cur.fetchall()]










#Za uvoz podatkov (admin)
#admin_repo = Repo(admin=True)
#admin_repo.uvozi_knjige_iz_json("Data/knjige.json")

#Za normalno uporabo aplikacije (javnost)
#repo = Repo(admin=False)
