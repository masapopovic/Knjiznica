GRANT CONNECT ON DATABASE opb2025_popovma TO javnost;

GRANT USAGE ON SCHEMA public TO javnost;

GRANT ALL ON ALL TABLES IN SCHEMA public TO javnost;


ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO javnost;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO javnost;


SELECT * FROM knjiga;
SELECT * FROM avtor;
SELECT * FROM knjiga_in_avtor;
SELECT * FROM knjiga_in_zanr;

SELECT * FROM clan;
SELECT * FROM ocena;
SELECT * FROM bralno_srecanje;

ALTER TABLE knjiga
ALTER COLUMN zanr TYPE TEXT[]
USING string_to_array(trim(both '{}' from zanr), ',');

ALTER TABLE rezervacija
ADD COLUMN status TEXT NOT NULL DEFAULT 'aktivna'
CHECK (status_rezervacije IN ('aktivna', 'izpolnjena', 'preklicana'));

DROP TABLE IF EXISTS clan, knjiga, avtor, bralno_srecanje, ocena,
                      izposoja, vracila, knjiga_in_avtor, zanr,
                      knjiga_in_zanr, udelezba CASCADE;
