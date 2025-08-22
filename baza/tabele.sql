CREATE TABLE clan (
    id_clana SERIAL PRIMARY KEY,
    ime TEXT NOT NULL,
    priimek TEXT NOT NULL,
    uporabnisko_ime TEXT UNIQUE NOT NULL,
    geslo TEXT NOT NULL,     
    email TEXT UNIQUE NOT NULL,
    status_clana TEXT NOT NULL CHECK (status_clana IN ('aktiven', 'neaktiven'))
);



CREATE TABLE knjiga (
    id_knjige SERIAL PRIMARY KEY,
    naslov TEXT NOT NULL,
    zanr TEXT NOT NULL,
    razpolozljivost TEXT NOT NULL CHECK (razpolozljivost IN ('na voljo', 'ni na voljo'))
);

CREATE TABLE avtor (
    id_avtorja SERIAL PRIMARY KEY,
    ime TEXT NOT NULL,
    priimek TEXT NOT NULL
);

CREATE TABLE bralno_srecanje (
    id_srecanja SERIAL PRIMARY KEY,
    prostor TEXT NOT NULL,
    datum TIMESTAMP NOT NULL,
    naziv_in_opis TEXT NOT NULL,
    id_knjige INT NOT NULL,
    FOREIGN KEY (id_knjige) REFERENCES knjiga(id_knjige)
);

CREATE TABLE ocena (
    id_ocene SERIAL PRIMARY KEY,
    ocena INT NOT NULL CHECK (ocena BETWEEN 1 AND 5),
    datum DATE DEFAULT CURRENT_DATE,
    komentar TEXT,
    id_clana INT NOT NULL,
    id_knjige INT NOT NULL,
    FOREIGN KEY (id_clana) REFERENCES clan(id_clana),
    FOREIGN KEY (id_knjige) REFERENCES knjiga(id_knjige)
);

--POVEZOVALNE TABELE

CREATE TABLE izposoja (
    id_clana INT NOT NULL,
    id_knjige INT NOT NULL,
    datum_izposoje DATE DEFAULT CURRENT_DATE,
    rok_vracila DATE GENERATED ALWAYS AS ((datum_izposoje + (INTERVAL '21 days'))::DATE) STORED,
    PRIMARY KEY (id_clana, id_knjige, datum_izposoje),
    FOREIGN KEY (id_clana) REFERENCES clan(id_clana),
    FOREIGN KEY (id_knjige) REFERENCES knjiga(id_knjige)
)

CREATE TABLE rezervacija (
    id_clana INT NOT NULL,
    id_knjige INT NOT NULL,
    datum_rezervacije DATE DEFAULT CURRENT_DATE,
    PRIMARY KEY (id_clana, id_knjige, datum_rezervacije),
    FOREIGN KEY (id_clana) REFERENCES clan(id_clana),
    FOREIGN KEY (id_knjige) REFERENCES knjiga(id_knjige)
)


CREATE TABLE knjiga_in_avtor (
    id_avtorja INT NOT NULL,
    id_knjige INT NOT NULL,
    PRIMARY KEY (id_avtorja, id_knjige),
    FOREIGN KEY (id_avtorja) REFERENCES avtor(id_avtorja),
    FOREIGN KEY (id_knjige) REFERENCES knjiga(id_knjige)
)

CREATE TABLE udelezba (
    id_srecanja INT NOT NULL,
    id_clana INT NOT NULL,
    PRIMARY KEY (id_srecanja, id_clana),
    FOREIGN KEY (id_srecanja) REFERENCES bralno_srecanje(id_srecanja),
    FOREIGN KEY (id_clana) REFERENCES clan(id_clana),
)
