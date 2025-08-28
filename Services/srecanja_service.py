
from Data.repository import Repo
from Data.models import *
import bcrypt
from datetime import date
from typing import Optional

class SrecanjaService:
    def __init__(self):
        #uporabi javnega uporabnika za vse operacije
        self.repo = Repo(admin=False)
        
    def prikazi_prihodnja_srecanja(self):
        return self.repo.prikazi_prihodnja_srecanja()

    def prijava_na_srecanje(self, id_clana: int, datum: str, naziv: str):
        srecanje = self.repo.get_srecanje(datum, naziv)
        if not srecanje:
            raise ValueError("Srečanje s tem datumom in nazivom ne obstaja.")

        id_srecanja = srecanje['id_srecanja']

        if self.repo.preveri_udelezbo(id_clana, id_srecanja):
            raise ValueError("Član je že prijavljen na to srečanje.")

        self.repo.dodaj_udelezbo(id_clana, id_srecanja)

    def prihodnja_srecanja_po_clanu(self, id_clana: int):
        return self.repo.prihodnja_srecanja_po_clanu(id_clana)

    def isci_prihodnja_srecanja(self, naziv: str = None, datum: str = None):
        return self.repo.isci_prihodnja_srecanja(naziv=naziv, datum=datum)

    def najdi_nazive(self, fragment: str) -> list[str]:
        return self.repo.najdi_nazive(fragment)
