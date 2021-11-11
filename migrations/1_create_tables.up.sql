create table users (
    user_id serial primary key,
    display_name varchar(18) unique not null,
    unique_key varchar(12) unique not null,
    avatar_url text
);

create table coordinates (
    coord_id serial primary key,
    ts timestamp not null,
    coord_x numeric not null,
    coord_y numeric not null,
    user_id integer,
    constraint fk_userid
        foreign key (user_id)
            references users(user_id)
            on delete cascade
);

create table friends (
    user_id integer not null,
    friend_id integer not null,
    constraint fk_userid
        foreign key (user_id)
            references users(user_id)
            on delete cascade,
    constraint fk_friendid
        foreign key (friend_id)
            references users(user_id)
            on delete cascade
);

create table pending_friends (
    receiver_id integer not null,
    sender_id integer not null,
    constraint fk_receiverid
        foreign key (receiver_id)
            references users(user_id)
            on delete cascade,
    constraint fk_receiver
        foreign key (sender_id)
            references users(user_id)
            on delete cascade
);
