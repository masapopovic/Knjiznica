import psycopg2, psycopg2.extensions, psycopg2.extras, json, bcrypt
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki
import datetime
import os
from typing import List, Optional


from . import auth_public as auth_javnost # uporabnik javnost
from . import auth as auth  # uporabnik jaz

from Data.models import Clan, ClanDto, Knjiga, Avtor, BralnoSrecanje, Ocena, Izposoja, Rezervacija, KnjigaInAvtor, Udelezba, Zanr

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
    
    def dodaj_oceno_vsem_izvodom_po_id(self, ocena_obj: Ocena):
        """
        Doda oceno vsem izvodom knjige, ki imajo enak naslov in iste avtorje kot knjiga z id_knjige.
        """
        self.cur.execute("""
            INSERT INTO ocena (id_clana, id_knjige, ocena, komentar, datum)
            SELECT %s, k.id_knjige, %s, %s, CURRENT_DATE
            FROM knjiga k
            WHERE k.naslov = (SELECT naslov FROM knjiga WHERE id_knjige = %s)
            AND k.id_knjige IN (
                SELECT ka.id_knjige
                FROM knjiga_in_avtor ka
                WHERE ka.id_knjige = k.id_knjige
                GROUP BY ka.id_knjige
                HAVING ARRAY_AGG(ka.id_avtorja ORDER BY ka.id_avtorja) =
                    (SELECT ARRAY_AGG(id_avtorja ORDER BY id_avtorja) 
                        FROM knjiga_in_avtor 
                        WHERE id_knjige = %s)
            )
        """, (
            ocena_obj.id_clana,
            ocena_obj.ocena,
            ocena_obj.komentar,
            ocena_obj.id_knjige,
            ocena_obj.id_knjige
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

    def ocene_po_id_knjige(self, id_knjige: int) -> list[Ocena]:
        """
        Vrne seznam vseh ocen za določen izvod knjige.
        """
        self.cur.execute("""
            SELECT id_ocene, ocena, datum, komentar, id_clana, id_knjige
            FROM ocena
            WHERE id_knjige = %s
            ORDER BY id_ocene DESC
        """, (id_knjige,))
        
        rows = self.cur.fetchall()
        return [Ocena.from_dict(dict(row)) for row in rows]



    #knjige po žanrih, avtorjih, naslovih ter povp. oceni
    def poisci_knjige(
            self,
            naslov: str = None,
            avtorji: list[str] = None,
            zanri: list[str] = None,
            min_ocena: int = None
        ) -> list[Knjiga]:
        """
        Išče knjige glede na naslov, seznam avtorjev, seznam žanrov in minimalno povprečno oceno.
        Če so podani avtorji ali žanri, vrne samo knjige, ki vsebujejo vse te avtorje in/ali vse te žanre.
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

        # Avtorji kot seznam
        if avtorji:
            avtorji_lower = [a.strip().lower() for a in avtorji]
            query += """
                AND k.id_knjige IN (
                    SELECT ka.id_knjige
                    FROM knjiga_in_avtor ka
                    JOIN avtor a ON ka.id_avtorja = a.id_avtorja
                    WHERE LOWER(a.ime || ' ' || a.priimek) = ANY(%s)
                    GROUP BY ka.id_knjige
                    HAVING COUNT(DISTINCT a.id_avtorja) = %s
                )
            """
            params.append(avtorji_lower)
            params.append(len(avtorji_lower))

        # Žanri kot seznam
        if zanri:
            zanri_lower = [z.lower() for z in zanri]
            query += """
                AND k.id_knjige IN (
                    SELECT kz.id_knjige
                    FROM knjiga_in_zanr kz
                    JOIN zanr z ON kz.id_zanra = z.id_zanra
                    WHERE LOWER(z.ime_zanra) = ANY(%s)
                    GROUP BY kz.id_knjige
                    HAVING COUNT(DISTINCT z.id_zanra) = %s
                )
            """
            params.append(zanri_lower)
            params.append(len(zanri_lower))

        if min_ocena:
            query += " GROUP BY k.id_knjige HAVING AVG(o.ocena) >= %s"
            params.append(min_ocena)

        query += " ORDER BY k.razpolozljivost DESC"

        self.cur.execute(query, params)
        rows = self.cur.fetchall()
        return [Knjiga.from_dict(dict(row)) for row in rows]

        
    def dobi_knjigo_po_id(self, id_knjige: int) -> Knjiga | None:
        self.cur.execute("""
            SELECT id_knjige, naslov, razpolozljivost
            FROM knjiga
            WHERE id_knjige = %s
        """, (id_knjige,))
        row = self.cur.fetchone()
        if row:
            return Knjiga.from_dict(dict(row))
        return None

    
    def dobi_avtorje_knjige(self, id_knjige: int):
        self.cur.execute("""
            SELECT a.ime, a.priimek
            FROM avtor a
            JOIN knjiga_in_avtor ka ON a.id_avtorja = ka.id_avtorja
            WHERE ka.id_knjige = %s
        """, (id_knjige,))
        rows = self.cur.fetchall() 
        return [Avtor.from_dict(dict(row)) for row in rows]
    
    
    def dobi_zanre_knjige(self, id_knjige: int) -> list[Zanr]:
        self.cur.execute("""
            SELECT z.id_zanra, z.ime_zanra
            FROM zanr z
            JOIN knjiga_in_zanr kz ON z.id_zanra = kz.id_zanra
            WHERE kz.id_knjige = %s
        """, (id_knjige,))
        rows = self.cur.fetchall()
        return [Zanr.from_dict(dict(row)) for row in rows]

 

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
        """
        Vrne seznam knjig, ki jih je član trenutno izposodil
        (tj. kjer še ni potekel rok vračila).
        """
        self.cur.execute("""
            SELECT k.id_knjige, k.naslov, k.razpolozljivost, i.rok_vracila
            FROM izposoja i
            JOIN knjiga k ON i.id_knjige = k.id_knjige
            WHERE i.id_clana = %s
            AND i.rok_vracila >= CURRENT_DATE
        """, (id_clana,))
        rows = self.cur.fetchall()
        knjige = [Knjiga.from_dict(dict(row)) for row in rows]
        for i, row in enumerate(rows):
            knjige[i].rok_vracila = row['rok_vracila']
        return knjige


    #vračilo 
    def dodaj_vracilo(self, id_clana: int, id_knjige: int):
        self.cur.execute(
            "INSERT INTO vracila (id_clana, id_knjige) VALUES (%s, %s)",
            (id_clana, id_knjige)
        )



    #Bralno srecanje

    def get_srecanje_po_id(self, id_srecanja: int):
        """
        Vrne podatke o bralnem srečanju glede na id_srecanja.
        """
        self.cur.execute("""
            SELECT 
                id_srecanja,
                prostor,
                datum,
                naziv_in_opis,
                id_knjige
            FROM bralno_srecanje
            WHERE id_srecanja = %s
        """, (id_srecanja,))
        row = self.cur.fetchone()
        return dict(row) if row else None

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
    
    def stevilo_prijavljenih(self, id_srecanja: int) -> int:
        self.cur.execute(
            "SELECT COUNT(*) as cnt FROM udelezba WHERE id_srecanja=%s",
            (id_srecanja,)
        )
        return self.cur.fetchone()["cnt"]


    











#Za uvoz podatkov (admin)
#admin_repo = Repo(admin=True)
#admin_repo.uvozi_knjige_iz_json("Data/knjige.json")

#Za normalno uporabo aplikacije (javnost)
#repo = Repo(admin=False)
