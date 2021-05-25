from django.urls import path

from .views import Movies, MoviesDetailApi

urlpatterns = [
    path('movies/', Movies.as_view()),
    path('movies/<uuid:pk>/', MoviesDetailApi.as_view())
]