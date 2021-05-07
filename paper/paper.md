---
title: 'Detección de Comportamiento Coordinado De Intercambio de Enlaces (Coordinated Link Sharing)'
tags:
  - Social Networks
  - Graphs
  - Coordinated behavior
  - CLSB
  - Python
  - Clustering
authors:
  - name: Soto, Camilo
    orcid: 0000-0001-9831-6131
    affiliation: 1
  - name: Zapata, Jose R
    orcid: 0000-0003-1484-5816
    affiliation: 1
affiliations:
 - name: Universidad Pontificia Bolivariana
   index: 1
date: 4 Mayo 2021
bibliography: paper.bib
---

# Keywords
Social Networks, Facebook, Graphs, Coordinated behavior, CLSB, Python, Clustering, Community Detection

# Summary
Gracias al uso masificado de las redes sociales y de su inmediatez, la difusión de noticias ha cobrado una relevancia importante, lo que antes tardaba una gran cantidad de tiempo en difundirse, ahora en solamente en unos minutos puede volverse viral. Este tipo de comportamientos tienen una gran influencia en la opinión de las masas, ejemplos de esto son los resultados de votaciones populares como el plebiscito por la paz en Colombia del 2016, Las elecciones presidenciales de Estados Unidos de América o el referendo para que el Reino Unido abandonara la Unión Europa (Brexit). Usando PyCoorNet [@pycoornet], una herramienta que permita analizar datos en una red social para descubrir patrones de comportamiento coordinado para compartir enlaces con el fin de detectar intentos de volver viral una noticia, se pretende analizar enlaces compartidos por TeleSur English en la red social Facebook [@facebook] con el objetivo de detectar este comportamiento.

# Motivaciones


# Objetivos

# Tiempo De Coordinación
El tiempo coordinación es el umbral de tiempo en segundos en el cual se define que un enlace es compartido coordinadamente. Es normal que un mismo enlace sea compartido por diferentes entidades de una red social, no es normal que se compartan en un tiempo inusualmente corto, lo cuál lo conviernte en un sospechos de una viralización intencionada y posiblemente de un comportamiento coordinado para este fin [@Giglietto2020].


# Detección De El Comportamiento Coordinado De Intercambio De Enlaces
Como se visualiza en \autoref{fig:clsb_flow}, para detectar el comportamiento coordinado de intercambio de enlaces se debe tener un set de datos con los  grupos, páginas y/o personas que compartieron el enlace en la red social, transformar los datos para extraer un tiempo de coordinación y usarlo como parámetro con el fin de detectar los enlaces y entidades de la red social que se comportan con este fenómeno. Esto permite usar técnicas de ciencia de datos y visualización compleja de datos para analizar el resultado.

![Flujo de detección del comportamiento coordinado de intercambio de enlaces\label{fig:clsb_flow}](img/clsb-flow.png){width=80%}

# Caso De Estudio

En el artículo "Understanding Coordinated and Inauthentic Link Sharing Behavior on Facebook in the Run-up of 2018 General Election and 2019 European Election in Italy" [@Giglietto2019], usando ingeniería de características, los autores proponen calcular el tiempo de coordinación calculando los deltas en tiempo entre que se compartió por primera vez cada link y el resto de estos, asignándole a estos deltas un quantil al que pertenencen para luego filtrar los datos a la muestra poblacional objetivo.

Si bien, escogiendo correctamente el quantil y el tamaño de la muestra poblacional, este es un método que funciona para periodos de tiempo de estudio cortos. Esta metodología supone que el fenómeno de coordinación se genera inmediatamente se comparte por primera vez el enlace, de lo contrario, los tiempos de coordinación se vuelven demasiado grandes y es susceptibles a los datos atípicos.

Por lo tanto, en el proyecto "Social Media Behaviour" de la Universidad Pontificia Bolivariana [@Bolivariana2021] se optó por utilizar técnicas de Aprendijade de Máquinas para detectar este tiempo de coordinación.

Tomando 4.077 URLs extraidas del Condor URLs data set [@Bakshy1130], usando PyCrowdTangle [@pycrowdtangle] se hace una extracción de publicaciones de Facebook en CrowdTangle [@crowdtangle], una herramienta propiedad de Facebook que rastrea interacciones en contenido público de páginas y grupos de Facebook, perfiles verificados, cuentas de Instagram y subreddits. No incluye anuncios pagados a menos que esos anuncios comenzaran como publicaciones orgánicas y no pagas que posteriormente fueron "impulsadas" utilizando las herramientas publicitarias de Facebook. Tampoco incluye la actividad en cuentas privadas o publicaciones visibles solo para grupos específicos de seguidores, el resultado es total de 15.636 publicaciones válidas, las cuáles son análisadas por medio de PyCooRnet para detectar el comportamiento coordinado de intercambio de enlaces.

Realizando extracción, transformación y carga de los datos (ETL), se construye un set de datos el cual, por medio de técnicas de aprendizaje de máquinas y modelos no supervisados [@8713992] se obtiene un tiempo de coordinación que sirve como parámetro de entrada para un modelo que usa el  método de clusterización Louvain para el análisis de comunidades [@Blondel2008] sobre grafos detecta las páginas y grupos de Facebook que se comportan como una comunidad compartiendo enlaces entre sí.

Usando herramientas de visualización de grafos como gephi [@ICWSM09154] podemos analizar el fenómeno en cuestión.

![Grafo de Coordinated Link Sharing de Telesur English\label{fig:telesur_graph}](img/telesur_nov.png){width=50%}

En \autoref{fig:telesur_graph} los nodos representan las páginas y grupos de facebook que tienen un comportamiento coordinado, los colores representan la comunidad al cual pertenece el nodo, y su tamaño la influencia de este grupo en el fenómeno analizado.


# Modelamiento

Siguiento la metodología propuesta en Giglieto, Righetti y Marino [@Giglietto2020], se calcula el intervalo de coordinación tomando tomando para cada una de las URL (Localizador de Recursos Uniforme) [@BernersLee1994], la diferencia de tiempo entre esta y el momento que fue compartida por primera vez.

Datos los parámetros  *Q* (cuantil de las URL más rápidas que se filtrarán) y *P* (el porcentaje del total de publicaciones que se analizarán) se realizan las siguientes tranformaciones:

```python
firstShareDate = min(url['date'])
url['secondsFromFirstShare'] = url['date'])-firstShareDate
```
Se calculan rangos de las URL a partir de la fecha en que el enlace fué compartido, organizándolos de menor a mayor
```python
url['rank'] = url[date].rank(ascending=True, method='first')
url['perc_of_shares'] = url[date].rank(ascending=True, method='average')
```
``url['rank']`` es usado para encontrar la segunda vez que se compartió esa URL, y así calcular cuál fué el tiempo inusual más rápido.

``url['perc_of_shares']`` almacena el rango promedio dentro el grupo, ese valor se usa para filtrar con el pámetro *P*. [@pythonrank]


Se calculan las publicaciones que compartieron estas URL en el percentil (parámetro dado por el usuario) con el intervalo de compartido más corto ``url['secondsFromFirstShare']``.

Usando *Q* y *P* , se promedian los tiempos y se calcula el *el intervalo de coordinacion*.

Tomando este este valor se filtran las URLs (independientemente de quien realiza la publicación) para tomar las URL que se compartieron dentro este umbral.

|      | Seg. desde el primer share |
|------|---------------------------:|
| mean | 7.248.030                  |
| std  | 1.986.423                  |
| min  | 0                          |
| 10%  | 0                          |
| 20%  | 1.955                      |
| 30%  | 10.863                     |
| 40%  | 23.302                     |
| 50%  | 40.108                     |
| 60%  | 64.195                     |
| 70%  | 110.119                    |
| 80%  | 232.424                    |
| 90%  | 38.289.150                 |
| max  | 120.799.000                |

Table: Descriptores de los segudos desde el primer share \label{tbl:firtShare}

![Box Plot\label{fig:bloxplot1}](img/bloxplot1.png){width=70%}

En \autoref{tbl:firtShare} se observa que los tiempos en los diferentes percentiles es demasiado alto y se gran cantidad de datos atípicos  \autoref{fig:bloxplot1}. Con esta metodología debe empezar a iterear entre diferentes quantiles y submuestras poblacionales. Este proceso iterativo necesita una alta carga computacional

En el proyecto, se decidió utilizar un modelo no supervisado para calcular el tiempo de coordinación.

El set de datos se agrupó por enlace y se organizó por fecha y hora en que se compartío, par aluego calcular el delta entre cada uno de los enlaces con el fin de crear un histograma de estos deltas, independiente del enlace. Con esto eliminamos el posible sesgo de tiempo que se genera si el tiempo entre que se comparte el primer enlace y el momento en que se comparte "viralmente" es alto.

Se cambiaron los deltas de tiempo a una escala logarítmica con el fin de acercar su comportamiento a una distribución normal. En \autoref{fig:histograma} visualizamos su histograma.

![Histograma\label{fig:histograma}](img/hist1.png){width=70%}


Usando K-means, se realiza realiza una clusterización de los datos y entrar a analizar los centroides.

Para escoger el valor K adecuado se usan el análisis de *suma de error al cuadrado* (SSE)  \autoref{fig:sse} y  *silueta*  (distancia de separación entre los clusters. Nos indica como está separado cada puento de un cluster a los clusters vecinos) \autoref{fig:silhouette} .

![SSE\label{fig:sse}](img/sse.png){width=70%}

![Silhouette\label{fig:silhouette}](img/silhouette.png){width=70%}

Analizando los resultados se concluye que el valor de K es igual a 2.

En \autoref{fig:kmeansPlot}  se observa la distribución de los tiempos en cada cluster. Los clusters están muy definidos con sus centroides muy separados entre ellos, lo cuál se puede comprobar con una prueba de diferencia de medias.

![Kmeans k=2\label{fig:kmeansPlot}](img/kmeans.png){width=70%}

En el cluster de la izquierda están concentrados los enlaces que su delta de tiempo de compartición entre ellos es el más bajo y con alto conteo.

El el cluster de la derecha se encuentran los enlaces con un delta de tiempo alto y con bajo conteo.

\autoref{fig:bloxplot} es un gráfico de Box Plot que permite observar la alta diferencia de medias de los 2 clusters.

![Clusters boxplot\label{fig:bloxplot}](img/boxplot.png){width=70%}



Tomando el centroide del cluster 0 obtenemos un tiempo en base logarítmica de 2.84 segundos, lo que equivale a 17 segundos en base decimal.

Este tiempo de coordinación lo usamos como parámetro para los otros modelos que dan como resultado los enlaces que se comportan como el fenómeno que estamos analizando y un grafo con las comunidades de entidades que lo realizan.

En \autoref{tbl:tiempoCoord} se observan las diferencias de tiempos de coordinación calculados con ambas metodologías en diferentes sets de datos.

| Set de datos  | Metodología Giglieto | Metodología Machine Learning |
| ------------- | -------------------: | ---------------------------: |
| Common Dreams |                   25 |                           16 |
| Intercept     |                  241 |                           19 |
| MintPress     |                   15 |                           18 |
| Misión Verdad |                  606 |                              |
| Teen Voge     |                 1200 |                           16 |
| Telesur       |                   60 |                           17 |
| The Nation    |                   65 |                              |
| The Real News |                 1200 |                              |
| Yes Magazine  |                 1200 |                              |

Table: Tiempo de coordinación en segundos  \label{tbl:tiempoCoord}

# Análisis de resultados Telesur

* Se encontraron 898 páginas o grupos diferenciados en 131 comunidades (clusters).

* El 50% de las páginas o grupos que tienen un comportamiento coordinado, están agrupadas en 7 comunidades. \autoref{fig:clusters}.

![Comunidades.\label{fig:clusters}](img/clusters.png){width=60%}

* La página o grupo más influenciadores son:

| Página o grupo                                                                 | Fuerza | Suscriptores | Enlaces | Cluster |
|--------------------------------------------------------------------------------|--------|--------------|---------|---------|
| [1 Progressive Activists](https://www.facebook.com/940257989416472)            | 568    | 13.333       | 647     | 0       |
| [The Progressive Party](https://www.facebook.com/742985139150026)              | 497    | 12.331       | 139     | 1       |
| [Bernie Believers [Bernie Sanders]](https://www.facebook.com/1500083383618517) | 477    | 42.858       | 322     | 11      |
| [Berniecrats](https://www.facebook.com/547808012048444)                        | 420    | 43.976       | 367     | 5       |
| [America for Bernie Sanders 2020](https://www.facebook.com/208802505933373)    | 419    | 40.134       | 493     | 1       |




# References