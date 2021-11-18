insert into users (display_name, unique_key, avatar_url)
values
('fully-full-swan', 'nfMCGgt3W6Tk', 'img/1dd6f32e-4db2-49b6-a7ab-78483241f353.png'),
('oddly-legal-jay','yPM8jpq93u-8', 'img/a0749e50-46fa-4421-a64a-1ac9facd98f3.png'),
('fully-apt-corgi', 'tZjsrUe5JMFY', 'img/3f9c2c42-2a18-418a-9db4-e3edb4e54f11.png'),
('truly-safe-swine', 'A4HRfvrKwMxi', 'img/4bc280d5-569d-4769-9d2b-3036891aa0c8.png'),
('sadly-huge-joey', 'GSKg9v2kCaTc', 'img/73a07378-cd71-4541-abdb-49fa0daf39c3.png');

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