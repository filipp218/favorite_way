CREATE TABLE Favorite_way(
    id serial PRIMARY KEY,
    user_id int,
    location1 geometry,
    location2 geometry,
    install_date timestamp,
    is_active bool
);

CREATE INDEX user_id_index on Favorite_way(user_id) where is_active is True;