from Data.repository import Repo
from Data.models import *
import bcrypt
from datetime import date
from typing import Optional

class AuthService:
    def __init__(self):
        #uporabi javnega uporabnika za vse operacije
        self.repo = Repo(admin=False)

    def registracija_clana(self, ime: str, priimek: str, uporabnisko_ime: str, geslo: str, email: str) -> ClanDto:
        # Preveri, ali uporabniško ime že obstaja
        obstojeci = self.repo.dobi_clana_po_uporabniskem_imenu(uporabnisko_ime)
        if obstojeci:
            raise ValueError("Uporabniško ime že obstaja.")

        # Hashiranje gesla
        geslo_hash = bcrypt.hashpw(geslo.encode("utf-8"), bcrypt.gensalt())
        geslo_hash_str = geslo_hash.decode("utf-8")

        # Ustvari objekt Clan
        clan = Clan(
            ime=ime,
            priimek=priimek,
            uporabnisko_ime=uporabnisko_ime,
            password_hash=geslo_hash_str,
            email=email,
            status_clana="aktiven"
        )

        # Shrani v bazo
        clan = self.repo.dodaj_clana(clan)
        return ClanDto(
            id_clana=clan.id_clana,
            ime=clan.ime,
            priimek=clan.priimek,
            uporabnisko_ime=clan.uporabnisko_ime,
            status_clana=clan.status_clana
        )
    
    def pridobi_clana_po_id(self, id_clana: int) -> ClanDto:
        clan = self.repo.dobi_clana_po_id(id_clana)
        if not clan:
            raise ValueError("Član s tem ID ne obstaja.")
        return ClanDto(
            id_clana=clan.id_clana,
            ime=clan.ime,
            priimek=clan.priimek,
            uporabnisko_ime=clan.uporabnisko_ime,
            status_clana=clan.status_clana
        )

    def prijava_clana(self, uporabnisko_ime: str, geslo: str) -> ClanDto:
        clan = self.repo.dobi_clana_po_uporabniskem_imenu(uporabnisko_ime)
        if not clan:
            raise ValueError("Uporabnik ne obstaja.")

        # Preveri geslo
        if not bcrypt.checkpw(geslo.encode("utf-8"), clan.password_hash.encode("utf-8")):
            raise ValueError("Napačno geslo.")

        # Če je vse ok, vrni ClanDto
        return ClanDto(
            id_clana=clan.id_clana,
            ime=clan.ime,
            priimek=clan.priimek,
            uporabnisko_ime=clan.uporabnisko_ime,
            status_clana=clan.status_clana
        )