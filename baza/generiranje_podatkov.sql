INSERT INTO bralno_srecanje (prostor, datum, naziv_in_opis, id_knjige) VALUES
('Čitalnica', '2025-09-10 17:00:00', 'Srečanje z avtorjem romana Izkrivljene igre', 1),
('Oddelek za otroke', '2025-09-12 16:00:00', 'Branje in delavnica za otroke', 2),
('Soba za dogodke', '2025-09-15 18:00:00', 'Pogovor o literaturi za odrasle', 3),
('Čitalnica', '2025-09-18 17:30:00', 'Literarni večer: poezija in proza', 4),
('Oddelek za otroke', '2025-09-20 16:00:00', 'Branje pravljic in ustvarjalna delavnica', 5),
('Soba za dogodke', '2025-09-22 18:30:00', 'Srečanje za ljubitelje kriminalk', 6),
('Čitalnica', '2025-09-25 17:00:00', 'Diskusija o romanih 21. stoletja', 7),
('Oddelek za otroke', '2025-09-28 16:30:00', 'Otroški literarni klub', 8),
('Soba za dogodke', '2025-10-01 18:00:00', 'Branje poezije in interpretacija', 9),
('Čitalnica', '2025-10-05 17:00:00', 'Srečanje z mladinsko literaturo', 10);


INSERT INTO clan (ime, priimek, uporabnisko_ime, geslo, email, status_clana) VALUES
('Ana', 'Novak', 'ana.novak', 'hash1', 'ana.novak@email.com', 'aktiven'),
('Marko', 'Kovač', 'marko.kovac', 'tajno456', 'marko.kovac@email.com', 'aktiven'),
('Lina', 'Zupan', 'lina.zupan', 'mojegeslo789', 'lina.zupan@email.com', 'neaktiven'),
('Peter', 'Horvat', 'peter.horvat', '123geslo', 'peter.horvat@email.com', 'aktiven'),
('Maja', 'Vidmar', 'maja.vidmar', 'geslo321', 'maja.vidmar@email.com', 'neaktiven');


INSERT INTO ocena (ocena, datum, komentar, id_clana, id_knjige) VALUES
(5, '2025-08-21', 'Odlična knjiga, zelo priporočam!', 1, 1),
(4, '2025-08-20', 'Zanimiva zgodba, nekaj delov bi lahko bili krajši.', 2, 5),
(3, '2025-08-19', 'Povprečna knjiga, nič posebnega.', 4, 3),
(2, '2025-08-18', 'Nisem bil navdušen, stil pisanja ni bil všeč.', 4,1),
(5, '2025-08-17', 'Neverjetna knjiga, prebrala bi še več od tega avtorja!', 3, 5);
