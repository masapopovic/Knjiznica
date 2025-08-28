from Data.repository import Repo
from Data.models import *
import bcrypt
from datetime import date
from typing import Optional

class LibraryService:
    def __init__(self):
        #uporabi javnega uporabnika za vse operacije
        self.repo = Repo(admin=False)

    def poisci_knjige_po_naslovu(self, naslov: str):
        knjige = self.repo.get_knjige_po_naslovu(naslov)
        if not knjige:
            raise ValueError("Ni knjig s tem naslovom.")
        return [Knjiga.from_dict(dict(k)) for k in knjige]

    def poisci_knjige_po_avtorju(self, avtor: str):
        knjige = self.repo.get_knjige_po_avtorju(avtor)
        if not knjige:
            raise ValueError("Ni knjig tega avtorja.")
        return [Knjiga.from_dict(dict(k)) for k in knjige]
    
    def poisci_knjige_po_vec_zanrih(self, zanri: list[str]) -> list[Knjiga]:
        """
        Vrne knjige, ki imajo vse podane žanre.
        """
        if not zanri:
            raise ValueError("Seznam žanrov ne sme biti prazen.")

        knjige = self.repo.poisci_knjige_po_vec_zanrih(zanri)
        if not knjige:
            raise ValueError(f"Ni knjig z vsemi žanri: {', '.join(zanri)}.")
        return knjige
    
    def knjige_z_oceno_vecjo_od(self, min_ocena: int) -> list[Knjiga]:
        """
        Vrne seznam knjig, katerih povprečna ocena je večja od min_ocena.
        """
        knjige = self.repo.knjige_z_oceno_vecjo_od(min_ocena)
        if not knjige:
            raise ValueError(f"Ni knjig s povprečno oceno večjo od {min_ocena}.")
        return knjige
    
    def izposodi_knjigo_po_id(self, id_clana: int, id_knjige: int):
        knjiga = self.repo.get_knjiga(id_knjige)
        if not knjiga:
            raise ValueError("Knjiga s tem ID ne obstaja.")
        if knjiga['razpolozljivost'] != 'na voljo':
            raise ValueError("Knjiga trenutno ni na voljo za izposojo.")

        self.repo.dodaj_izposojo(id_clana, id_knjige)
        self.repo.posodobi_razpoložljivost(id_knjige, 'ni na voljo')

    def vrni_knjigo_po_id(self, id_clana: int, id_knjige: int):
        knjiga = self.repo.get_knjiga(id_knjige)
        if not knjiga:
            raise ValueError("Knjiga s tem ID ne obstaja.")

        self.repo.dodaj_vracilo(id_clana, id_knjige)
        self.repo.posodobi_razpoložljivost(id_knjige, 'na voljo')
    
