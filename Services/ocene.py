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

    
    def dodaj_oceno_za_prijavljenega(self, uporabnisko_ime: str, id_knjige: int, ocena: int, komentar: str = ""):
            """
            Doda oceno knjige za člana, ki je prijavljen z uporabniškim imenom.
            """
            # Preveri, ali je ocena veljavna
            if not (1 <= ocena <= 5):
                raise ValueError("Ocena mora biti med 1 in 5.")

            # Dobi id_clana preko uporabniškega imena
            clan = self.repo.dobi_clana_po_uporabniskem_imenu(uporabnisko_ime)
            if not clan:
                raise ValueError("Član ne obstaja.")

            # Ustvari objekt Ocena
            nova_ocena = Ocena(
                ocena=ocena,
                datum=None,  # repo lahko nastavi trenutni datum
                komentar=komentar,
                id_clana=clan.id_clana,
                id_knjige=id_knjige
            )

            # Pošlji v repo
            self.repo.dodaj_oceno(nova_ocena)

            