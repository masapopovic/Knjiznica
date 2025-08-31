
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

    def prijava_na_srecanje(self, id_clana: int, id_srecanja: int):
        # Dobimo srečanje po ID-ju
        srecanje = self.repo.get_srecanje_po_id(id_srecanja)

        if not srecanje:
            raise ValueError("Srečanje s tem ID-jem ne obstaja.")

        if self.repo.preveri_udelezbo(id_clana, id_srecanja):
            raise ValueError("Član je že prijavljen na to srečanje.")

        self.repo.dodaj_udelezbo(id_clana, id_srecanja)


    def je_clan_prijavljen(self, id_clana: int, id_srecanja: int) -> bool:
        return self.repo.preveri_udelezbo(id_clana, id_srecanja)

    def prihodnja_srecanja_po_clanu(self, id_clana: int):
        return self.repo.prihodnja_srecanja_po_clanu(id_clana)

    def isci_prihodnja_srecanja(self, naziv: str = None, datum: str = None):
        return self.repo.isci_prihodnja_srecanja(naziv=naziv, datum=datum)
    
    def stevilo_prijavljenih(self, id_srecanja: int) -> int:
        return self.repo.stevilo_prijavljenih(id_srecanja)


