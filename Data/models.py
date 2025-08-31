from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from datetime import datetime
from datetime import date
from typing import Optional

#razredi:

@dataclass_json
@dataclass
class Clan:
    id_clana: int = field(default=0)
    ime: str = field(default="")
    priimek: str = field(default="")
    uporabnisko_ime: str = field(default="")
    password_hash: str = field(default="")  
    email: str = field(default="")
    status_clana: str = field(default="aktiven")


@dataclass_json
@dataclass
class ClanDto:
    id_clana: int = field(default=0)
    ime: str = field(default="")
    priimek: str = field(default="")
    uporabnisko_ime: str = field(default="")
    status_clana: str = field(default="aktiven")


@dataclass_json
@dataclass
class Knjiga:
    id_knjige: int = field(default=0)
    naslov: str = field(default="")
    razpolozljivost: str = field(default="na voljo")

@dataclass_json
@dataclass
class Zanr:
    id_zanra: int = field(default=0)
    ime_zanra: str = field(default="")

@dataclass_json
@dataclass
class Avtor:
    id_avtorja: int = field(default=0)
    ime: str = field(default="")
    priimek: str = field(default="")


@dataclass_json
@dataclass
class BralnoSrecanje:
    id_srecanja: int = field(default=0)
    prostor: str = field(default="")
    datum: str = field(default="")  
    naziv_in_opis: str = field(default="")
    id_knjige: int = field(default=0)


@dataclass_json
@dataclass
class Ocena:
    id_ocene: int = field(default=0)
    ocena: int = field(default=0)
    datum: str = field(default="")  
    komentar: Optional[str] = None
    id_clana: int = field(default=0)
    id_knjige: int = field(default=0)



@dataclass_json
@dataclass
class Izposoja:
    id_clana: int = field(default=0)
    id_knjige: int = field(default=0)
    datum_izposoje: str = field(default="")  
    rok_vracila: Optional[str] = None  
    status_izposoje:  str = field(default="izposojeno")



@dataclass_json
@dataclass
class KnjigaInAvtor:
    id_avtorja: int = field(default=0)
    id_knjige: int = field(default=0)


@dataclass_json
@dataclass
class Udelezba:
    id_srecanja: int = field(default=0)
    id_clana: int = field(default=0)

@dataclass_json
@dataclass
class KnjigaInZanr:
    id_knjige: int = field(default=0)
    id_zanra: int = field(default=0)