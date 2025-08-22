INSERT INTO bralno_srecanje (prostor, datum, naziv_in_opis, id_knjige) VALUES
('Čitalnica', '2025-09-10 17:00:00', 'Srečanje z avtorjem knjige', 13),
('Oddelek za otroke', '2025-09-12 16:00:00', 'Otroški literarni klub', 10),
('Soba za dogodke', '2025-09-15 18:00:00', 'Pogovor o literaturi za odrasle', 3),
('Čitalnica', '2025-09-18 17:30:00', 'Srečanje z avtorjem knjige', 29),
('Oddelek za otroke', '2025-09-20 16:00:00', 'Otroški literarni klub', 79),
('Soba za dogodke', '2025-09-22 18:30:00', 'Branje poezije in interpretacija', 18),
('Čitalnica', '2025-09-25 17:00:00', 'Pogovor o literaturi za odrasle', 5),
('Oddelek za otroke', '2025-09-28 16:30:00', 'Otroški literarni klub', 16),
('Soba za dogodke', '2025-10-01 18:00:00', 'Branje poezije in interpretacija', 55),
('Čitalnica', '2025-10-05 17:00:00', 'Srečanje z avtorjem knjige', 68);


INSERT INTO clan (ime, priimek, uporabnisko_ime, geslo, email, status_clana) VALUES
('Ana', 'Novak', 'ana.novak', 'hash1', 'ana.novak@email.com', 'aktiven'),
('Marko', 'Kovač', 'marko.kovac', 'hash2', 'marko.kovac@email.com', 'aktiven'),
('Lina', 'Zupan', 'lina.zupan', 'hash3', 'lina.zupan@email.com', 'neaktiven'),
('Peter', 'Horvat', 'peter.horvat', 'hash4', 'peter.horvat@email.com', 'aktiven'),
('Maja', 'Vidmar', 'maja.vidmar', 'hash5', 'maja.vidmar@email.com', 'neaktiven');


INSERT INTO ocena (ocena, datum, komentar, id_clana, id_knjige) VALUES
(5, '2025-08-21', 'Odlična knjiga, zelo priporočam!', 1, 1),
(4, '2025-08-20', 'Zanimiva zgodba, nekaj delov bi lahko bili krajši.', 2, 5),
(3, '2025-08-19', 'Povprečna knjiga, nič posebnega.', 4, 3),
(2, '2025-08-18', 'Nisem bil navdušen, stil pisanja ni bil všeč.', 4,1),
(5, '2025-08-17', 'Neverjetna knjiga, prebrala bi še več od tega avtorja!', 3, 5);
