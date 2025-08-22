import psycopg2, psycopg2.extensions, psycopg2.extras, json, bcrypt
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki
import datetime
import os


import auth_public as auth_javnost  # uporabnik javnost
import auth as auth  # uporabnik jaz

from models import Clan, ClanDto, Knjiga, Avtor, BralnoSrecanje, Ocena, Izposoja, Rezervacija, KnjigaInAvtor, Udelezba
from typing import List
from typing import Optional, List

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
        return row['povprecje'] if row and row['povprecje'] is not None else 0
    
    def dobi_ocene_po_naslovu_in_avtorju(self, naslov_knjige: Optional[str] = None, avtor: Optional[str] = None) -> List[dict]:
        query = """
        SELECT 
            o.id_ocene,
            o.ocena,
            o.datum,
            o.komentar,
            o.id_clana,
            c.ime || ' ' || c.priimek AS clan,
            k.naslov AS knjiga,
            k.avtor AS avtor_knjige
        FROM ocena o
        JOIN clan c ON o.id_clana = c.id_clana
        JOIN knjiga k ON o.id_knjige = k.id_knjige
        WHERE 1=1
        """
        params = []
        if naslov_knjige:
            query += " AND LOWER(k.naslov) = LOWER(%s)"
            params.append(naslov_knjige)
            if avtor:
                query += " AND LOWER(k.avtor) = LOWER(%s)"
                params.append(avtor)
                query += " ORDER BY o.id_ocene ASC"
                self.cur.execute(query, params)
                return [dict(row) for row in self.cur.fetchall()]






#Za uvoz podatkov (admin)
#admin_repo = Repo(admin=True)
#admin_repo.uvozi_knjige_iz_json("Data/knjige.json")

#Za normalno uporabo aplikacije (javnost)
repo = Repo(admin=False)
