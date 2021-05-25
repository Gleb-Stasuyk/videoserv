import uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Genre(models.Model):
    id = models.UUIDField(primary_key=True)
    title = models.CharField(_('название'), max_length=100)
    description = models.TextField(_('описание'), blank=True, null=True)

    class Meta:
        db_table = 'genre'
        verbose_name = _('жанр')
        verbose_name_plural = _('жанры')

    def __str__(self):
        return self.title


class FilmworkType(models.TextChoices):
    MOVIE = 'movie', _('фильм')
    TV_SHOW = 'tv_show', _('шоу')


class PersonType(models.TextChoices):
    ACTOR = 'Actor', _('актер')
    DIRECTOR = 'Director', _('режиссёр')
    WRITER = 'Writer', _('сценарист')


class Gender(models.TextChoices):
    MALE = 'male', _('мужской')
    FEMALE = 'female', _('женский')


class Person(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(_('имя'), max_length=255)
    gender = models.TextField(_('пол'), choices=Gender.choices, null=True, blank=True)

    class Meta:
        db_table = 'person'
        verbose_name = _('человек')
        verbose_name_plural = _('люди')

    def __str__(self):
        return self.name


class FilmWork(models.Model):
    id = models.UUIDField(primary_key=True)
    title = models.CharField(_('название'), max_length=255)
    plot = models.TextField(_('содержание'), blank=True, null=True)
    creation_date = models.DateField(_('дата выхода'), blank=True, null=True)
    certificate = models.TextField(_('сертификат'), blank=True, null=True)
    file_path = models.FileField(_('файл'), upload_to='film_works/', blank=True, null=True)
    imdb_rating = models.FloatField(_('рейтинг'), validators=[MinValueValidator(0)], blank=True, null=True)
    type = models.CharField(_('тип'), max_length=20, choices=FilmworkType.choices, default=FilmworkType.MOVIE)
    genres_id = models.ManyToManyField(Genre, through='FilmWorkGenre')
    persons_id = models.ManyToManyField(Person, through='FilmWorkPerson')

    class Meta:
        db_table = 'film_work'
        verbose_name = _('кинопроизведение')
        verbose_name_plural = _('кинопроизведения')

    def __str__(self):
        return self.title


class FilmWorkGenre(models.Model):
    film_work = models.OneToOneField(FilmWork, models.DO_NOTHING, primary_key=True, related_name='filmwork_genre')
    genre = models.ForeignKey('Genre', models.DO_NOTHING, related_name='genre')

    class Meta:
        db_table = 'film_work_genre'
        unique_together = (('film_work', 'genre'),)


class FilmWorkPerson(models.Model):
    id = models.UUIDField(primary_key=True)
    film_work = models.ForeignKey(FilmWork, models.DO_NOTHING, related_name='filmwork_person')
    person = models.ForeignKey('Person', models.DO_NOTHING)
    person_type = models.CharField(_('профессия'), max_length=30, choices=PersonType.choices)

    class Meta:
        db_table = 'film_work_person'
