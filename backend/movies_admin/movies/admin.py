from django.contrib import admin

from .models import Genre, FilmWork, Person, FilmWorkPerson, FilmWorkGenre


class PersonRoleInline(admin.TabularInline):
    model = FilmWorkPerson
    extra = 0
    exclude = ['id']


class GenreInline(admin.TabularInline):
    model = FilmWorkGenre
    extra = 0
    exclude = ['id']


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    list_display = ('title', 'creation_date', 'imdb_rating', 'certificate', 'type')
    search_fields = ('title', 'plot',)
    list_filter = ('type',)
    exclude = ['id']

    inlines = [
        PersonRoleInline,
        GenreInline,
    ]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    exclude = ['id']


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    exclude = ['id']
    inlines = [
        PersonRoleInline
    ]
