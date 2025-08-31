from Data.repository import Repo
from Data.models import Ocena, Knjiga
from datetime import datetime
from typing import List, Optional


class OcenaService:
    def __init__(self):
        #uporabi javnega uporabnika za vse operacije
        self.repo = Repo(admin=False)


    def povprecna_ocena_knjige(self, id_knjige: int) -> Optional[float]:
        """
        Vrne povprečno oceno za izbrano knjigo.
        """
        return self.repo.povprecna_ocena_knjige(id_knjige)
    

    def ocene_po_id_knjige(self, id_knjige: int) -> list[Ocena]:
        """
        Vrne seznam vseh ocen za določeno knjigo (po ID),
        z najnovejšimi ocenami na vrhu.
        """
        return self.repo.ocene_po_id_knjige(id_knjige)

    

    def dodaj_oceno(self, id_clana: int, id_knjige: int, ocena: int, komentar: str = ""):
        """
        Doda oceno knjige za člana.
        """
        if not (1 <= ocena <= 5):
            raise ValueError("Ocena mora biti med 1 in 5.")

        # Dobi podatke knjige po ID
        knjiga = self.repo.dobi_knjigo_po_id(id_knjige)

        # Dobi avtorje te knjige
        avtorji = self.repo.dobi_avtorje_knjige(id_knjige)

        # Oblikuj niz za iskanje: vsi avtorji ločeni z vejico
        avtorji_iskani = ", ".join([f"{a.ime} {a.priimek}" for a in avtorji])

        # Poišči vse izvode iste knjige (isti naslov in isti avtorji)
        vse_izvode = self.repo.poisci_knjige(naslov=knjiga.naslov, avtorji=avtorji_iskani)

        for k in vse_izvode:
            nova_ocena = Ocena(
                ocena=ocena,
                datum=None,  # repo nastavi trenutni datum
                komentar=komentar,
                id_clana=id_clana,
                id_knjige=k.id_knjige
            )
            self.repo.dodaj_oceno(nova_ocena)
    
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



