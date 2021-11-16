insert into users (display_name, unique_key, avatar_url)
values
('fully-full-swan', 'nfMCGgt3W6Tk', 'http://192.168.0.105:8000/img/761fd95455782bb0f1127495927f441cef4fa13a4805a1b6697c52e6cde31da5.png'),
('oddly-legal-jay','yPM8jpq93u-8', 'http://192.168.0.105:8000/img/55c7e49a6b915acf31f6a7d3d78599328934c1568d5d9e4d43e85e2b5cd09cca.png'),
('fully-apt-corgi', 'tZjsrUe5JMFY', 'http://192.168.0.105:8000/img/a91598b8b7b541bb29f43d812fc99c66c8aadbd5de097d3ff3cf23d85fbb3c0f.png'),
('truly-safe-swine', 'A4HRfvrKwMxi', 'http://192.168.0.105:8000/img/2dd2349e2e8402d9053218db697f03b38ca79f95b21c5adb06ca671cf90f3a55.png'),
('sadly-huge-joey', 'GSKg9v2kCaTc', 'http://192.168.0.105:8000/img/cc5caecb0d6230bd7462094c2968753833aae99c14b48888ada0f73a706af891.png');

-- When you add friend, you add 2 entries to the db
insert into friends (user_id, friend_id)
values
(1, 2),
(2, 1),
(3, 4),
(4, 3),
(3, 1),
(1, 3);

-- Not the case this time
insert into pending_friends (receiver_id, sender_id, sent_at)
values
(1, 5, '2021-11-11 15:00:00.685'),
(1, 4, '2021-11-11 15:00:00.685'),
(2, 5, '2021-11-12 20:00:12.152');

insert into coordinates (user_id, ts, latitude, longitude)
values
(1, '2021-11-11 14:00:00.685', 39.0685555, -42.5589567),
(1, '2021-11-11 14:00:03.645', 56.0613555, -40.5589567),
(1, '2021-11-11 14:00:06.285', 13.0645555, -39.5589567),
(1, '2021-11-11 14:00:09.686', 42.0685555, -38.5589567),
(1, '2021-11-11 14:00:12.152', 23.0685555, -37.5589567),
(2, '2021-11-12 15:00:00.685', 12.0685555, 13.5589567),
(2, '2021-11-12 16:00:03.645', 24.0613555, 34.5589567),
(2, '2021-11-12 17:00:06.285', 40.0645555, -39.5589567),
(2, '2021-11-12 18:00:09.686', 31.0685555, 2.5589567),
(2, '2021-11-12 19:00:12.152', 12.0685555, 4.5589567);