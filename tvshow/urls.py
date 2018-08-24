from django.conf.urls import url
from . import views

urlpatterns =[
    url(r'^$',views.index,name='index'),
    url(r'^tvshow/$',views.checknpass, name = 'addmovie'),
    url(r'^movie$',views.movie_index, name = 'addmovie')
]