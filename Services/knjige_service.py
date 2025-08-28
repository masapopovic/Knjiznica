from Data.repository import Repo
from Data.models import *
import bcrypt
from datetime import date
from typing import Optional

class KnjigaService:
    def __init__(self):
        #uporabi javnega uporabnika za vse operacije
        self.repo = Repo(admin=False)
    
    def dobi_knjigo_po_id(self, id_knjige: int):
        return self.repo.dobi_knjigo_po_id(id_knjige)

    def prikazi_vse_knjige(self):
        return self.repo.poisci_knjige()

    def iskanje_knjig(self, naslov=None, avtor=None, zanri=None, min_ocena=None):
        return self.repo.poisci_knjige(naslov, avtor, zanri, min_ocena)

    def dobi_izposojene_knjige(self, id_clana: int):
        return self.repo.dobi_izposojene_knjige(id_clana)
    
    def izposodi_knjigo(self, id_clana: int, id_knjige: int):
        knjiga = self.repo.dobi_knjigo_po_id(id_knjige)
        if not knjiga:
            raise ValueError("Knjiga s tem ID ne obstaja.")
        if knjiga['razpolozljivost'] != 'na voljo':
            raise ValueError("Knjiga trenutno ni na voljo za izposojo.")

        self.repo.dodaj_izposojo(id_clana, id_knjige)
        self.repo.posodobi_razpolozljivost(id_knjige, 'ni na voljo')

    def vrni_knjigo_po_id(self, id_clana: int, id_knjige: int):
        knjiga = self.repo.dobi_knjigo_po_id(id_knjige)
        if not knjiga:
            raise ValueError("Knjiga s tem ID ne obstaja.")

        self.repo.dodaj_vracilo(id_clana, id_knjige)
        self.repo.posodobi_razpolozljivost(id_knjige, 'na voljo')

    def dobi_avtorje_knjige(self, id_knjige: int):
        return self.repo.dobi_avtorje_knjige(id_knjige)
    
