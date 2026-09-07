from django.urls import path

from . import views

urlpatterns = [
    path('', views.ranked_list, name='ranked_list'),
    path('games/', views.game_list, name='game_list'),
    path('compare/', views.compare, name='compare'),
    path('compare/pick/', views.compare_pick, name='compare_pick'),
]
