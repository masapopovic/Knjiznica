import psycopg2, psycopg2.extensions, psycopg2.extras, json
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki
import datetime
import os


import auth_public as auth_javnost  # uporabnik javnost
import auth as auth  # uporabnik jaz

from models import Clan, ClanDto, Knjiga, Avtor, BralnoSrecanje, Ocena, Izposoja, Rezervacija, KnjigaInAvtor, Udelezba
from typing import List

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





# Za uvoz podatkov (admin)
admin_repo = Repo(admin=True)
admin_repo.uvozi_knjige_iz_json("Data/knjige.json")

# Za normalno uporabo aplikacije (javnost)
repo = Repo(admin=False)
# tu potem kliceš funkcije za branje/izposojo knjig itd.