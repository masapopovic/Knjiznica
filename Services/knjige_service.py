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

    
    def dobi_zanre_knjige(self, id_knjige: int) -> list[str]:
        return self.repo.dobi_zanre_knjige(id_knjige)

    def iskanje_knjig(
        self,
        naslov: str = None,
        avtorji: list[str] = None,
        zanri: list[str] = None,
        min_ocena: int = None
    ) -> list[Knjiga]:
        """
        Vrne seznam knjig, vsak objekt vsebuje seznam avtorjev in žanrov.
        """
        knjige = self.repo.poisci_knjige(
            naslov=naslov,
            avtorji=avtorji,
            zanri=zanri,
            min_ocena=min_ocena
        )

        for k in knjige:
            k.avtorji = self.repo.dobi_avtorje_knjige(k.id_knjige)  
            k.zanri = self.repo.dobi_zanre_knjige(k.id_knjige)      

        return knjige


    def dobi_izposojene_knjige(self, id_clana: int):
        return self.repo.dobi_izposojene_knjige(id_clana)
    

    
    def izposodi_knjigo(self, id_clana: int, id_knjige: int):
        #status člana
        clan = self.repo.dobi_clana_po_id(id_clana)
        if not clan:
            raise ValueError("Član s tem ID ne obstaja.")
        
        if clan.status_clana != "aktiven":
            raise ValueError("Izposoja ni mogoča, ker član ni aktiven.")
        
        #preveri, če je knjiga na voljo
        knjiga = self.repo.dobi_knjigo_po_id(id_knjige)
        if not knjiga or knjiga.razpolozljivost != "na voljo":
            raise ValueError("Knjiga trenutno ni na voljo za izposojo.")
        
        #dodaj izposojo
        self.repo.dodaj_izposojo(id_clana, id_knjige)
        self.repo.posodobi_razpolozljivost(id_knjige, 'ni na voljo')


    def vrni_knjigo_po_id(self, id_clana: int, id_knjige: int):
        #ali knjiga obstaja
        knjiga = self.repo.dobi_knjigo_po_id(id_knjige)
        if not knjiga:
            raise ValueError("Knjiga s tem ID ne obstaja.")

        self.repo.dodaj_vracilo(id_clana, id_knjige)

        try:
            self.repo.posodobi_razpolozljivost(id_knjige, 'na voljo')
            self.repo.conn.commit()
        except Exception as e:
            self.repo.conn.rollback()
            raise e


    def dobi_avtorje_knjige(self, id_knjige: int):
        return self.repo.dobi_avtorje_knjige(id_knjige)
    
