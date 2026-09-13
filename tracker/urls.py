from django.urls import path

from . import views

urlpatterns = [
    path('', views.ranked_list, name='ranked_list'),
    path('games/', views.game_list, name='game_list'),
    path('games/add/', views.add_game, name='add_game'),
    path('games/import/', views.import_cfb_search, name='import_cfb_search'),
    path('games/import/select/', views.import_cfb_select, name='import_cfb_select'),
    path('games/<int:game_id>/', views.game_detail, name='game_detail'),
    path('compare/', views.compare, name='compare'),
    path('compare/pick/', views.compare_pick, name='compare_pick'),
]
