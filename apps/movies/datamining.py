from apps.movies.functions import media, normalizar, desnormalizar
import math

def coseno(target, data):
    similitudes = {}
    longitudes = {}

    for f1 in target.keys():
        similitudes[f1] = {}

    for values in data.values():
        for f1, r1 in values.items():
            longitudes.setdefault(f1, 0.0)
            longitudes[f1] += r1
            if f1 not in target: continue
            for f2, r2 in values.items():
                if f1 == f2: continue
                similitudes[f1].setdefault(f2, 0.0)
                similitudes[f1][f2] += r1 * r2

    for f1, values in similitudes.items():
        for f2 in values:
            denominador = math.sqrt(longitudes[f1] * longitudes[f2])
            if denominador == 0:
                values[f2] = 0
            else:
                values[f2] /= denominador

    return similitudes

def coseno_ajustado(target, data):
    sum_ij = {}
    sum_i = {}
    sum_j = {}

    for f1 in target.keys():
        sum_ij[f1] = {}
        sum_i[f1] = {}
        sum_j[f1] = {}

    for values in data.values():
        m = media(values)
        for f1, r1 in values.items():
            if f1 not in target: continue
            for f2, r2 in values.items():
                if f1 == f2: continue
                sum_ij[f1].setdefault(f2, 0.0)
                sum_i[f1].setdefault(f2, 0.0)
                sum_j[f1].setdefault(f2, 0.0)
                sum_ij[f1][f2] += (r1 - m) * (r2 - m)
                sum_i[f1][f2] += (r1 - m) ** 2
                sum_j[f1][f2] += (r2 - m) ** 2

    for f1, values in sum_ij.items():
        for f2 in values:
            denominador = math.sqrt(sum_i[f1][f2] * sum_j[f1][f2])
            if denominador == 0:
                values[f2] = 0
            else:
                values[f2] /= denominador

    return sum_ij

def zscore(data):
    m = 0
    sumatoria = 0
    for values in data.values():
        m = media(values)
        card = len(values)
        for f1,r1 in values.items():
            sumatoria += pow(r1-m,2)
        return math.sqrt(sumatoria/card)

def ds(data):
    sumatoria = 0
    for values in data.values():
        m = media(values)
        for index in values.items():
            sumatoria += (index[1]-m)
        return sumatoria/len(values)


def correlacion_pearson(target, data):
    sum_ij = {}
    sum_i = {}
    sum_j = {}

    medias = {}
    frecuencias = {}

    for values in data.values():
        for feature, value in values.items():
            medias.setdefault(feature, 0.0)
            frecuencias.setdefault(feature, 0)
            medias[feature] += value
            frecuencias[feature] += 1

    for feature in medias:
        medias[feature] /= frecuencias[feature]

    for f1 in target.keys():
        sum_ij[f1] = {}
        sum_i[f1] = {}
        sum_j[f1] = {}

    for values in data.values():
        for f1, r1 in values.items():
            if f1 not in target: continue
            m1 = medias[f1]
            for f2, r2 in values.items():
                if f1 == f2: continue
                sum_ij[f1].setdefault(f2, 0.0)
                sum_i[f1].setdefault(f2, 0.0)
                sum_j[f1].setdefault(f2, 0.0)
                m2 = medias[f2]
                sum_ij[f1][f2] += (r1 - m1) * (r2 - m2)
                sum_i[f1][f2] += (r1 - m1) ** 2
                sum_j[f1][f2] += (r2 - m2) ** 2

    for f1, values in sum_ij.items():
        for f2 in values:
            denominador = math.sqrt(sum_i[f1][f2] * sum_j[f1][f2])
            if denominador == 0:
                values[f2] = 0
            else:
                values[f2] /= denominador

    return sum_ij

def prediccion_similitud(target, feature, matriz):
    normalizado = normalizar(target)
    numerador = 0.0
    denominador = 0.0

    for key, value in normalizado.items():
        if feature in matriz[key]:
            sim = matriz[key][feature]

            numerador += sim * value
            denominador += abs(sim)

    if denominador == 0:
        return 0

    return desnormalizar(numerador / denominador, target)

def reco_similitud(target, matriz):
    recomendaciones = {}
    denominadores = {}

    for f1, value in target.items():
        for f2, sim in matriz[f1].items():
            if f2 in target: continue
            recomendaciones.setdefault(f2, 0.0)
            denominadores.setdefault(f2, 0)
            recomendaciones[f2] += sim * value
            denominadores[f2] += abs(sim)

    recomendaciones = [[value / denominadores[f] if denominadores[f] != 0 else 0, f] for f, value in recomendaciones.items()]
    recomendaciones.sort(reverse = True)

    return recomendaciones

def desviacion(target, data):
    desviaciones = {}
    frecuencias = {}

    for f1 in target.keys():
        desviaciones[f1] = {}
        frecuencias[f1] = {}

    for values in data.values():
        for f1, r1 in values.items():
            if f1 not in target: continue
            for f2, r2 in values.items():
                if f1 == f2: continue
                desviaciones[f1].setdefault(f2, 0.0)
                frecuencias[f1].setdefault(f2, 0)
                desviaciones[f1][f2] += r1 - r2
                frecuencias[f1][f2] += 1

    for f1, values in desviaciones.items():
        for f2 in values:
            values[f2] /= frecuencias[f1][f2]

    return (desviaciones, frecuencias)

def slope_one(target, feature, matriz):
    desviaciones, frecuencias = matriz
    numerador = 0.0
    denominador = 0.0

    for key, value in target.items():
        if feature in desviaciones[key]:
            desv = desviaciones[key][feature] * -1

            numerador += desv + value
            denominador += 1

    if denominador == 0:
        return 0

    return numerador / denominador

def slope_one_pesos(target, feature, matriz):
    desviaciones, frecuencias = matriz
    numerador = 0.0
    denominador = 0.0

    for key, value in target.items():
        if feature in desviaciones[key]:
            desv = desviaciones[key][feature] * -1
            frec = frecuencias[key][feature]

            numerador += (desv + value) * frec
            denominador += frec

    if denominador == 0:
        return 0

    return numerador / denominador

def reco_slope_one(target, matriz):
    desviaciones, frecuencias = matriz
    recomendaciones = {}
    frecuencias_rec = {}

    for f1, value in target.items():
        for f2, desv in desviaciones[f1].items():
            if f2 in target: continue
            recomendaciones.setdefault(f2, 0.0)
            frecuencias_rec.setdefault(f2, 0)
            recomendaciones[f2] += desv + value
            frecuencias_rec[f2] += 1

    recomendaciones = [[value / frecuencias_rec[f], f] for f, value in recomendaciones.items()]
    recomendaciones.sort(reverse = True)

    return recomendaciones

