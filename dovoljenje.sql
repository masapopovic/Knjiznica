GRANT CONNECT ON DATABASE opb2025_popovma TO javnost;

GRANT USAGE ON SCHEMA public TO javnost;

GRANT ALL ON ALL TABLES IN SCHEMA public TO javnost;


ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO javnost;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO javnost;


SELECT * FROM knjiga;
SELECT * FROM avtor;
SELECT * FROM zanr;
SELECT * FROM vracila;
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

ALTER TABLE clan
ADD COLUMN role TEXT NOT NULL DEFAULT 'clan'
CHECK (role IN ('clan', 'admin'));

ALTER TABLE clan
DROP COLUMN role;

ALTER TABLE izposoja
ADD COLUMN status_izposoje TEXT NOT NULL DEFAULT 'izposojeno'
CHECK (status_izposoje IN ('izposojeno', 'vrnjeno'));

DROP TABLE vracila CASCADE;

ALTER TABLE izposoja
ADD COLUMN status_izposoje TEXT DEFAULT 'izposojeno';

ALTER TABLE izposoja
ADD CONSTRAINT status_izposoje_check
CHECK (status_izposoje IN ('izposojeno', 'vrnjeno'));


SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'opb2025_popovma' AND pid <> pg_backend_pid();

SELECT * FROM izposoja;
SELECT * FROM vracila;

DROP TABLE vracila CASCADE;

SELECT pid, usename, query, state
FROM pg_stat_activity
WHERE datname = 'opb2025_popovma';


