from Presentation.bottleext import get, post, request, template, redirect, static_file,  response, run
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


def cookie_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user_id = request.get_cookie("id_clana", secret="skrivnost123")
        if not user_id:
            redirect("/prijava")  # če ni piškotka → na prijavno stran
        return f(*args, **kwargs)
    return wrapper

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

# -------- Homepage oz. iskalnik --------
@get("/home")
@cookie_required
def home():
    id_clana = int(request.get_cookie("id_clana", secret="skrivnost123"))
    clan = auth_service.repo.dobi_clana_po_id(id_clana)  
    return template(
        "domaca_stran.html",
        clan=clan
    )

# -------- rezultati iskanja --------
@get("/rezultati")
@cookie_required
def rezultati():
    id_clana = int(request.get_cookie("id_clana", secret="skrivnost123"))

    naslov = request.query.get("naslov") or None
    avtorji = request.query.get("avtorji")
    if avtorji:
        avtorji = [a.strip() for a in avtorji.split(",")]
    else:
        avtorji = None

    zanri = request.query.get("zanri")
    if zanri:
        zanri = [z.strip() for z in zanri.split(",")]
    else:
        zanri = None

    min_ocena = request.query.get("min_ocena")
    min_ocena = int(min_ocena) if min_ocena else None

    knjige = knjiga_service.iskanje_knjig(naslov, avtorji, zanri, min_ocena)

    return template(
        "rezultati.html",
        clan=auth_service.repo.dobi_clana_po_id(id_clana),
        knjige=knjige
    )


# -------- Stran posamezne knjige --------

@get("/knjiga/<id_knjige:int>")
@cookie_required
def prikazi_knjigo(id_knjige):

    id_clana = int(request.get_cookie("id_clana", secret="skrivnost123"))

    knjiga = knjiga_service.dobi_knjigo_po_id(id_knjige)
    if not knjiga:
        return "Knjiga s tem ID ne obstaja."

   
    knjiga.avtorji = knjiga_service.dobi_avtorje_knjige(id_knjige)  
    knjiga.zanri = knjiga_service.dobi_zanre_knjige(id_knjige)     

   
    ocene = ocena_service.ocene_po_id_knjige(id_knjige) 
    povprecna_ocena = ocena_service.povprecna_ocena_knjige(id_knjige)

    return template(
        "knjiga.html",
        clan_id=id_clana,
        knjiga=knjiga,
        ocene=ocene,
        povprecna_ocena=povprecna_ocena,
        request=request 
    )


@post("/dodaj_oceno/<id_knjige:int>")
@cookie_required
def dodaj_oceno_route(id_knjige):
    
    id_clana = int(request.get_cookie("id_clana", secret="skrivnost123"))

    
    ocena = request.forms.get("ocena")
    komentar = request.forms.get("komentar", "")

    try:
        ocena = int(ocena)
        if not (1 <= ocena <= 5):
            raise ValueError("Ocena mora biti med 1 in 5.")
    except (ValueError, TypeError):
        return "Neveljavna ocena. Vnesite število med 1 in 5."

    
    try:
        ocena_service.dodaj_oceno_vsem_izvodom(id_clana, id_knjige, ocena, komentar)
    except Exception as e:
        return f"Prišlo je do napake: {str(e)}"

    #Po uspešnem dodajanju ocene preusmeri nazaj na stran knjige
    redirect(f"/knjiga/{id_knjige}?uspesno=1")



@post("/izposodi/<id_knjige:int>")
@cookie_required
def izposodi_route(id_knjige):
    id_clana = int(request.get_cookie("id_clana", secret="skrivnost123"))
    try:
        knjiga_service.izposodi_knjigo(id_clana, id_knjige)
        return template("sporocilo.html", sporocilo="Izposoja uspešna!", id_knjige=id_knjige)
    except ValueError as e:
        return template("sporocilo.html", sporocilo=str(e))



# -------- Bralna srečanja --------
@get("/srecanja")
@cookie_required
def srecanja():
    
    id_clana = int(request.get_cookie("id_clana", secret="skrivnost123"))

    
    naziv = request.query.naziv or None
    datum = request.query.datum or None

    prihodnja = srecanja_service.isci_prihodnja_srecanja(naziv=naziv, datum=datum)

    for s in prihodnja:
        knjiga = knjiga_service.dobi_knjigo_po_id(s.id_knjige)
        s.naslov_knjige = knjiga.naslov if knjiga else "Neznano"
        s.stevilo_prijavljenih = srecanja_service.stevilo_prijavljenih(s.id_srecanja)
        s.je_prijavljen = srecanja_service.je_clan_prijavljen(id_clana, s.id_srecanja)

    return template(
        "bralna_srecanja.html",
        srecanja=prihodnja,
        napaka=None,
        naziv=naziv,
        datum=datum
    )


@post("/prijava_srecanja")
@cookie_required
def prijava_srecanja():
    id_clana = int(request.get_cookie("id_clana", secret="skrivnost123"))
    id_srecanja = int(request.forms.get("id_srecanja"))

    try:
        srecanja_service.prijava_na_srecanje(id_clana, id_srecanja)
        redirect("/srecanja")  # ostanemo na seznamu srečanj
    except ValueError as e:
        prihodnja = srecanja_service.prikazi_prihodnja_srecanja()
        return template("bralna_srecanja.html", srecanja=prihodnja, napaka=str(e))


@get("/profil")
@cookie_required
def profil():
    id_clana = int(request.get_cookie("id_clana", secret="skrivnost123"))

    clan = auth_service.repo.dobi_clana_po_id(id_clana)

    izposojene_knjige = knjiga_service.dobi_izposojene_knjige(id_clana)

    prijavljena_srecanja = srecanja_service.prihodnja_srecanja_po_clanu(id_clana)

    for s in prijavljena_srecanja:
        knjiga = knjiga_service.dobi_knjigo_po_id(s.id_knjige)
        s.naslov_knjige = knjiga.naslov if knjiga else "Neznano"

    return template(
        "profil.html",
        clan=clan,
        izposojene_knjige=izposojene_knjige,
        prijavljena_srecanja=prijavljena_srecanja
    )

@post("/vrni/<id_knjige:int>")
@cookie_required
def vrni_knjigo(id_knjige):
    id_clana = int(request.get_cookie("id_clana", secret="skrivnost123"))

    try:
        knjiga_service.vrni_knjigo_po_id(id_clana, id_knjige)
    except ValueError as e:
        return f"Napaka: {str(e)}"
    except Exception as e:
        return f"Prišlo je do napake: {str(e)}"

    redirect("/profil")



@post("/odjava")
def odjava():
    response.delete_cookie("id_clana", secret="skrivnost123")
    redirect("/prijava")  # po odjavi ga vrže na prijavno stran


if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER, debug=True)