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
                # Vstavimo novega avtorja
                self.cur.execute(
                    "INSERT INTO avtor (ime, priimek) VALUES (%s, %s) RETURNING id_avtorja",
                    (knjiga['ime_avtorja'], knjiga['priimek_avtorja'])
                )
                id_avtorja = self.cur.fetchone()['id_avtorja']

            # Vstavimo knjigo
            self.cur.execute(
                "INSERT INTO knjiga (naslov, zanr, razpolozljivost) VALUES (%s, %s, %s) RETURNING id_knjige",
                (knjiga['naslov'], knjiga['žanri'], 'na voljo')
            )
            id_knjige = self.cur.fetchone()['id_knjige']

            # Povezovalna tabela knjiga_in_avtor
            self.cur.execute(
                "INSERT INTO knjiga_in_avtor (id_knjige, id_avtorja) VALUES (%s, %s)",
                (id_knjige, id_avtorja)
            )

        self.conn.commit()



    def dodaj_clana(self, clan: Clan):

        # hashiranje gesla
        hashed = bcrypt.hashpw(clan.geslo.encode("utf-8"), bcrypt.gensalt())
        hashed_str = hashed.decode("utf-8")  # da ga lahko shraniš kot TEXT

        self.cur.execute("""
            INSERT INTO clan (ime, priimek, uporabnisko_ime, geslo, email, status_clana)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id_clana
        """, (
            clan.ime,
            clan.priimek,
            clan.uporabnisko_ime,
            hashed_str,
            clan.email,
            clan.status_clana
        ))

        # posodobimo id_clana v Python objektu
        clan.id_clana = self.cur.fetchone()["id_clana"]
        self.conn.commit()
    
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

            

    def knjige_z_oceno_vecjo_od(self, min_ocena: int) -> List[Knjiga]:
        self.cur.execute("""
            SELECT 
                k.id_knjige,
                k.naslov,
                k.zanr,
                k.razpolozljivost
            FROM knjiga k
            JOIN ocena o ON k.id_knjige = o.id_knjige
            GROUP BY k.id_knjige, k.naslov, k.zanr, k.razpolozljivost
            HAVING AVG(o.ocena) > %s
            ORDER BY AVG(o.ocena) DESC
        """, (min_ocena,))
        return [Knjiga.from_dict(dict(row)) for row in self.cur.fetchall()]

    #knjige po žanrih
    def poisci_knjige_po_vec_zanrih(self, zanri: list[str]) -> list[Knjiga]:    #lahko iščeš po več žanrih
        self.cur.execute("""
            SELECT id_knjige, naslov, zanr, razpolozljivost
            FROM knjiga
            WHERE zanr && %s::text[]
        """, (zanri,))
        rows = self.cur.fetchall()
        return [Knjiga.from_dict(dict(row)) for row in rows]
    
    #knjige po avtorjih
    def dobi_knjige_po_avtorju(self, ime: Optional[str] = None, priimek: Optional[str] = None) -> List[Knjiga]:
        """
        Vrne seznam knjig, ki jih je napisal avtor z določenim imenom in/ali priimkom.
        Če je ime ali priimek None, se ignorira pri iskanju.
        """
        query = """
        SELECT 
            k.id_knjige,
            k.naslov,
            k.zanr,
            k.razpolozljivost
        FROM knjiga k
        JOIN knjiga_in_avtor ka ON k.id_knjige = ka.id_knjige
        JOIN avtor a ON ka.id_avtorja = a.id_avtorja
        WHERE 1=1
        """
        params = []
        if ime:
            query += " AND LOWER(a.ime) LIKE LOWER(%s)"
            params.append(f"%{ime}%")
        if priimek:
            query += " AND LOWER(a.priimek) LIKE LOWER(%s)"
            params.append(f"%{priimek}%")
        
        self.cur.execute(query, params)
        return [Knjiga.from_dict(dict(row)) for row in self.cur.fetchall()]








#Za uvoz podatkov (admin)
#admin_repo = Repo(admin=True)
#admin_repo.uvozi_knjige_iz_json("Data/knjige.json")

#Za normalno uporabo aplikacije (javnost)
repo = Repo(admin=False)
