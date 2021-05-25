GRANT ALL PRIVILEGES ON DATABASE movies TO postgres;

CREATE TABLE IF NOT EXISTS film_work (
id uuid PRIMARY KEY,
plot TEXT,
title VARCHAR(255) NOT NULL,
imdb_rating REAL DEFAULT 0.0);

CREATE TABLE IF NOT EXISTS genre (
id uuid PRIMARY KEY,
title VARCHAR(255) NOT NULL);

CREATE TABLE IF NOT EXISTS person (
id uuid PRIMARY KEY,
name VARCHAR(255) NOT NULL);

CREATE TYPE types AS ENUM ('Actor', 'Writer', 'Director');

CREATE TABLE IF NOT EXISTS film_work_person (
id uuid PRIMARY KEY,
film_work_id uuid NOT NULL references film_work(id),
person_id uuid NOT NULL references person(id),
person_type types);

CREATE TABLE IF NOT EXISTS film_work_genre (
film_work_id uuid NOT NULL references film_work(id),
genre_id uuid NOT NULL references genre(id),
PRIMARY KEY (film_work_id, genre_id));

