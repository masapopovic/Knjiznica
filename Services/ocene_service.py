from Data.repository import Repo
from Data.models import Ocena, Knjiga
from datetime import datetime
from typing import List, Optional


class OcenaService:
    def __init__(self):
        #uporabi javnega uporabnika za vse operacije
        self.repo = Repo(admin=False)


    def povprecna_ocena_knjige(self, id_knjige: int) -> Optional[float]:
        return self.repo.povprecna_ocena_knjige(id_knjige)
    

    def ocene_po_id_knjige(self, id_knjige: int) -> list[Ocena]:
        return self.repo.ocene_po_id_knjige(id_knjige)

    
    
    def dodaj_oceno_vsem_izvodom(self, id_clana: int, id_knjige: int, ocena: int, komentar: str = ""):
        """
        Doda oceno vsem izvodom knjige, ki imajo enak naslov in iste avtorje kot knjiga z id_knjige.
        """
        ocena_obj = Ocena(
            id_clana=id_clana,
            id_knjige=id_knjige,
            ocena=ocena,
            komentar=komentar
        )

        self.repo.dodaj_oceno_vsem_izvodom_po_id(ocena_obj)



