from itertools import chain
import json
import sqlite3
import uuid
from dataclasses import dataclass, field
from typing import List

import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor, execute_batch

load_dotenv()


@dataclass
class FilmWorkPerson:
    film_work_id: uuid.UUID
    person_id: uuid.UUID
    person_type: str


@dataclass
class FilmWorkGenre:
    film_work_id: uuid.UUID
    genre_id: uuid.UUID


@dataclass
class Movie:
    title: str
    plot: str
    genre: List[str]
    writers: List[str]
    actors: List[str]
    directors: List[str]
    imdb_rating: float = field(default=0.0)
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class SQLiteLoader:
    conn: sqlite3.Connection

    def get_movies_data(self):
        return pd.read_sql("""SELECT m.*, w.name AS writer_name FROM movies m 
                            LEFT JOIN writers w ON m.writer=w.id""", self.conn)

    def get_actors_data(self):
        actors = pd.read_sql("""SELECT m.id, m.genre, m.director, m.writers, m.title, m.plot, 
        m.ratings, m.imdb_rating, a.name actor_name
        FROM movies AS m
        LEFT JOIN movie_actors as ma ON ma.movie_id=m.id
        LEFT JOIN actors as a ON ma.actor_id=a.id""", self.conn)

        actors['actor_name'].replace('N/A', '', inplace=True)
        actors['actors_names'] = actors['actor_name'].apply(lambda x: [x])
        actors_df = actors.groupby('id').sum().reset_index()[['id', 'actors_names']]

        return actors_df

    def transform_movies_data(self):
        df = self.get_movies_data()
        df['writers_list'] = df[df['writers'] != '']['writers'].apply(lambda x: json.loads(x)).apply(
            lambda x: [l['id'] for l in x])
        writers_series = df.dropna(subset=['writers_list'])['writers_list'].apply(lambda x: self.replace_writers(x))
        df['writers_list'] = writers_series
        df['writer_name'] = df['writer_name'].apply(lambda x: [x])
        df['genre'] = df['genre'].apply(lambda x: x.split(', '))
        df['directors'] = df['director'].apply(lambda x: x.split(', '))
        df['imdb_rating'] = df['imdb_rating'].replace('N/A', 0.0)
        df.writers_list.fillna(df.writer_name, inplace=True)
        df = df.drop(['writers', 'writer', 'writer_name'], axis=1)
        # merge agtors to movie df
        actors_df = self.get_actors_data()
        df = df.merge(actors_df, on=['id'])

        return df

    def get_writers_dict(self):
        writers = pd.read_sql('''SELECT * FROM writers''', self.conn)
        writers_dict = pd.Series(writers.name.values, index=writers.id).to_dict()

        return writers_dict

    def replace_writers(self, row):
        writers_dict = self.get_writers_dict()

        return [writers_dict.get(x) for x in row]

    def load_movies(self):
        df = self.transform_movies_data()
        # replace N/A values to 'No Information'
        df['writers_list'] = df.apply(lambda x: [i.replace('N/A', 'No Information') for i in x['writers_list']], axis=1)
        data = []
        for index, row in df.iterrows():
            movie = Movie(title=row['title'], genre=row['genre'], plot=row['plot'], actors=row['actors_names'],
                          writers=row['writers_list'], imdb_rating=row['imdb_rating'], directors=row['directors'])
            data.append(movie)

        return data


class PostgresSaver:
    def __init__(self, pg_conn):
        self.conn = pg_conn
        self.cur = pg_conn.cursor()

    def save_film_work_person(self, data):
        film_work_person = []
        df = pd.read_sql_query('SELECT * FROM person;', self.conn)
        persons_dict = pd.Series(df.id.values, index=df.name).to_dict()
        for movie in data:
            tables = [(movie.actors, 'Actor'), (movie.writers, 'Writer'), (movie.directors, 'Director')]
            for person_type, type_name in tables:
                for person in person_type:
                    film_work_person.append(FilmWorkPerson(film_work_id=movie.id,
                                                           person_id=persons_dict.get(person),
                                                           person_type=type_name))

        print("insert film_work_person")
        execute_batch(
            self.cur,
            "INSERT INTO film_work_person (id, film_work_id, person_id, person_type) VALUES (%s, %s, %s, %s)",
            [
                (str(uuid.uuid4()), str(row.film_work_id), str(row.person_id), str(row.person_type))
                for row in film_work_person
            ],
            page_size=500,
        )
        self.conn.commit()

    def save_film_work_genre(self, data):
        film_work_genre = []
        df = pd.read_sql_query('SELECT * FROM genre;', self.conn)
        genres_dict = pd.Series(df.id.values, index=df.title).to_dict()
        for movie in data:
            [
                film_work_genre.append(
                    FilmWorkGenre(film_work_id=movie.id, genre_id=genres_dict.get(genre))) for genre in movie.genre
            ]

        print("insert film_work_genre")
        execute_batch(
            self.cur,
            "INSERT INTO film_work_genre (film_work_id, genre_id) VALUES (%s, %s)",
            [
                (str(row.film_work_id), str(row.genre_id))
                for row in film_work_genre
            ],
            page_size=500,
        )
        self.conn.commit()

    def save_persons(self, data):
        persons = set()
        [[persons.add(person) for person in list(chain(m.directors, m.writers, m.actors))] for m in data]

        print("insert persons")
        execute_batch(
            self.cur,
            "INSERT INTO person (id, name) VALUES (%s, %s)",
            [
                (str(uuid.uuid4()), person)
                for person in persons
            ],
            page_size=500,
        )
        self.conn.commit()

    def save_movies(self, data):
        print("insert movies")
        execute_batch(
            self.cur,
            "INSERT INTO film_work (id, plot, title, imdb_rating ) VALUES (%s, %s, %s, %s)",
            [
                (str(movie.id), movie.plot, movie.title, movie.imdb_rating)
                for movie in data
            ],
            page_size=500,
        )
        self.conn.commit()

    def save_genres(self, data):
        genres = set()
        [[genres.add(genre) for genre in m.genre] for m in data]

        print("insert genres")
        execute_batch(
            self.cur,
            "INSERT INTO genre (id, title) VALUES (%s, %s)",
            [
                (str(uuid.uuid4()), genre,)
                for genre in genres
            ],
            page_size=500,
        )
        self.conn.commit()

    def save_all_data(self, data):
        self.save_genres(data)
        self.save_movies(data)
        self.save_persons(data)
        self.save_film_work_genre(data)
        self.save_film_work_person(data)


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""
    postgres_saver = PostgresSaver(pg_conn)
    sqlite_loader = SQLiteLoader(connection)

    data = sqlite_loader.load_movies()
    postgres_saver.save_all_data(data)


if __name__ == '__main__':
    dsl = {'dbname': os.getenv('DBNAME'), 'user': os.getenv('USER'), 'password': os.getenv('PASS'),
           'host': os.getenv('HOST'), 'port': os.getenv('PORT')}
    with sqlite3.connect('/code/backend/db.sqlite') as sqlite_conn, \
            psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
            load_from_sqlite(sqlite_conn, pg_conn)
