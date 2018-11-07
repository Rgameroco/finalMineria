from apps.movies.models import *
from django.db import connection
import math

def get_data(user_id, movie_id):
    cursor = connection.cursor()
    cursor.execute('SELECT r.user::text, r.movie_id::text, r.rating FROM movies_rating r --WHERE r.movie_id in (SELECT rr.movie_id FROM movies_rating rr WHERE rr.user = %s) or r.movie_id = %s' %(user_id, movie_id))
    rows = cursor.fetchall()
    users = {}

    for user, movie, rating in rows:
        if user not in users:
            users[user] = {}
        users[user][movie] = rating

    return users

def get_features(user_id, movie_id):
    cursor = connection.cursor()
    cursor.execute('SELECT r.movie_id FROM movies_rating r WHERE r.user = %s' %user_id)
    rows = cursor.fetchall()

    features = []
    for e in rows:
        features.append(e[0])
    features.append(movie_id)

    return features

def get_no_calificadas(user_id):
    cursor = connection.cursor()
    cursor.execute('select * from movies_movie mo where mo.id not in (select movie_id from movies_rating r where r.user = %s) order by mo.id' %user_id)
    rows = cursor.fetchall()

    return rows


def media(data):
    if len(data) == 0:
        return 0
    return sum(data[key] for key in data) / len(data)

def normalizar(data):
    maximo = -99999999999
    minimo = 99999999999

    for key in data:
        if data[key] < minimo:
            minimo = data[key]
        if data[key] > maximo:
            maximo = data[key]

    dif = maximo - minimo
    normalizado = {}
    for key in data:
        if dif == 0:
            normalizado[key] = 0
        else:
            normalizado[key] = (2 * (data[key] - minimo) - (dif)) / (dif)

    return normalizado

def desnormalizar(normalizado, data):
    maximo = -99999999999
    minimo = 99999999999

    for key in data:
        if data[key] < minimo:
            minimo = data[key]
        if data[key] > maximo:
            maximo = data[key]

    return 0.5 * ((normalizado + 1) * (maximo - minimo)) + minimo


def scosenoajustado(feature1, feature2, data):
    sum_ij = 0
    sum_i = 0
    sum_j = 0
    for e in data:
        features = data[e]
        if feature1 in features and feature2 in features:
            m = media(features)
            sum_ij += (features[feature1] - m) * (features[feature2] - m)
            sum_i += (features[feature1] - m) ** 2
            sum_j += (features[feature2] - m) ** 2

    d = math.sqrt(sum_i) * math.sqrt(sum_j)

    if d == 0:
        return 0
    
    return sum_ij / d

def desviacion_estandar(feature1, feature2, data):
    suma = 0
    card = 0
    for e in data:
        features = data[e]
        if feature1 in features and feature2 in features:
            suma += features[feature1] - features[feature2]
            card += 1

    if card == 0:
        return 0

    return (suma / card, card)


def coseno(data):
    sum_ij = {}
    longitudes = {}

    for values in data.values():
        values = list(values.items())
        init = 0

        for f1, r1 in values:
            init += 1

            if f1 not in longitudes:
                longitudes[f1] = 0
            longitudes[f1] += r1

            for f2, r2 in values[init:]:
                tf1 = f1
                tf2 = f2
                tr1 = r1
                tr2 = r2
                existe = False

                if f1 in sum_ij:
                    if f2 in sum_ij[f1]:
                        existe = True
                
                if not existe:
                    if f2 in sum_ij:
                        if f1 in sum_ij[f2]:
                            existe = True
                            tf1 = f2
                            tf2 = f1
                            tr1 = r2
                            tr2 = r1

                if not existe:
                    if tf1 not in sum_ij:
                        sum_ij[tf1] = {}

                    if tf2 not in sum_ij[tf1]:
                        sum_ij[tf1][tf2] = 0

                sum_ij[tf1][tf2] += tr1 * tr2

    for f1, values in sum_ij.items():
        for f2 in values:
            d = math.sqrt(longitudes[f1]) * math.sqrt(longitudes[f2])
            if d == 0:
                sum_ij[f1][f2] = 0
            else:
                sum_ij[f1][f2] /= d

    return sum_ij

def coseno_ajustado(data):
    sum_ij = {}
    sum_i = {}
    sum_j = {}

    for values in data.values():
        m = media(values)
        values = list(values.items())
        init = 0

        for f1, r1 in values:
            init += 1

            for f2, r2 in values[init:]:
                tf1 = f1
                tf2 = f2
                tr1 = r1
                tr2 = r2
                existe = False

                if f1 in sum_ij:
                    if f2 in sum_ij[f1]:
                        existe = True
                
                if not existe:
                    if f2 in sum_ij:
                        if f1 in sum_ij[f2]:
                            existe = True
                            tf1 = f2
                            tf2 = f1
                            tr1 = r2
                            tr2 = r1

                if not existe:
                    if tf1 not in sum_ij:
                        sum_ij[tf1] = {}
                        sum_i[tf1] = {}
                        sum_j[tf1] = {}

                    if tf2 not in sum_ij[tf1]:
                        sum_ij[tf1][tf2] = 0
                        sum_i[tf1][tf2] = 0
                        sum_j[tf1][tf2] = 0

                sum_ij[tf1][tf2] += (tr1 - m) * (tr2 - m)
                sum_i[tf1][tf2] += (tr1 - m) ** 2
                sum_j[tf1][tf2] += (tr2 - m) ** 2

    for f1, values in sum_ij.items():
        for f2 in values:
            d = math.sqrt(sum_i[f1][f2]) * math.sqrt(sum_j[f1][f2])
            if d == 0:
                sum_ij[f1][f2] = 0
            else:
                sum_ij[f1][f2] /= d

    # matriz = {}
    # for i in range(len(features)):
    #     matriz[features[i]] = {}
    #     for j in range(i + 1, len(features)):
    #         matriz[features[i]][features[j]] = scosenoajustado(features[i], features[j], data)

    return sum_ij

def correlacion_pearson(data):
    medias = {}

    for values in data.values():
        for feature, value in values.items():
            if feature not in medias:
                medias[feature] = [0, 0]
            medias[feature][0] += value
            medias[feature][1] += 1

    for feature in medias:
        medias[feature] = medias[feature][0] / medias[feature][1]
    sum_ij = {}
    sum_i = {}
    sum_j = {}

    for values in data.values():
        values = list(values.items())
        init = 0

        for f1, r1 in values:
            init += 1

            for f2, r2 in values[init:]:
                tf1 = f1
                tf2 = f2
                tr1 = r1
                tr2 = r2
                existe = False
                print('f1',f1,'r1',r1,'tf1',tf1,'tf2',tf2)
                if f1 in sum_ij:
                    if f2 in sum_ij[f1]:
                        existe = True
                
                if not existe:
                    if f2 in sum_ij:
                        if f1 in sum_ij[f2]:
                            existe = True
                            tf1 = f2
                            tf2 = f1
                            tr1 = r2
                            tr2 = r1

                if not existe:
                    if tf1 not in sum_ij:
                        sum_ij[tf1] = {}
                        sum_i[tf1] = {}
                        sum_j[tf1] = {}

                    if tf2 not in sum_ij[tf1]:
                        sum_ij[tf1][tf2] = 0
                        sum_i[tf1][tf2] = 0
                        sum_j[tf1][tf2] = 0

                m1 = medias[tf1]
                m2 = medias[tf2]
                sum_ij[tf1][tf2] += (tr1 - m1) * (tr2 - m2)
                sum_i[tf1][tf2] += (tr1 - m1) ** 2
                sum_j[tf1][tf2] += (tr2 - m2) ** 2

    for f1, values in sum_ij.items():
        for f2 in values:
            d = math.sqrt(sum_i[f1][f2]) * math.sqrt(sum_j[f1][f2])
            if d == 0:
                sum_ij[f1][f2] = 0
            else:
                sum_ij[f1][f2] /= d

    return sum_ij

def aproximacion_pearson(data):
    sum_ij = {}
    sum_i = {}
    sum_j = {}
    sum_i2 = {}
    sum_j2 = {}
    sum_n = {}

    for values in data.values():
        values = list(values.items())
        init = 0

        for f1, r1 in values:
            init += 1

            for f2, r2 in values[init:]:
                tf1 = f1
                tf2 = f2
                tr1 = r1
                tr2 = r2
                existe = False

                if f1 in sum_ij:
                    if f2 in sum_ij[f1]:
                        existe = True
                
                if not existe:
                    if f2 in sum_ij:
                        if f1 in sum_ij[f2]:
                            existe = True
                            tf1 = f2
                            tf2 = f1
                            tr1 = r2
                            tr2 = r1

                if not existe:
                    if tf1 not in sum_ij:
                        sum_ij[tf1] = {}
                        sum_i[tf1] = {}
                        sum_j[tf1] = {}
                        sum_i2[tf1] = {}
                        sum_j2[tf1] = {}
                        sum_n[tf1] = {}

                    if tf2 not in sum_ij[tf1]:
                        sum_ij[tf1][tf2] = 0
                        sum_i[tf1][tf2] = 0
                        sum_j[tf1][tf2] = 0
                        sum_i2[tf1][tf2] = 0
                        sum_j2[tf1][tf2] = 0
                        sum_n[tf1][tf2] = 0

                sum_ij[tf1][tf2] += tr1 * tr2
                sum_i[tf1][tf2] += tr1
                sum_j[tf1][tf2] += tr2
                sum_i2[tf1][tf2] += tr1 ** 2
                sum_j2[tf1][tf2] += tr2 ** 2
                sum_n[tf1][tf2] += 1

    for f1, values in sum_ij.items():
        for f2 in values:
            d = math.sqrt(sum_i2[f1][f2] - (sum_i[f1][f2]**2) / sum_n[f1][f2]) * math.sqrt(sum_j2[f1][f2] - (sum_j[f1][f2]**2) / sum_n[f1][f2])
            if d == 0:
                sum_ij[f1][f2] = 0
            else:
                sum_ij[f1][f2] = sum_ij[f1][f2] - (sum_i[f1][f2] * sum_j[f1][f2]) / sum_n[f1][f2]

    return sum_ij

def pred_sim(target, feature, matriz):
    normalizado = normalizar(target)
    numerador = 0
    denominador = 0
    for key in normalizado:
        if feature in matriz and key in matriz[feature]:
            em = matriz[feature][key]
        elif key in matriz and feature in matriz[key]:
            em = matriz[key][feature]
        else:
            continue
        # print(em, normalizado[key])
        numerador += em * normalizado[key]
        denominador += abs(em)

    if denominador == 0:
        return 0

    # print(numerador / denominador)
    return desnormalizar(numerador / denominador, target)


def matriz_desviacion(data):
    sumas = {}
    cardinalidades = {}

    for values in data.values():
        # values = list(values.items())
        # init = 0

        for f1, r1 in values.items():
            if f1 not in sumas:
                sumas[f1] = {}
                cardinalidades[f1] = {}
            for f2, r2 in values.items():
                if f1 == f2: continue
                if f2 not in sumas[f1]:
                    sumas[f1][f2] = 0.0
                    cardinalidades[f1][f2] = 0.0

                sumas[f1][f2] += r1 - r2
                cardinalidades[f1][f2] += 1

    for f1, values in sumas.items():
        for f2 in values:
            values[f2] /= cardinalidades[f1][f2]

    return (sumas, cardinalidades)

def pred_slope_one_pesos(target, feature, matriz):
    desviacion, cardinalidad = matriz
    numerador = 0.0
    denominador = 0.0
    for key in target:
        if feature in desviacion and key in desviacion[feature]:
            em = desviacion[feature][key]
            card = cardinalidad[feature][key]
        else:
            continue

        print(key, card, em)
        
        numerador += (em + target[key]) * card
        denominador += card

    if denominador == 0:
        return 0

    return numerador / denominador

def pred_slope_one(target, feature, matriz):
    desviacion, cardinalidad = matriz
    numerador = 0
    denominador = 0

    for key in target:
        if feature in desviacion and key in desviacion[feature]:
            em = desviacion[feature][key]
        elif key in desviacion and feature in desviacion[key]:
            em = desviacion[key][feature] * -1
        else:
            em = 0

        # if feature in desviacion and key in desviacion[feature]:
        #     em = desviacion[feature][key]
        # else:
        #     em = 0
        
        numerador += em + target[key]
        denominador += 1

    if denominador == 0:
        return 0

    return numerador / denominador

def pred_slope_one_bipolar(target, feature, matriz):
    desviacion, cardinalidad = matriz
    numerador = 0
    denominador = 0
    m = media(target)
    for key in target:
        if feature in desviacion and key in desviacion[feature]:
            em = desviacion[feature][key]
            card = cardinalidad[feature][key]
        elif key in desviacion and feature in desviacion[key]:
            em = desviacion[key][feature] * -1
            card = cardinalidad[key][feature]
        else:
            continue

        # if feature in desviacion and key in desviacion[feature]:
        #     em = desviacion[feature][key]
        #     card = cardinalidad[feature][key]
        # else:
        #     continue
        
        numerador += (em + target[key]) * card
        denominador += card

    if denominador == 0:
        return 0

    return numerador / denominador

def reco_slope_one_pesos(target, matriz):
    desviacion, cardinalidad = matriz
    recomendaciones = {}
    cardinalidades = {}
    for feature, value in target.items():
        for dfeature, dvalues in desviacion.items():
            if dfeature not in target and feature in dvalues:
                card = cardinalidad[dfeature][feature]
                if dfeature not in recomendaciones:
                    recomendaciones[dfeature] = 0.0
                    cardinalidades[dfeature] = 0
                recomendaciones[dfeature] += (dvalues[feature] + value) * card
                cardinalidades[dfeature] += card
    
    recomendaciones = [(value / cardinalidades[feature], feature) for feature, value in recomendaciones.items()]
    recomendaciones.sort(reverse = True)

    return recomendaciones

