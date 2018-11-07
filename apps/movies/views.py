from django.shortcuts import  redirect
from django.urls import reverse
from django.views.generic import TemplateView
from apps.movies.models import *
from apps.movies.functions import get_data, get_no_calificadas
from apps.movies.datamining import *
import time


def get_context(self, context):
    user = str(self.kwargs.get('user', ''))
    movie = str(self.kwargs.get('movie', ''))

    if user:
        context['calificadas'] = Rating.objects.filter(user = user)
        context['no_calificadas'] = get_no_calificadas(user)
        
    context['user'] = user
    context['movie'] = movie

    return context

class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        get_context(self, context)
        user = context['user']
        movie = context['movie']
        predicciones = {}

        print('Cargando data db . . .')
        start = time.time()
        data = get_data(user, movie)
        print(len(data))
        print('Data db:', time.time() - start)

        print('Generando matriz coseno . . .')
        start = time.time()
        matriz_coseno = coseno(data[user], data)
        print('Matriz:', time.time() - start)

        print('Generando matriz coseno ajustado . . .')
        start = time.time()
        matriz_coseno_ajustado = coseno_ajustado(data[user], data)
        print('Matriz:', time.time() - start)

        print('Generando matriz correlacion pearson . . .')
        start = time.time()
        matriz_correlacion_pearson = correlacion_pearson(data[user], data)
        print('Matriz:', time.time() - start)

        print('Generando matriz desviacion . . .')
        start = time.time()
        matriz_desviacion = desviacion(data[user], data)
        print('Matriz:', time.time() - start)

        print('Prediciendo coseno . . .')
        start = time.time()
        predicciones['coseno'] = prediccion_similitud(data[user], movie, matriz_coseno)
        print('Prediccion:', time.time() - start)

        print('Prediciendo coseno ajustado . . .')
        start = time.time()
        predicciones['coseno_ajustado'] = prediccion_similitud(data[user], movie, matriz_coseno_ajustado)
        print('Prediccion:', time.time() - start)

        print('Prediciendo correlacion . . .')
        start = time.time()
        predicciones['correlacion_pearson'] = prediccion_similitud(data[user], movie, matriz_correlacion_pearson)
        print('Prediccion:', time.time() - start)

        print('Prediciendo slope one . . .')
        start = time.time()
        predicciones['slope_one'] = slope_one(data[user], movie, matriz_desviacion)
        print('Prediccion:', time.time() - start)

        context['predicciones'] = predicciones

        print('zScore . . .')
        print(zscore(data))

        print('DS . . .')
        print(ds(data))
        return context

class CosenoRecomendarView(TemplateView):
    template_name = "recomendar.html"

    def get_context_data(self, **kwargs):
        context = super(CosenoRecomendarView, self).get_context_data(**kwargs)
        get_context(self, context)
        user = context['user']
        movie = context['movie']

        print('Cargando data db . . .')
        start = time.time()
        data = get_data(user, movie)
        print(len(data))
        print('Data db:', time.time() - start)

        print('Generando matriz . . .')
        start = time.time()
        matriz = coseno(data[user], data)
        print('Matriz:', time.time() - start)

        print('Prediciendo . . .')
        start = time.time()
        print(prediccion_similitud(data[user], movie, matriz))
        print('Prediccion:', time.time() - start)

        print('Recomendando . . .')
        start = time.time()
        recomendadas = reco_similitud(data[user], matriz)[:10]
        print('Recomendación:', time.time() - start)

        for e in recomendadas:
            e.append(Movie.objects.get(pk = e[1]).title)

        context['recomendadas'] = recomendadas

        return context

class CosenoAjustadoRecomendarView(TemplateView):
    template_name = "recomendar.html"

    def get_context_data(self, **kwargs):
        context = super(CosenoAjustadoRecomendarView, self).get_context_data(**kwargs)
        get_context(self, context)
        user = context['user']
        movie = context['movie']

        print('Cargando data db . . .')
        start = time.time()
        data = get_data(user, movie)
        print(len(data))
        print('Data db:', time.time() - start)

        print('Generando matriz . . .')
        start = time.time()
        matriz = coseno_ajustado(data[user], data)
        print('Matriz:', time.time() - start)

        print('Prediciendo . . .')
        start = time.time()
        print(prediccion_similitud(data[user], movie, matriz))
        print('Prediccion:', time.time() - start)

        print('Recomendando . . .')
        start = time.time()
        recomendadas = reco_similitud(data[user], matriz)[:10]
        print('Recomendación:', time.time() - start)

        for e in recomendadas:
            e.append(Movie.objects.get(pk = e[1]).title)

        context['recomendadas'] = recomendadas

        return context

class CorrelacionPearsonRecomendarView(TemplateView):
    template_name = "recomendar.html"

    def get_context_data(self, **kwargs):
        context = super(CorrelacionPearsonRecomendarView, self).get_context_data(**kwargs)
        get_context(self, context)
        user = context['user']
        movie = context['movie']

        print('Cargando data db . . .')
        start = time.time()
        data = get_data(user, movie)
        print(len(data))
        print('Data db:', time.time() - start)

        print('Generando matriz . . .')
        start = time.time()
        matriz = correlacion_pearson(data[user], data)
        print('Matriz:', time.time() - start)

        print('Prediciendo . . .')
        start = time.time()
        print(prediccion_similitud(data[user], movie, matriz))
        print('Prediccion:', time.time() - start)

        print('Recomendando . . .')
        start = time.time()
        recomendadas = reco_similitud(data[user], matriz)[:10]
        print('Recomendación:', time.time() - start)

        for e in recomendadas:
            e.append(Movie.objects.get(pk = e[1]).title)

        context['recomendadas'] = recomendadas

        return context

class SlopeOneRecomendarView(TemplateView):
    template_name = "recomendar.html"

    def get_context_data(self, **kwargs):
        context = super(SlopeOneRecomendarView, self).get_context_data(**kwargs)
        get_context(self, context)
        user = context['user']
        movie = context['movie']

        print('Cargando data db . . .')
        start = time.time()
        data = get_data(user, movie)
        print(len(data))
        print('Data db:', time.time() - start)

        print('Generando matriz . . .')
        start = time.time()
        matriz = desviacion(data[user], data)
        print('Matriz:', time.time() - start)

        print('Prediciendo . . .')
        start = time.time()
        print(slope_one(data[user], movie, matriz))
        print('Prediccion:', time.time() - start)

        print('Recomendando . . .')
        start = time.time()
        recomendadas = reco_slope_one(data[user], matriz)[:10]
        print('Recomendación:', time.time() - start)

        for e in recomendadas:
            e.append(Movie.objects.get(pk = e[1]).title)

        context['recomendadas'] = recomendadas

        return context

class SlopeOnePesosRecomendarView(TemplateView):
    template_name = "recomendar.html"

    def get_context_data(self, **kwargs):
        context = super(SlopeOnePesosRecomendarView, self).get_context_data(**kwargs)
        get_context(self, context)
        user = context['user']
        movie = context['movie']

        print('Cargando data db . . .')
        start = time.time()
        data = get_data(user, movie)
        print(len(data))
        print('Data db:', time.time() - start)

        print('Generando matriz . . .')
        start = time.time()
        matriz = desviacion(data[user], data)
        print('Matriz:', time.time() - start)

        print('Prediciendo . . .')
        start = time.time()
        print(slope_one_pesos(data[user], movie, matriz))
        print('Prediccion:', time.time() - start)

        print('Recomendando . . .')
        start = time.time()
        recomendadas = reco_slope_one_pesos(data[user], matriz)[:10]
        print('Recomendación:', time.time() - start)

        for e in recomendadas:
            e.append(Movie.objects.get(pk = e[1]).title)

        context['recomendadas'] = recomendadas

        return context


def calificar(request, user):
    rating = request.POST.get('rating', None)
    movie = request.POST.get('movie', None)
    action = request.POST.get('action', None)
    if action == 'calificar':
        if rating != None and movie != None:
            m = Rating()
            m.rating = rating
            m.movie = Movie.objects.get(pk = movie)
            m.user = user
            m.timestamp = 0
            m.save()
        return redirect(reverse('movies:index', kwargs={'user': user}))
    else:
        return redirect(reverse('movies:predecir', kwargs={'user': user, 'movie': movie}))
