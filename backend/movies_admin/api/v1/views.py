from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models.functions import Cast
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from movies.models import FilmWork, Genre, PersonType
from django.db.models import Q, FloatField, CharField


class MoviesApiMixin:
    model = FilmWork
    http_method_names = ['get']

    def get_queryset(self):
        return (FilmWork.objects.prefetch_related('persons_id', 'genres_id')
            .annotate(
            actors=ArrayAgg('persons_id__name', filter=Q(persons_id__filmworkperson__person_type=PersonType.ACTOR),
                            distinct=True),
            directors=ArrayAgg('persons_id__name',
                               filter=Q(persons_id__filmworkperson__person_type=PersonType.DIRECTOR),
                               distinct=True),
            writers=ArrayAgg('persons_id__name', filter=Q(persons_id__filmworkperson__person_type=PersonType.WRITER),
                             distinct=True),
            genres=ArrayAgg('genres_id__title', distinct=True),
            description=Cast('plot', CharField()),
            rating=Cast('imdb_rating', FloatField())))

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class Movies(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        paginator, page, queryset, is_paginated = self.paginate_queryset(self.get_queryset(), self.paginate_by)
        films = list(queryset.values('id', 'title', 'description', 'creation_date', 'rating',
                                     'type', 'genres', 'actors', 'directors', 'writers'))
        next_page = page.next_page_number() if page.has_next() else None
        prev_page = page.previous_page_number() if page.has_previous() else None
        context = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': prev_page,
            'next': next_page,
            'result': films,
        }

        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):

    def get(self, request, *args, **kwargs):
        self.object = self.get_queryset().filter(id=kwargs['pk'])
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, *, object_list=None, **kwargs):
        film = list(self.object.values())
        return film[0] if self.object else {}

