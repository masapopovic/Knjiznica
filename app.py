from Presentation.bottleext import get, post, run, request, template, redirect, static_file, url, response, template_user, route
from Services.auth_service import AuthService
from Services.knjige_service import KnjigaService
from Services.ocene_service import OcenaService
from Services.srecanja_service import SrecanjaService
import os
from functools import wraps


# inicializacija servisov
auth_service = AuthService()
knjiga_service = KnjigaService()
ocena_service = OcenaService()
srecanja_service = SrecanjaService()

# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)


@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='Presentation/static')


# -------- Začetna stran --------
@get("/")
def zacetna_stran():
    user_id = request.get_cookie("id_clana", secret="skrivnost123")
    if user_id:
        redirect("/home")
    return template("zacetna_stran.html")

# -------- Prijava / registracija --------
@get("/prijava")
def prijava_form():
    return template("prijava.html", napaka=None)

@post("/prijava")
def prijava():
    uname = request.forms.get("uporabnisko_ime")
    geslo = request.forms.get("geslo")
    try:
        clan_dto = auth_service.prijava_clana(uname, geslo)
        response.set_cookie("id_clana", str(clan_dto.id_clana), secret="skrivnost123", path="/")
        redirect("/home")
    except ValueError as e:
        return template("prijava.html", napaka=str(e))

@get("/registracija")
def registracija_form():
    return template("registracija.html", napaka=None)

@post("/registracija")
def registracija():
    ime = request.forms.get("ime")
    priimek = request.forms.get("priimek")
    uname = request.forms.get("uporabnisko_ime")
    geslo = request.forms.get("geslo")
    email = request.forms.get("email")
    try:
        clan = auth_service.registracija_clana(ime, priimek, uname, geslo, email)
        response.set_cookie("id_clana", str(clan.id_clana), secret="skrivnost123", path="/")
        redirect("/home")
    except ValueError as e:
        return template("registracija.html", napaka=str(e))

# -------- Homepage --------
@get("/home")
@cookie_required
def home():
    id_clana = int(request.get_cookie("id_clana", secret="skrivnost123"))
    clan = auth_service.repo.dobi_clana_po_id(id_clana)  # ali po id_clana
    return template(
        "domaca_stran.html",
        clan=clan,
        knjige=[],               # tukaj se bo naložil rezultat iskanja prek POST
        prihodnja_srecanja=srecanja_service.prikazi_prihodnja_srecanja()
    )
# lahka pustima ta deu sam ta deu ti da rezulate teh knjig na pač isti strani pač home page-u js sm pa naredla zej nov tt post get whatewer
# ko te pa da na novo stran na kiri so sam seznami knjig če šetkaš pa se ti osloč ka je bolš
#@post("/iskanje_knjig")
#@cookie_required
#def iskanje_knjig():
#    id_clana = int(request.get_cookie("id_clana", secret="skrivnost123"))
#    naslov = request.forms.get("naslov")
#    avtor = request.forms.get("avtor")
#    zanri = request.forms.getall("zanri")  # več izbranih
#    min_ocena = request.forms.get("min_ocena")

#    rezultati = knjiga_service.iskanje_knjig(naslov, avtor, zanri, min_ocena)
#    return template("home.html", clan=auth_service.repo.dobi_clana_po_id(id_clana),
#                    knjige=rezultati, prihodnja_srecanja=srecanja_service.prikazi_prihodnja_srecanja())

@get("/rezultati")
@cookie_required
def rezultati():
    id_clana = int(request.get_cookie("id_clana", secret="skrivnost123"))
    naslov = request.query.get("naslov")
    avtor = request.query.get("avtor")
    min_ocena = request.query.get("min_ocena")

    knjige = knjiga_service.iskanje_knjig(naslov, avtor, [], min_ocena)

    return template("rezultati.html", clan=auth_service.repo.dobi_clana_po_id(id_clana), knjige=knjige)


# -------- Stran posamezne knjige --------
@get("/knjiga/<id_knjige:int>")
@cookie_required
def prikazi_knjigo(id_knjige):
    # ID prijavljenega člana iz piškotka
    id_clana = int(request.get_cookie("id_clana", secret="skrivnost123"))

    # Pridobi podatke o izbranem izvodu
    knjiga = knjiga_service.dobi_knjigo_po_id(id_knjige)
    if not knjiga:
        return "Knjiga s tem ID ne obstaja."

    # Pridobi vse avtorje knjige
    avtorji = knjiga_service.dobi_avtorje_knjige(id_knjige)

    # Dodajanje ocene bo vplivalo na vse izvode, zato pridobi vse ocene za vse izvode
    ocene = ocena_service.ocene_po_naslovu_in_avtorju(
        knjiga.naslov,
        avtorji[0]['ime'] if avtorji else '',
        avtorji[0]['priimek'] if avtorji else ''
    )

    # Template odloči, ali pokaže gumb za izposojo
    return template(
        "knjiga.html",
        clan_id=id_clana,
        knjiga=knjiga,
        avtorji=avtorji,
        ocene=ocene
    )


@post("/dodaj_oceno/<id_knjige:int>")
@cookie_required
def dodaj_oceno(id_knjige):
    id_clana = int(request.get_cookie("id_clana", secret="skrivnost123"))
    ocena = int(request.forms.get("ocena"))
    komentar = request.forms.get("komentar")
    ocena_service.dodaj_oceno(id_clana, id_knjige, ocena, komentar)
    redirect(f"/knjiga/{id_knjige}")

@post("/izposodi/<id_knjige:int>")
@cookie_required
def izposodi_knjigo(id_knjige):
    id_clana = int(request.get_cookie("id_clana", secret="skrivnost123"))
    knjiga_service.izposodi_knjigo(id_clana, id_knjige)
    redirect("/home")

# -------- Bralna srečanja --------
@get("/srecanja")
@cookie_required
def srecanja():
    # Preberi GET parametre
    naziv = request.query.naziv or None
    datum = request.query.datum or None

    # Pokliči service funkcijo, ki vrne filtrirana srečanja
    prihodnja = srecanja_service.isci_prihodnja_srecanja(naziv=naziv, datum=datum)

    return template("bralna_srecanja.html", srecanja=prihodnja, napaka=None)

@get("/srecanja_autocomplete")
def srecanja_autocomplete():
    query = request.query.q  # niz, ki ga tipka uporabnik
    if not query:
        return {"results": []}

    # Pokliči repo/service, da vrne samo nazive
    matches = srecanja_service.najdi_nazive(query)
    return {"results": matches}  # vrnemo JSON

@post("/prijava_srecanja")
@cookie_required
def prijava_srecanja():
    id_clana = int(request.get_cookie("id_clana", secret="skrivnost123"))
    id_srecanja = int(request.forms.get("id_srecanja"))

    try:
        srecanja_service.prijavi_clana_na_srecanje(id_clana, id_srecanja)
        redirect("/srecanja")  # ostanemo na seznamu srečanj
    except ValueError as e:
        prihodnja = srecanja_service.prikazi_prihodnja_srecanja()
        return template("bralna_srecanja.html", srecanja=prihodnja, napaka=str(e))


@get("/profil")
@cookie_required
def profil():
    id_clana = int(request.get_cookie("id_clana", secret="skrivnost123"))

    # Trenutno prijavljen član
    clan = auth_service.repo.dobi_clana_po_id(id_clana)

    # Trenutno izposojene knjige
    izposojene_knjige = knjiga_service.dobi_izposojene_knjige(id_clana)

    # Prihodnja bralna srečanja, kjer je član prijavljen
    prijavljena_srecanja = srecanja_service.prihodnja_srecanja_po_clanu(id_clana)

    return template(
        "profil.html",
        clan=clan,
        izposojene_knjige=izposojene_knjige,
        prijavljena_srecanja=prijavljena_srecanja
    )


