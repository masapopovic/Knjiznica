from Data.repository import Repo
from Data.models import Ocena, Knjiga
from datetime import datetime
from typing import List, Optional


class OcenaService:
    def __init__(self):
        self.repo = Repo()

    def dodaj_oceno(self, ocena: int, komentar: str, id_clana: int, id_knjige: int) -> bool:
        """
        Doda novo oceno knjigi.
        """
        if ocena < 1 or ocena > 5:
            return False  # Ocena mora biti med 1 in 5
        
        nova_ocena = Ocena(
            ocena=ocena,
            datum=datetime.now(),
            komentar=komentar,
            id_clana=id_clana,
            id_knjige=id_knjige
        )
        self.repo.dodaj_oceno(nova_ocena)
        return True

    def povprecna_ocena_knjige(self, id_knjige: int) -> Optional[float]:
        """
        Vrne povprečno oceno za izbrano knjigo.
        """
        return self.repo.povprecna_ocena_knjige(id_knjige)

    def ocene_po_naslovu_in_avtorju(
        self, 
        naslov_knjige: Optional[str] = None, 
        ime_avtorja: Optional[str] = None, 
        priimek_avtorja: Optional[str] = None
    ) -> List[Ocena]:
        """
        Vrne seznam ocen glede na naslov knjige in/ali avtorja.
        """
        return self.repo.dobi_ocene_po_naslovu_in_avtorju(naslov_knjige, ime_avtorja, priimek_avtorja)

    def knjige_z_oceno_vecjo_od(self, min_ocena: int) -> List[Knjiga]:
        """
        Vrne seznam knjig, ki imajo povprečno oceno večjo od min_ocena.
        """
        return self.repo.knjige_z_oceno_vecjo_od(min_ocena)
