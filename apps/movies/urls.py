from django.urls import path
from apps.movies.views import *

app_name = 'movies'

urlpatterns = [
    path('user/<int:user>/', IndexView.as_view(), name='index'),
    path('user/<int:user>/calificar/', calificar, name='calificar'),
    path('user/<int:user>/movie/<int:movie>/', IndexView.as_view(), name='predecir'),

    path('user/<int:user>/recomendar/coseno', CosenoRecomendarView.as_view(), name='recomendar_coseno'),
    path('user/<int:user>/recomendar/cosenoajustado', CosenoAjustadoRecomendarView.as_view(), name='recomendar_coseno_ajustado'),
    path('user/<int:user>/recomendar/correlacionpearson', CorrelacionPearsonRecomendarView.as_view(), name='recomendar_correlacion_pearson'),
    path('user/<int:user>/recomendar/slopeone', SlopeOneRecomendarView.as_view(), name='recomendar_slope_one'),
    path('user/<int:user>/recomendar/slopeonepesos', SlopeOnePesosRecomendarView.as_view(), name='recomendar_slope_one_pesos'),

]