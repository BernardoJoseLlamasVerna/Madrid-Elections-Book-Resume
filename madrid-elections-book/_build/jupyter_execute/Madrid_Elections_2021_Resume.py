#!/usr/bin/env python
# coding: utf-8

# # Resumen de las elecciones a la Comunidad de Madrid 2021

# ## 0.-Objetivo del presente trabajo ##
# 
# El presente trabajo tiene como objetivo analizar los resultados de las elecciones autonómicas del 4 de mayo del 2021 en Madrid y sacar conclusiones sobre la distribución del voto mediante representaciones espaciales, así como su comparación con pasadas elecciones para sacar conclusiones de cómo ha ido variando.
# 
# ### Nota sobre la obtención de los datos: ###
# Los datos de las últimas elecciones se obtuvieron del siguiente enlace: https://resultados2021.comunidad.madrid/Mesas/es. Los pasos para analizar la información y procesarla están resumidos en el siguiente documento: Madrid_Elections_2021.ipynb . Al no conseguir datos similares con el mismo formato de pasadas elecciones autonómicas se optó por hacer un "web scrapper" de la página del periódico El País donde se resumen los votos obtenidos en las últimas 5 elecciones (2021, 2019, 2015, 2011 y 2007).

# ## 1.-Obtención y preparación de los datos ##

# Obtenemos los datos de las elecciones autonómicas de Madrid 2019 y 2021 haciendo "scrapping" de las siguientes páginas: 
# 
# * https://resultados.elpais.com/elecciones/2019/autonomicas/12/, 
# * https://resultados.elpais.com/elecciones/2021/autonomicas/12/
# 
# Para poder procesar la información de la web hemos tenido que instalar los siguientes paquetes:
# * **Instalamos beautifulsoup4:** pip install beautifulsoup4 
# * **Intalamos lxml:** pip install lxml 
# * **Instalamos requests library:** pip install requests

# Analizando la web a la que nos lleva la primera url vemos el resumen de enlaces que a su vez llevan a los datos de cada municipio. Estos enlaces están alojados en elementos 'ul' que a su vez tienen una lista de elementos 'li' con enlaces que llevan a cada página.
# 
# Vamos a obtener la lista resumen de esos elementos 'ul', 'li' y los enlaces para después procesar cada página:

# In[1]:


from bs4 import BeautifulSoup
import requests


# ### 1.0.-Preparación de los datos de 2019: 
# Obtenemos el texto html de la web y vemos que el elemento ul donde se aloja el resumen de municipios tiene la clase 'estirar':

# In[2]:


html_text = requests.get('https://resultados.elpais.com/elecciones/2019/autonomicas/12/').text
soup = BeautifulSoup(html_text, 'lxml')
# soup


# In[3]:


ul = soup.select('ul.estirar')[1]
# ul


# El resumen de elementos 'li':

# In[4]:


lis = ul.find_all('li') 
# lis


# Vamos a crear un array resumen que contenga el nombre de cada municipio y su link asociado:

# In[5]:


url = 'https://resultados.elpais.com/elecciones/2019/autonomicas/12/'
results_2019 = []
for li in lis:
    for link in li.find_all('a'):
        local_result = {}
        local_result['municipio'] = link.text
        local_result['link'] = url+link.get('href')
        results_2019.append(local_result)

results_2019[0]


# ### 1.0.0-Extracción de los datos de cada municipio
# 
# Vamos a hacer una prueba con una de las páginas donde se resumen los datos de un municipio para ver cómo tenemos que extraer los datos y después aplicarlo al resumen de municipios y links que hemos obtenido en results_2019.
# 
# Hacemos la prueba con el municipio de Madarcos:

# In[6]:


# link de pruebas (municipio Madarcos):
link_pruebas = 'https://resultados.elpais.com/elecciones/2019/autonomicas/12/28/78.html'

# obtenemos el código html:
html_text_municipio = requests.get(link_pruebas).text
soup = BeautifulSoup(html_text_municipio, 'lxml')
# soup


# Después de analizar dónde están los datos que buscamos podemos diferenciar dos tablas resumen con los siguientes identificadores:
# * **Tabla de escrutado:** 'id'='tablaResumen'
# * **Tabla resumen partidos:** 'id'='tablaVotosPartidos'

# ### Tabla de escrutado:
# Vemos que obtenemos los siguientes campos:

# In[7]:


table_escrutado = soup.find('table', {'id': 'tablaResumen'})
table_escrutado_trs = table_escrutado.find_all('tr')
table_escrutado_trs


# Y que podemos resumir los datos de la siguiente manera:

# In[8]:


results_table_escrutado = []
for tr in table_escrutado_trs:
    local_table_escrutado = {}
    local_table_escrutado['encabezado'] = None if tr.select_one('.encabezado') is None else tr.select_one('.encabezado').text
    local_table_escrutado['numero'] = None if tr.select_one('.tipoNumero') is None else tr.select_one('.tipoNumero').text
    local_table_escrutado['porcentaje'] = None if tr.select_one('.tipoPorciento') is None else tr.select_one('.tipoPorciento').text
    
    results_table_escrutado.append(local_table_escrutado)
    
results_table_escrutado


# De aquí podemos aplicar unas funciones para extraer los datos de los campos comunes en cada diccionario (encabezado, número y porcentaje) y pasar los valores de string a numéricos:

# In[9]:


def clean_strings_and_turn_float(value):
    if ' %' in value:
        return value.replace(' %', '').replace(',', '.')
    else:
        return value.replace('.', '')
    
def result_resume(results_table_escrutado):
    results_resume = []
    for result in results_table_escrutado:
        local_resume = {}
        if result.get('encabezado') == 'Escrutado:':
            local_resume['escrutado'] = clean_strings_and_turn_float(result.get('porcentaje'))
        if result.get('encabezado') == 'Votos contabilizados:':
            local_resume['votos_totales'] = clean_strings_and_turn_float(result.get('numero'))
            local_resume['votos_totales_porcentaje'] = clean_strings_and_turn_float(result.get('porcentaje'))
        if result.get('encabezado') == 'Abstenciones:':
            local_resume['abstencion'] = clean_strings_and_turn_float(result.get('numero'))
            local_resume['abstencion_porcentaje'] = clean_strings_and_turn_float(result.get('porcentaje'))
        if result.get('encabezado') == 'Votos nulos:':
            local_resume['votos_nulos'] = clean_strings_and_turn_float(result.get('numero'))
            local_resume['votos_nulos_porcentaje'] = clean_strings_and_turn_float(result.get('porcentaje'))
        if result.get('encabezado') == 'Votos en blanco:':
            local_resume['votos_blancos'] = clean_strings_and_turn_float(result.get('numero'))
            local_resume['votos_blancos_porcentaje'] = clean_strings_and_turn_float(result.get('porcentaje'))
        
        results_resume.append(local_resume)

    return results_resume

result_resume(results_table_escrutado)


# ### Tabla resumen partidos:
# Vemos que obtenemos los siguientes campos:

# In[10]:


table_partidos = soup.find('table', {'id': 'tablaVotosPartidos'})
table_partido_trs = table_partidos.find_all('tr')
table_partido_trs


# In[11]:


results_table_partido = []
for tr in table_partido_trs:
    local_table_partido = {}
    local_table_partido['partido'] = None if tr.select_one('.nombrePartido') is None else tr.select_one('.nombrePartido').text
    local_table_partido['numero_votos'] = None if tr.select_one('.tipoNumeroVotos') is None else tr.select_one('.tipoNumeroVotos').text
    local_table_partido['porcentaje'] = None if tr.select_one('.tipoPorcientoVotos') is None else tr.select_one('.tipoPorcientoVotos').text
    
    results_table_partido.append(local_table_partido)
    
results_table_partido


# Vamos a hacer un tratamiento parecido al caso de la tabla de escrutado: vamos a reducir los nombres de cada partido a minúsculas, si tienen más de una palabra las unimos por guiones y eliminamos acentos; los valores los pasamos de strings a valores numéricos y eliminamos los signos de porcentajes.

# In[12]:


import unicodedata

def strip_accents(text):
    try:
        text = unicode(text, 'utf-8')
    except NameError: # unicode is a default on python 3 
        pass

    text = unicodedata.normalize('NFD', text)           .encode('ascii', 'ignore')           .decode("utf-8")

    return str(text)
    
def result_partido_resume(results_table_partido):
    results_resume_partido = []
    for result in results_table_partido:
        local_resume = {}
        if result.get('partido') == None:
            continue
        else:
            partido = strip_accents(result.get('partido').lower().replace('-', '_').replace(' ', '_'))
            local_resume[partido] = clean_strings_and_turn_float(result.get('numero_votos'))
            local_resume[partido+'_porcentaje'] = clean_strings_and_turn_float(result.get('porcentaje'))
    
        results_resume_partido.append(local_resume)

    return results_resume_partido

result_partido_resume(results_table_partido)


# Ya podemos aplicar sobre todos los municipios. Para ellos definimos dos funciones que resumen lo que hemos hecho en ambas tablas:

# In[13]:


def table_escrutado(link):
    html_text_municipio = requests.get(link).text
    soup = BeautifulSoup(html_text_municipio, 'lxml')

    table_escrutado = soup.find('table', {'id': 'tablaResumen'})
    table_escrutado_trs = table_escrutado.find_all('tr')
    
    results_table_escrutado = []
    for tr in table_escrutado_trs:
        local_table_escrutado = {}
        local_table_escrutado['encabezado'] = None if tr.select_one('.encabezado') is None else tr.select_one('.encabezado').text
        local_table_escrutado['numero'] = None if tr.select_one('.tipoNumero') is None else tr.select_one('.tipoNumero').text
        local_table_escrutado['porcentaje'] = None if tr.select_one('.tipoPorciento') is None else tr.select_one('.tipoPorciento').text
    
        results_table_escrutado.append(local_table_escrutado)
    
    return results_table_escrutado


# In[14]:


def table_partido(link):
    html_text_municipio = requests.get(link).text
    soup = BeautifulSoup(html_text_municipio, 'lxml')
    
    table_partido = soup.find('table', {'id': 'tablaVotosPartidos'})
    table_partido_trs = table_partido.find_all('tr')
    
    results_table_partido = []
    for tr in table_partido_trs:
        local_table_partido = {}
        local_table_partido['partido'] = None if tr.select_one('.nombrePartido') is None else tr.select_one('.nombrePartido').text
        local_table_partido['numero_votos'] = None if tr.select_one('.tipoNumeroVotos') is None else tr.select_one('.tipoNumeroVotos').text
        local_table_partido['porcentaje'] = None if tr.select_one('.tipoPorcientoVotos') is None else tr.select_one('.tipoPorcientoVotos').text
    
        results_table_partido.append(local_table_partido)
        
    return results_table_partido


# Aplicamos sobre la url inicial desde la que accederemos a todos los municipios:

# In[15]:


url = 'https://resultados.elpais.com/elecciones/2019/autonomicas/12/'
results_pruebas = []
for li in lis:
    for link in li.find_all('a'):
        local_result = {}
        local_result['municipio'] = link.text
        local_result['link'] = url+link.get('href')
        local_result['escrutinio'] = table_escrutado(local_result['link'])
        local_result['partidos'] = table_partido(local_result['link'])
        results_pruebas.append(local_result)
        
results_pruebas[0]


# Vamos a chequear qué longitud tiene nuestra lista:

# In[16]:


len(results_pruebas)


# Vemos que tiene una longitud de 178 cuando se sabe que la Comunidad de Madrid tiene 179 municipios. Por lo tanto la página de inicio tiene un fallo y no presenta la información de un municipio.
# 
# Sabemos que el municipio que falta es La Acebeda. Más adelante cuando pasemos los resultados a un dataframe y le añadamos la información geográfica explicaremos cómo hemos sabido que era ese municipio.
# 
# Buscando de forma manual llegamos que la información electoral de La Acebeda para el año 2019 está resumida en este enlace: https://resultados.elpais.com/elecciones/2019/autonomicas/12/28/01.html

# In[17]:


# insertamos la info. asociada a La Acebeda:
la_acebeda = {}
la_acebeda['municipio'] = 'La Acebeda'
la_acebeda['link'] = 'https://resultados.elpais.com/elecciones/2019/autonomicas/12/28/01.html'
la_acebeda['escrutinio'] = table_escrutado(la_acebeda['link'])
la_acebeda['partidos'] = table_partido(la_acebeda['link'])
results_pruebas.insert(0, la_acebeda)

results_pruebas[0]


# Pasamos a presentar la información de una forma que nos sea más fácil de tratar como dataframe:

# In[18]:


results_pruebas_formatted = []

for result_prueba in results_pruebas:
    local_result = {}
    local_result['municipio'] = result_prueba['municipio']
    local_result['link'] = result_prueba['link']
    local_result['escrutinio'] = result_resume(result_prueba['escrutinio'])
    local_result['partidos'] = result_partido_resume(result_prueba['partidos'])
    
    results_pruebas_formatted.append(local_result)
    
results_pruebas_formatted[0]


# ### 1.0.1-Convertir la información en dataframe

# Vamos a crear un dataframe donde se muestre la información de cada municipio y el resumen de partidos a los que se ha votado en cada uno.

# In[19]:


import pandas as pd

df_partidos = pd.json_normalize(results_pruebas_formatted, record_path='partidos', meta=['municipio', 'link'])
df_partidos = df_partidos.groupby('municipio').apply(lambda x: x.bfill().head(1)).reset_index(drop=True)

df_escrutinio = pd.json_normalize(results_pruebas_formatted, record_path='escrutinio', meta=['municipio'])
df_escrutinio = df_escrutinio.groupby('municipio').apply(lambda x: x.bfill().head(1)).reset_index(drop=True)

df = pd.merge(df_partidos, df_escrutinio, on='municipio', how='outer')
df


# In[20]:


# cambiamos la posición de las columnas para una mejor presentación:
first_column = df.pop('municipio')
second_column = df.pop('link')
df.insert(0, 'municipio', first_column)
df.insert(1, 'link', second_column)
df


# In[21]:


df.count()


# ### 1.0.2-Añadir información geoespacial al dataframe:

# La información geoespacial la hemos obtenido del siguiente enlace: https://raw.githubusercontent.com/FMullor/TopoJson/master/MadridMunicipios.geojson.
# 
# Nos va a servir para poder realizar mapas de la distribución del voto en cada municipio.

# In[22]:


import geopandas as gpd
import matplotlib.pyplot as plt

# sacamos la info del link y ordenamos por orden alfabético los municipios:
municipios = 'https://raw.githubusercontent.com/FMullor/TopoJson/master/MadridMunicipios.geojson'
map_municipios = gpd.read_file(municipios)
map_municipios = map_municipios.sort_values('municipio')
map_municipios.head()


# In[23]:


map_municipios.info()


# Como podemos ver, el geodataframe map_municipios tiene como máximo 182 registros. A la hora de poder cruzar la información con nuestros dataframes, vemos que la columna 'municipio' tiene 182 registros, lo que significa que hay 3 elementos de más sabiendo que la Comunidad de Madrid tiene 179 municipios. Tenemos que investigar si hay elementos repetitivos y cuáles son. Una vez limpio, solo nos interesan las columnas 'municipio' y 'geometry':

# In[24]:


map_municipios = map_municipios[['municipio', 'geometry']]
map_municipios


# Vemos que hay municipios cuyo nombre al tener acentos o caracteres especiales no aparece correctamente y no va a coincidir con la información de nuestro dataframe. Para obtenerlos, hacemos: 

# In[25]:


no_intersection_map = set(map_municipios['municipio']).difference(set(df['municipio']))
len(no_intersection_map)
no_intersection_map


# Por lo tanto, procedemos a corregir los nombres:

# In[26]:


map_municipios['municipio'] = map_municipios['municipio'].replace([
 'AlcalÃ¡ de Henares',
 'AlcorcÃ³n',
 'CarabaÃ±a',
 'ChapinerÃ\xada',
 'ChinchÃ³n',
 'CobeÃ±a',
 'El VellÃ³n',
 'El Ã\x81lamo',
 'FuentidueÃ±a de Tajo',
 'GriÃ±Ã³n',
 'Horcajo de la Sierra',
 'JurisdicciÃ³n Macomunada de El Boalo y Manzanares el Real (El Chaparral)',
 'JurisdicciÃ³n Mancomunada de Cerdedilla y Navacerrada',
 'LeganÃ©s',
 'Morata de TajuÃ±a',
 'MÃ³stoles',
 'Navarredonda y San MamÃ©s',
 'Nuevo BaztÃ¡n',
 'Orusco de TajuÃ±a',
 'Perales de TajuÃ±a',
 'PinuÃ©car-Gandullas',
 'Pozuelo de AlarcÃ³n',
 'PrÃ¡dena del RincÃ³n',
 'RascafrÃ\xada',
 'RedueÃ±a',
 'San AgustÃ\xadn del Guadalix',
 'San MartÃ\xadn de Valdeiglesias',
 'San MartÃ\xadn de la Vega',
 'San SebastiÃ¡n de los Reyes',
 'Santa MarÃ\xada de la Alameda',
 'TorrejÃ³n de Ardoz',
 'TorrejÃ³n de Velasco',
 'TorrejÃ³n de la Calzada',
 'ValdepiÃ©lagos',
 'Valverde de AlcalÃ¡',
 'Villanueva de la CaÃ±ada',
 'Villarejo de SalvanÃ©s',
 'Villaviciosa de OdÃ³n'
], [
 'Alcalá de Henares',
 'Alcorcón',
 'Carabaña',
 'Chapinería',
 'Chinchón',
 'Cobeña',
 'El Vellón',
 'El Álamo',
 'Fuentidueña de Tajo',
 'Griñón',
 'Horcajo de la Sierra',
 'Jurisdicción Macomunada de El Boalo y Manzanares el Real (El Chaparral)',
 'Jurisdicción Mancomunada de Cerdedilla y Navacerrada',
 'Leganés',
 'Morata de Tajuña',
 'Móstoles',
 'Navarredonda y San Mamés',
 'Nuevo Baztán',
 'Orusco de Tajuña',
 'Perales de Tajuña',
 'Piñuécar-Gandullas',
 'Pozuelo de Alarcón',
 'Prádena del Rincón',
 'Rascafría',
 'Redueña',
 'San Agustín del Guadalix',
 'San Martín de Valdeiglesias',
 'San Martín de la Vega',
 'San Sebastián de los Reyes',
 'Santa María de la Alameda',
 'Torrejón de Ardoz',
 'Torrejón de Velasco',
 'Torrejón de la Calzada',
 'Valdepiélagos',
 'Valverde de Alcalá',
 'Villanueva de la Cañada',
 'Villarejo de Salvanés',
 'Villaviciosa de Odón'])

map_municipios.head()


# Vemos si hay valores repetidos:

# In[27]:


# sacamos los nombres de los municipios y los metemos en una lista:
municipios = map_municipios['municipio'].to_list()
#comprobamos qué nombres de municipios pueden estar repetidos:
set([x for x in municipios if municipios.count(x) > 1])


# Vemos si los valores de 'geometry' de 'Arroyomolinos' son los mismos y por lo tanto se pueden eliminar sin problema:

# In[28]:


map_municipios[map_municipios['municipio'] == 'Arroyomolinos']


# Son los mismos, se puede eliminar un registro:

# In[29]:


# nos quedamos solo con un valor de Arroyomolinos (keep = 'first'):
map_municipios.drop_duplicates(subset ="municipio", keep = 'first', inplace = True)
map_municipios[map_municipios['municipio'] == 'Arroyomolinos']


# Vemos si pueden haber diferencias entre los nombres de los municipios:

# In[30]:


no_intersection_map = set(map_municipios['municipio']).difference(set(df['municipio']))
len(no_intersection_map)
no_intersection_map


# Comprobamos con qué nombres se corresponderían estos municipios de map_municipios con los que tenemos en nuestro dataframe:
# 
# * Horcajo de la Sierra : Horcajo de la Sierra-Aoslos,
# * Jurisdicción Macomunada de El Boalo y Manzanares el Real (El Chaparral) : Manzanares el Real,
# * Jurisdicción Mancomunada de Cerdedilla y Navacerrada : Navacerrada

# Antes de corregir los nombres, comprobamos si ya existen en map_municipios:

# In[31]:


map_municipios[map_municipios['municipio'] == 'Horcajo de la Sierra-Aoslos']


# In[32]:


map_municipios[map_municipios['municipio'] == 'Manzanares el Real']


# In[33]:


map_municipios[map_municipios['municipio'] == 'Navacerrada']


# Se ve que 'Horcajo de la Sierra-Aoslos' es el único que no existe, por lo tanto se puede reemplazar.
# 
# Tenemos que ver si los otros dos pares de nombres de municipios tienen los mismos valores de 'geometry':

# In[34]:


geometry_1 = map_municipios[map_municipios['municipio'] == 'Manzanares el Real']['geometry']
geometry_2 = map_municipios[map_municipios['municipio'] == 'Jurisdicción Macomunada de El Boalo y Manzanares el Real (El Chaparral)']['geometry'] 

print(geometry_1)
print(geometry_2)


# In[35]:


geometry_3 = map_municipios[map_municipios['municipio'] == 'Navacerrada']['geometry']
geometry_4 = map_municipios[map_municipios['municipio'] == 'Jurisdicción Mancomunada de Cerdedilla y Navacerrada']['geometry'] 

print(geometry_3)
print(geometry_4)


# No tienen el mismo valor de 'geometry', por lo tanto solo vamos a corregir 'Horcajo de la Sierra' y los otros dos desaparecerán a la hora de mergear con nuestro dataframe:

# In[36]:


map_municipios['municipio'] = map_municipios['municipio'].replace({
    'Horcajo de la Sierra': 'Horcajo de la Sierra-Aoslos',
})

no_intersection_map = set(map_municipios['municipio']).difference(set(df['municipio']))
len(no_intersection_map)
no_intersection_map


# Ya podemos mergear para que nuestro dataframe tenga información geoespacial:

# In[37]:


df_2019 = pd.merge(df, map_municipios, how='left', on='municipio')
df_2019.info()


# Pasamos las columnas a valores numéricos, excepto 'municipio', 'link' y 'geometry':

# In[38]:


cols = df_2019.columns.drop(['municipio', 'link', 'geometry'])

df_2019[cols] = df_2019[cols].apply(pd.to_numeric, errors='coerce', axis=1)
df_2019.info()


# ### 1.1.-Resumen del procedimiento:
# Todo el proceso hasta obtener una primera versión del dataframe se puede resumir en las siguientes funciones:

# In[39]:


def table_escrutado(link):
    from bs4 import BeautifulSoup
    import requests
    
    html_text_municipio = requests.get(link).text
    soup = BeautifulSoup(html_text_municipio, 'lxml')

    table_escrutado = soup.find('table', {'id': 'tablaResumen'})
    table_escrutado_trs = table_escrutado.find_all('tr')
    
    results_table_escrutado = []
    for tr in table_escrutado_trs:
        local_table_escrutado = {}
        local_table_escrutado['encabezado'] = None if tr.select_one('.encabezado') is None else tr.select_one('.encabezado').text
        local_table_escrutado['numero'] = None if tr.select_one('.tipoNumero') is None else tr.select_one('.tipoNumero').text
        local_table_escrutado['porcentaje'] = None if tr.select_one('.tipoPorciento') is None else tr.select_one('.tipoPorciento').text
    
        results_table_escrutado.append(local_table_escrutado)
    
    return results_table_escrutado


# In[40]:


def table_partido(link):
    from bs4 import BeautifulSoup
    import requests
    
    html_text_municipio = requests.get(link).text
    soup = BeautifulSoup(html_text_municipio, 'lxml')
    
    table_partido = soup.find('table', {'id': 'tablaVotosPartidos'})
    table_partido_trs = table_partido.find_all('tr')
    
    results_table_partido = []
    for tr in table_partido_trs:
        local_table_partido = {}
        local_table_partido['partido'] = None if tr.select_one('.nombrePartido') is None else tr.select_one('.nombrePartido').text
        local_table_partido['numero_votos'] = None if tr.select_one('.tipoNumeroVotos') is None else tr.select_one('.tipoNumeroVotos').text
        local_table_partido['porcentaje'] = None if tr.select_one('.tipoPorcientoVotos') is None else tr.select_one('.tipoPorcientoVotos').text
    
        results_table_partido.append(local_table_partido)
        
    return results_table_partido


# In[41]:


def clean_strings_and_turn_float(value):
    if ' %' in value:
        return value.replace(' %', '').replace(',', '.')
    else:
        return value.replace('.', '')
    
def result_resume(results_table_escrutado):
    results_resume = []
    for result in results_table_escrutado:
        local_resume = {}
        if result.get('encabezado') == 'Escrutado:':
            local_resume['escrutado'] = clean_strings_and_turn_float(result.get('porcentaje'))
        if result.get('encabezado') == 'Votos contabilizados:':
            local_resume['votos_totales'] = clean_strings_and_turn_float(result.get('numero'))
            local_resume['votos_totales_porcentaje'] = clean_strings_and_turn_float(result.get('porcentaje'))
        if result.get('encabezado') == 'Abstenciones:':
            local_resume['abstencion'] = clean_strings_and_turn_float(result.get('numero'))
            local_resume['abstencion_porcentaje'] = clean_strings_and_turn_float(result.get('porcentaje'))
        if result.get('encabezado') == 'Votos nulos:':
            local_resume['votos_nulos'] = clean_strings_and_turn_float(result.get('numero'))
            local_resume['votos_nulos_porcentaje'] = clean_strings_and_turn_float(result.get('porcentaje'))
        if result.get('encabezado') == 'Votos en blanco:':
            local_resume['votos_blancos'] = clean_strings_and_turn_float(result.get('numero'))
            local_resume['votos_blancos_porcentaje'] = clean_strings_and_turn_float(result.get('porcentaje'))
        
        results_resume.append(local_resume)

    return results_resume


# In[42]:


def strip_accents(text):
    import unicodedata
    try:
        text = unicode(text, 'utf-8')
    except NameError: # unicode is a default on python 3 
        pass

    text = unicodedata.normalize('NFD', text)           .encode('ascii', 'ignore')           .decode("utf-8")

    return str(text)


# In[43]:


def result_partido_resume(results_table_partido):
    results_resume_partido = []
    for result in results_table_partido:
        local_resume = {}
        if result.get('partido') == None:
            continue
        else:
            partido = strip_accents(result.get('partido').lower().replace('-', '_').replace(' ', '_'))
            local_resume[partido] = clean_strings_and_turn_float(result.get('numero_votos'))
            local_resume[partido+'_porcentaje'] = clean_strings_and_turn_float(result.get('porcentaje'))
    
        results_resume_partido.append(local_resume)

    return results_resume_partido


# In[44]:


def prepare_data_from_web(url, lis):
    data_from_web = []
    for li in lis:
        for link in li.find_all('a'):
            local_result = {}
            local_result['municipio'] = link.text
            local_result['link'] = url+link.get('href')
            local_result['escrutinio'] = table_escrutado(local_result['link'])
            local_result['partidos'] = table_partido(local_result['link'])
            
            data_from_web.append(local_result)
        
    return data_from_web


# In[45]:


def format_data(data_from_web):
    data_formatted = []
    for data in data_from_web:
        local_result = {}
        local_result['municipio'] = data['municipio']
        local_result['link'] = data['link']
        local_result['escrutinio'] = result_resume(data['escrutinio'])
        local_result['partidos'] = result_partido_resume(data['partidos'])
    
        data_formatted.append(local_result)
    
    return data_formatted


# In[46]:


def data_frame_preparation(data_formatted):
    import pandas as pd
    ## dataframe preparation
    df_partidos = pd.json_normalize(data_formatted, record_path='partidos', meta=['municipio', 'link'])
    df_partidos = df_partidos.groupby('municipio').apply(lambda x: x.bfill().head(1)).reset_index(drop=True)
    
    df_escrutinio = pd.json_normalize(data_formatted, record_path='escrutinio', meta=['municipio'])
    df_escrutinio = df_escrutinio.groupby('municipio').apply(lambda x: x.bfill().head(1)).reset_index(drop=True)
    
    df = pd.merge(df_partidos, df_escrutinio, on='municipio', how='outer')
    ## columns position switched:
    first_column = df.pop('municipio')
    second_column = df.pop('link')
    df.insert(0, 'municipio', first_column)
    df.insert(1, 'link', second_column)
    
    return df


# In[47]:


def extract_data_from_web(url):
    from bs4 import BeautifulSoup
    import requests
    # html code processing from url:
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'lxml')
    ul = soup.select('ul.estirar')[1]
    lis = ul.find_all('li')
    # preparing data before formatting:
    data_from_web = prepare_data_from_web(url, lis)
    # data formatted:
    data_formatted = format_data(data_from_web)
    ## dataframe 
    df = data_frame_preparation(data_formatted)
    
    return df


# ### 1.2.-Preparación de los datos de 2021: 
# 
# Aplicamos la función que resumen el procedimiento:

# In[48]:


url = 'https://resultados.elpais.com/elecciones/2021/autonomicas/12/'
df_2021 = extract_data_from_web(url)

df_2021


# In[49]:


len(df_2021)


# Se ve que el número de municipios coincide con los que tiene la CAM; aún así vamos a comprobar antes de añadir la información geoespacial.

# ### 1.2.1-Añadir información geoespacial al dataframe:

# Vemos si pueden haber diferencias entre los nombres de los municipios:

# In[50]:


no_intersection_map = set(map_municipios['municipio']).difference(set(df_2021['municipio']))
len(no_intersection_map)
no_intersection_map


# Son los mismos que antes, procedemos a mergear los dataframes:

# In[51]:


import pandas as pd
df_2021 = pd.merge(df_2021, map_municipios, how='left', on='municipio')
df_2021.info()


# In[52]:


# pasamos a valores numéricos todas las columnas excepto 'municipio', 'link' y 'geometry':
cols = df_2021.columns.drop(['municipio', 'link', 'geometry'])

df_2021[cols] = df_2021[cols].apply(pd.to_numeric, errors='coerce', axis=1)
df_2021.info()


# ## 2.-Contexto y análisis de los resultados

# El pasado 4 de mayo de 2021 se celebraron elecciones autonómicas en la Comunidad de Madrid, donde el Partido Popular fue el partido más votado con Isabel Díaz Ayuso repitiendo como candidata.
# 
# Estas elecciones se celebraron en un contexto particular: la irrupción del COVID-19 en España y el fin del período de confinamiento estricto de 99 días.
# 
# Las últimas elecciones se celebraron en 2019 donde el PSOE encabezado por Ángel Gabilondo fue el partido más votado frente a un PP desgastado a nivel regional y nacional por los casos de corrupción que tenían como epicentro la Comunidad de Madrid, pero no pudo formar gobierno por el apoyo de Ciudadanos (Cs) a Isabel Díaz Ayuso a cambio de formar un gobierno autonómico de coalición. Similares gobiernos PP-Cs existían en otras regiones como Castilla y León o Murcia. 
# 
# Precisamente en Murcia, debido a los rumores de negociaciones entre PSOE y Cs para retirar el apoyo al PP, llevaron a Isabel Díaz Ayuso a anticiparse y convocar elecciones para no perder el gobierno autonómico sabiendo que las encuestas le eran favorables por dos aspectos: 
# 
# * 1) la estrategia de oposición al Gobierno nacional por la gestión de la COVID-19 y canalizar el malestar que generó en muchos sectores el confinamiento. 
# 
# 
# * 2) las encuestas que indicaban una total caída del apoyo electoral a Cs, su socio de gobierno.
# 
# Vamos a pasar a analizar los resultados y a comentarlos.

# ### 2.1.-Exposición de los resultados

# En las elecciones autonómicas de 2019 los partidos que obtuvieron representación fueron PSOE, PP, Cs, Más Madrid, Vox y Podemos-IU. Por otro lado, en las elecciones de 2021 vemos el siguiente resultado: PP, Más Madrid, PSOE, Vox, Podemos-IU, desapareciendo Cs del mapa electoral.
# 
# Hay que indicar que para obtener representación institucional en las elecciones autonómicas hay que superar la barrera del 5% de votos. En las elecciones de 2019 se repartían 132 escaños, mientras que en 2021 por el aumento poblacional el reparto fue de 136 escaños.
# 
# Vamos a pasar a exponer los resultados absolutos por partidos tomando como referencia los resultados de cada unas de las elecciones.

# In[53]:


import numpy as np
import matplotlib.pyplot as plt
from chart_studio import plotly
import plotly.graph_objs as go
from plotly import tools
from plotly.offline import iplot, init_notebook_mode
init_notebook_mode()


# In[54]:


import plotly.graph_objects as go
parties=['pp', 'psoe', 'cs', 'mas_madrid', 'vox', 'podemos_iu']
final_results_2019 = [
    df_2019['pp'].sum(), 
    df_2019['psoe'].sum(),
    df_2019['cs'].sum(),
    df_2019['mas_madrid'].sum(),
    df_2019['vox'].sum(),
    df_2019['podemos_iu'].sum(),
]
final_results_2021 = [
    df_2021['pp'].sum(), 
    df_2021['psoe'].sum(),
    df_2021['cs'].sum(),
    df_2021['mas_madrid'].sum(),
    df_2021['vox'].sum(),
    df_2021['podemos_iu'].sum(),
]

fig = go.Figure(data=[
    go.Bar(name='2021', x=parties, y=final_results_2021),
    go.Bar(name='2019', x=parties, y=final_results_2019)
])
# Change the bar mode
fig.update_layout(title='Distribución del voto por partidos', barmode='group')
fig.show()


# Para saber cuál es la variación de los porcentajes de cada partido vamos a calcularlos con respecto al total de votos de cada elección. Para ello extraemos los resultados totales de cada partido en cada elección y creamos una función que nos da la diferencia en votos y porcentajes totales.

# In[55]:


# Dataset 2019

# excluimos las columnas de 'municipio', 'link' y 'geometry':
cols_2019 = df_2019.columns.drop(['municipio', 'link', 'geometry'])

# excluimos los porcentajes:
cols_votes_2019 = [col for col in cols_2019 if '_porcentaje' not in col]
cols_votes_2019 = [col for col in cols_votes_2019 if '_share' not in col]


# In[56]:


# Dataset 2021

# excluimos las columnas de 'municipio', 'link' y 'geometry':
cols_2021 = df_2021.columns.drop(['municipio', 'link', 'geometry'])

# excluimos los porcentajes:
cols_votes_2021 = [col for col in cols_2021 if '_porcentaje' not in col]
cols_votes_2021 = [col for col in cols_votes_2019 if '_share' not in col]


# In[57]:


def total_results(party, df_year):
    total_votes = df_year[party].sum()
    total_percentage = (df_year[party].sum()/(df_year['votos_totales'].sum()))*100
    
    total_votes = str("{:,}".format(total_votes)).strip('.0')+' votos'
    total_percentage = str(round(total_percentage, 2))+' %'
    
    return [total_votes, total_percentage]


# In[58]:


def difference_elections(party, df_year_1, df_year_2):
    votes_difference = df_year_1[party].sum() - df_year_2[party].sum()
    
    percentage_1 = (df_year_1[party].sum()/(df_year_1['votos_totales'].sum()))*100
    percentage_2 = (df_year_2[party].sum()/(df_year_2['votos_totales'].sum()))*100
    percentage_difference = percentage_1 - percentage_2
    
    votes_difference = str("{:,}".format(votes_difference)).strip('.0')+' votos'
    percentage_difference = str(round(percentage_difference, 2))+' %'
    
    return [votes_difference, percentage_difference]


# #### **Partido Popular**

# In[59]:


print('PP_2019: '+ total_results('pp', df_2019)[0] +' / '+ total_results('pp', df_2019)[1])
print('PP_2021: '+ total_results('pp', df_2021)[0] +' / '+ total_results('pp', df_2021)[1])
print('PP_difference: '+ difference_elections('pp', df_2021, df_2019)[0] +' / '+ difference_elections('pp', df_2021, df_2019)[1])


# #### **PSOE**

# In[60]:


print('PSOE_2019: '+ total_results('psoe', df_2019)[0] +' / '+ total_results('psoe', df_2019)[1])
print('PSOE_2021: '+ total_results('psoe', df_2021)[0] +' / '+ total_results('psoe', df_2021)[1])
print('PSOE_difference: '+ difference_elections('psoe', df_2021, df_2019)[0] +' / '+ difference_elections('psoe', df_2021, df_2019)[1])


# #### **Ciudadanos**

# In[61]:


print('CS_2019: '+ total_results('cs', df_2019)[0] +' / '+ total_results('cs', df_2019)[1])
print('CS_2021: '+ total_results('cs', df_2021)[0] +' / '+ total_results('cs', df_2021)[1])
print('CS_difference: '+ difference_elections('cs', df_2021, df_2019)[0] +' / '+ difference_elections('cs', df_2021, df_2019)[1])


# #### **Más Madrid**

# In[62]:


print('MAS_MADRID_2019: '+ total_results('mas_madrid', df_2019)[0] +' / '+ total_results('mas_madrid', df_2019)[1])
print('MAS_MADRID_2021: '+ total_results('mas_madrid', df_2021)[0] +' / '+ total_results('mas_madrid', df_2021)[1])
print('MAS_MADRID_difference: '+ difference_elections('mas_madrid', df_2021, df_2019)[0] +' / '+ difference_elections('mas_madrid', df_2021, df_2019)[1])


# #### **PODEMOS-IU**

# In[63]:


print('PODEMOS_IU_2019: '+ total_results('podemos_iu', df_2019)[0] +' / '+ total_results('podemos_iu', df_2019)[1])
print('PODEMOS_IU_2021: '+ total_results('podemos_iu', df_2021)[0] +' / '+ total_results('podemos_iu', df_2021)[1])
print('PODEMOS_IU_difference: '+ difference_elections('podemos_iu', df_2021, df_2019)[0] +' / '+ difference_elections('podemos_iu', df_2021, df_2019)[1])


# #### **Vox**

# In[64]:


print('VOX_2019: '+ total_results('vox', df_2019)[0] +' / '+ total_results('vox', df_2019)[1])
print('VOX_2021: '+ total_results('vox', df_2021)[0] +' / '+ total_results('vox', df_2021)[1])
print('VOX_difference: '+ difference_elections('vox', df_2021, df_2019)[0] +' / '+ difference_elections('vox', df_2021, df_2019)[1])


# Vemos claramente cómo el PP es el partido que más crece en número de votos (+910,607 votos / 22.33%), frente a Cs que es el que más disminuye su apoyo electoral (-501,023 votos / -15.84%) pasando de 631,117 votos (19.39%) a 130,094 votos (3.55%), lo que implica no llegar al 5% mínimo para obtener representación parlamentaria. Otro partido que pierde apoyos es el PSOE (-272,236 votos / -10.49%).
# 
# El resto de partidos aumenta sus apoyos: Más Madrid pasa de 474,725 votos (14.59%) a 618,285 votos (16.85%), lo que supone un incremento de 142,439 votos (2.27%), consiguiendo dar el sorpaso al PSOE dentro del bloque de la izquierda; le sigue Podemos-IU de 181,242 votos (5.57%) a 262,45 votos (7.15%), lo que supone un crecimiento en 81,208 votos (1.59%). Por último, Vox es el partido de los que obtiene representación que menos crece: 288,313 votos (8.86%) en 2019 a 333,447 votos (9.09%) en 2021, lo que supone un aumento de 44,824 votos (0.24%).

# ### 2.2.-Análisis de la distribución del voto

# A continuación vamos a hacer un análisis de la distribución del voto y cómo ha ido variando entre estas dos elecciones.
# 
# Vamos a analizar el voto conjunto de PP y PSOE, partidos que desde la Transición se han ido repartiendo a nivel nacional, autonómico y provincial la mayoría de los votos en cada elección. Esto nos permitirá ver qué apoyo representan frente a los partidos que han surgido en la última década (Podemos, Cs, Vox y Más Madrid) o que planeaban desde la Transición un nuevo modelo constitucional frente al consenso de PP y PSOE, como es el caso de IU.
# 
# Por último analizaremos la distribución del voto en torno a los ejes derecha (PP, Cs, Vox) e izquierda (PSOE, Más Madrid, Podemos-IU). Vamos a escoger esta división porque es la que siempre se ha resaltado desde los medios de comunicación y confirmado muchas veces por la política de alianzas entre los diferentes partidos, aunque hay que indicar que Cs varias veces ha prestado apoyo al PSOE frente al PP y que hay muchos analistas que indican que las políticas económicas y sociales del PSOE no se deberían considerar dentro del eje de izquierdas.

# **PP-PSOE (vs) Más Madrid-Cs-Vox-Podemos-IU** 

# In[65]:


# 2019:
pp_2019 = df_2019['pp'].sum()
psoe_2019 = df_2019['psoe'].sum()
cs_2019 = df_2019['cs'].sum()
mas_madrid_2019 = df_2019['mas_madrid'].sum()
podemos_iu_2019 = df_2019['podemos_iu'].sum()
vox_2019 = df_2019['podemos_iu'].sum()

pp_psoe_2019 = pp_2019 + psoe_2019
otros_partidos_2019 = cs_2019 + mas_madrid_2019 + podemos_iu_2019 + vox_2019
pp_psoe_percentage_2019 = (pp_psoe_2019/df_2019['votos_totales'].sum())*100
otros_partidos_percentage_2019 = (otros_partidos_2019/df_2019['votos_totales'].sum())*100

# 2021:
pp_2021 = df_2021['pp'].sum()
psoe_2021 = df_2021['psoe'].sum()
cs_2021 = df_2021['cs'].sum()
mas_madrid_2021 = df_2021['mas_madrid'].sum()
podemos_iu_2021 = df_2021['podemos_iu'].sum()
vox_2021 = df_2021['podemos_iu'].sum()

pp_psoe_2021 = pp_2021 + psoe_2021
otros_partidos_2021 = cs_2021 + mas_madrid_2021 + podemos_iu_2021 + vox_2021
pp_psoe_percentage_2021 = (pp_psoe_2021/df_2021['votos_totales'].sum())*100
otros_partidos_percentage_2021 = (otros_partidos_2021/df_2021['votos_totales'].sum())*100

# Diferencia entre 2019 y 2021
## diferencia de votos:
pp_psoe_vote_diff = pp_psoe_2021 - pp_psoe_2019
otros_partidos_vote_diff = otros_partidos_2021 - otros_partidos_2019
## diferencia de porcentajes:
pp_psoe_per_diff = pp_psoe_percentage_2021 - pp_psoe_percentage_2019
otros_per_diff = otros_partidos_percentage_2021 - otros_partidos_percentage_2019


# In[66]:


import plotly.graph_objects as go
parties=['pp_psoe', 'otros_partidos']
final_results_2019 = [
    pp_psoe_2019, 
    otros_partidos_2019,
]
final_results_2021 = [
    pp_psoe_2021, 
    otros_partidos_2021,
]

fig = go.Figure(data=[
    go.Bar(name='2021', x=parties, y=final_results_2021),
    go.Bar(name='2019', x=parties, y=final_results_2019)
])
# Change the bar mode
fig.update_layout(title='PP-PSOE (vs) Más Madrid-Cs-Vox-Podemos-IU', barmode='group')
fig.show()


# In[67]:


# 2019
pp_psoe_2019 = str("{:,}".format(pp_psoe_2019)).strip('.0')+' votos'
pp_psoe_percentage_2019 = str(round(pp_psoe_percentage_2019, 2))+' %'
otros_partidos_2019 = str("{:,}".format(otros_partidos_2019)).strip('.0')+' votos'
otros_partidos_percentage_2019 = str(round(otros_partidos_percentage_2019, 2))+' %'

# 2021
pp_psoe_2021 = str("{:,}".format(pp_psoe_2021)).strip('.0')+' votos'
pp_psoe_percentage_2021 = str(round(pp_psoe_percentage_2021, 2))+' %'
otros_partidos_2021 = str("{:,}".format(otros_partidos_2021)).strip('.0')+' votos'
otros_partidos_percentage_2021 = str(round(otros_partidos_percentage_2021, 2))+' %'

# Diferencia entre 2019 y 2021
## diferencia de votos:
pp_psoe_vote_diff = str("{:,}".format(pp_psoe_vote_diff)).strip('.0')+' votos'
otros_partidos_vote_diff = str("{:,}".format(otros_partidos_vote_diff)).strip('.0')+' votos'
## diferencia de porcentajes:
pp_psoe_per_diff = str(round(pp_psoe_per_diff, 2))+' %'
otros_per_diff = str(round(otros_per_diff, 2))+' %'


# In[68]:


print('PP_PSOE_2019: '+ pp_psoe_2019 +' / '+ pp_psoe_percentage_2019)
print('PP_PSOE_2021: '+ pp_psoe_2021 +' / '+ pp_psoe_percentage_2021)
print('PP_PSOE_DIFF: '+ pp_psoe_vote_diff +' / '+ pp_psoe_per_diff)


# In[69]:


print('OTROS_PARTIDOS_2019: '+ otros_partidos_2019 +' / '+ otros_partidos_percentage_2019)
print('OTROS_PARTIDOS_2021: '+ otros_partidos_2021 +' / '+ otros_partidos_percentage_2021)
print('OTROS_PARTIDOS_DIFF: '+ otros_partidos_vote_diff +' / '+ otros_per_diff)


# Podemos ver que de las elecciones de 2019 a las de 2021 se produce una reconfiguración de los partidos tradicionales del Régimen del 78 (PP-PSOE) al pasar de 1,606,519 votos (49.36%) en 2019 a 2,244,890 votos (61.2%) en 2021, lo que supone un aumento de 638,371 votos (11.84%) liderado por el espectacular aumento del PP.
# 
# Por otro lado, los partidos al margen de PP-PSOE pasan de acumular 1,468,326 votos (45.11%) en 2019 a 1,273,279 votos (34.71%) en 2021, lo que supone una disminución de 195,047 votos (-10.4%). El principal responsable de esta caída está en el desplome de Cs, ya que como vimos Más Madrid, Podemos-IU y Vox crecieron en apoyos. 
# 
# Se podría decir que bastante del apoyo que obtuvo Cs en 2019 pasó al PP en 2021 y que parte del apoyo del PSOE pudo haberse repartido tanto hacia la izquierda (principalmente Más Madrid) como hacia la derecha (principalmente PP).

# **Derecha(PP-Cs-Vox) (vs) Izquierda(PSOE, Más Madrid, Podemos-IU)** 

# In[70]:


# Partidos
## 2019
pp_2019 = df_2019['pp'].sum()
psoe_2019 = df_2019['psoe'].sum()
cs_2019 = df_2019['cs'].sum()
mas_madrid_2019 = df_2019['mas_madrid'].sum()
podemos_iu_2019 = df_2019['podemos_iu'].sum()
vox_2019 = df_2019['podemos_iu'].sum()
## 2021
pp_2021 = df_2021['pp'].sum()
psoe_2021 = df_2021['psoe'].sum()
cs_2021 = df_2021['cs'].sum()
mas_madrid_2021 = df_2021['mas_madrid'].sum()
podemos_iu_2021 = df_2021['podemos_iu'].sum()
vox_2021 = df_2021['podemos_iu'].sum()

# 2019:
## Derecha:
right_votes_2019 = pp_2019 + cs_2019 + vox_2019
right_percentage_2019 = (right_votes_2019/df_2019['votos_totales'].sum())*100
## Izquierda:
left_votes_2019 = psoe_2019 + mas_madrid_2019 + podemos_iu_2019
left_percentage_2019 = (left_votes_2019/df_2019['votos_totales'].sum())*100
## Derecha-Izquierda diferencia:
right_left_vote_diff_2019 = right_votes_2019 - left_votes_2019
right_left_perc_diff_2019 = right_percentage_2019 - left_percentage_2019

# 2021:
## Derecha:
right_votes_2021 = pp_2021 + cs_2021 + vox_2021
right_percentage_2021 = (right_votes_2021/df_2021['votos_totales'].sum())*100
## Izquierda:
left_votes_2021 = psoe_2021 + mas_madrid_2021 + podemos_iu_2021
left_percentage_2021 = (left_votes_2021/df_2021['votos_totales'].sum())*100
## Derecha-Izquierda diferencia:
right_left_vote_diff_2021 = right_votes_2021 - left_votes_2021
right_left_perc_diff_2021 = right_percentage_2021 - left_percentage_2021

# Diferencia entre 2019 y 2021:
## diferencia de votos
right_vote_diff = right_votes_2021 - right_votes_2019
left_vote_diff = left_votes_2021 - left_votes_2019
## diferencia de porcentajes
right_percentage_diff = right_percentage_2021 - right_percentage_2019
left_percentage_diff = left_percentage_2021 - left_percentage_2019


# In[71]:


import plotly.graph_objects as go
parties=['derecha', 'izquierda']
final_results_2019 = [
    right_votes_2019, 
    left_votes_2019,
]
final_results_2021 = [
    right_votes_2021, 
    left_votes_2021,
]

fig = go.Figure(data=[
    go.Bar(name='2021', x=parties, y=final_results_2021),
    go.Bar(name='2019', x=parties, y=final_results_2019)
])
# Change the bar mode
fig.update_layout(title='Derecha (vs) Izquierda', barmode='group')
fig.show()


# In[72]:


# 2019
## Derecha:
right_votes_2019 = str("{:,}".format(right_votes_2019)).strip('.0')+' votos'
right_percentage_2019 = str(round(right_percentage_2019, 2))+' %'
## Izquierda:
left_votes_2019 = str("{:,}".format(left_votes_2019)).strip('.0')+' votos'
left_percentage_2019 = str(round(left_percentage_2019, 2))+' %'
## Derecha-Izquierda diferencia
right_left_vote_diff_2019 = str("{:,}".format(right_left_vote_diff_2019)).strip('.0')+' votos'
right_left_perc_diff_2019 = str(round(right_left_perc_diff_2019, 2))+' %'

# 2021
## Derecha:
right_votes_2021 = str("{:,}".format(right_votes_2021)).strip('.0')+' votos'
right_percentage_2021 = str(round(right_percentage_2021, 2))+' %'
## Izquierda:
left_votes_2021 = str("{:,}".format(left_votes_2021)).strip('.0')+' votos'
left_percentage_2021 = str(round(left_percentage_2021, 2))+' %'
## Derecha-Izquierda diferencia
right_left_vote_diff_2021 = str("{:,}".format(right_left_vote_diff_2021)).strip('.0')+' votos'
right_left_perc_diff_2021 = str(round(right_left_perc_diff_2021, 2))+' %'

# Diferencia entre 2019-2021
## diferencia de votos
right_vote_diff = str("{:,}".format(right_vote_diff)).strip('.0')+' votos'
left_vote_diff = str("{:,}".format(left_vote_diff)).strip('.0')+' votos'
## diferencia de porcentajes
right_percentage_diff = str(round(right_percentage_diff, 2))+' %'
left_percentage_diff = str(round(left_percentage_diff, 2))+' %'


# In[73]:


print('RIGHT_2019: '+ right_votes_2019 +' / '+ right_percentage_2019)
print('RIGHT_2021: '+ right_votes_2021 +' / '+ right_percentage_2021)
print('RIGHT_DIFF: '+ right_vote_diff +' / '+ right_percentage_diff)


# In[74]:


print('LEFT_2019: '+ left_votes_2019 +' / '+ left_percentage_2019)
print('LEFT_2021: '+ left_votes_2021 +' / '+ left_percentage_2021)
print('LEFT_DIFF: '+ left_vote_diff +' / '+ left_percentage_diff)


# In[75]:


print('RIGHT_LEFT_DIFF_2019: '+ right_left_vote_diff_2019 +' / '+ right_left_perc_diff_2019)
print('RIGHT_LEFT_DIFF_2021: '+ right_left_vote_diff_2021 +' / '+ right_left_perc_diff_2021)


# Podemos decir que el bloque de la derecha aumenta en 490,792 votos (8.07%) en 2021, mientras que el bloque de la izquierda cae en 47,468 votos (-6.63%). En 2019, la derecha representaba el 47.11% (1,533,343 votos) mientras que la izquierda un 47.36% (1,541,502 votos), prácticamente empatados con una diferencia del 0.25% (8,159 votos) a favor de la izquierda. En cambio en el 2021 la derecha representa un 55.18% (2,024,135 votos) frente al 40.73% (1,494,034 votos), una diferencia del 14.45% (530,101 votos) a favor de la derecha.
# 
# El aumento de la derecha está liderado por el crecimiento del PP, pero se ve atenuado por la fuerte caída de Cs y el poco crecimiento de Vox. Mientras tanto en la izquierda la caída se debe al desplome del PSOE principalmente, pero atenuado por los crecimientos de Más Madrid y Podemos-IU.

# ### 2.3.-Distribución espacial de los resultados

# A continuación vamos a hacer representaciones espaciales sobre la distribución del voto por los municipios de Madrid. Se van a seguir comparativas parecidas a las del apartado anterior: PP (vs) PSOE, PP-PSOE (vs) Otros Partidos, Derecha (vs) Izquierda, comparación del PP con el resto de partidos.
# 
# Para la construcción de mapas interactivos que permitieran mostrar la distribución del voto en cada municipio se ha utilizado la librería BokehJS y los datos geoespaciales de nuestros dataframes (columna 'geometry').

# In[76]:


# funcion que te devuelve nº de municipios donde gana un partido (party_1) sobre otro (party_2):
def won_municipalities(party_1, party_2, df):
    municipalities = []
    municipalities = df['municipio'][df[party_1] > df[party_2]].count()
    
    return municipalities


# **PP (vs) PSOE** 

# In[77]:


# añado nuevas columnas
df_2019["pp_share"] = df_2019["pp"] / df_2019["votos_totales"]
df_2019["rel_pp_share"] = df_2019["pp"] / (df_2019["pp"]+df_2019["psoe"])
df_2019["psoe_share"] = df_2019["psoe"] / df_2019["votos_totales"]
df_2019["rel_psoe_share"] = df_2019["psoe"] / (df_2019["pp"]+df_2019["psoe"])


# In[78]:


from geopandas import GeoDataFrame

# result
from bokeh.io import output_notebook
from bokeh.plotting import figure, ColumnDataSource
from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, HoverTool
from bokeh.palettes import brewer
output_notebook()
import json

result = GeoDataFrame(df_2019)
wi_geojson=GeoJSONDataSource(geojson=result.to_json())

color_mapper = LinearColorMapper(palette = brewer['RdBu'][10], low = 0, high = 1)
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,
                     border_line_color=None,location = (0,0), orientation = 'horizontal')
hover = HoverTool(tooltips = [ ('municipio','@municipio'),('pp', '@pp'),
                               ('psoe','@psoe'),
                               ('votos_totales','@votos_totales')])
p = figure(title="Elecciones Madrid 2019: PP (vs) PSOE", tools=[hover])
p.patches("xs","ys",source=wi_geojson,
          fill_color = {'field' :'rel_psoe_share', 'transform' : color_mapper})
p.add_layout(color_bar, 'below')
show(p)


# In[79]:


# añado nuevas columnas
df_2021["pp_share"] = df_2021["pp"] / df_2021["votos_totales"]
df_2021["rel_pp_share"] = df_2021["pp"] / (df_2021["pp"]+df_2021["psoe"])
df_2021["psoe_share"] = df_2021["psoe"] / df_2021["votos_totales"]
df_2021["rel_psoe_share"] = df_2021["psoe"] / (df_2021["pp"]+df_2021["psoe"])


# In[80]:


result = GeoDataFrame(df_2021)
wi_geojson=GeoJSONDataSource(geojson=result.to_json())

color_mapper = LinearColorMapper(palette = brewer['RdBu'][10], low = 0, high = 1)
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,
                     border_line_color=None,location = (0,0), orientation = 'horizontal')
hover = HoverTool(tooltips = [ ('municipio','@municipio'),('pp', '@pp'),
                               ('psoe','@psoe'),
                               ('votos_totales','@votos_totales')])
p = figure(title="Elecciones Madrid 2021: PP (vs) PSOE", tools=[hover])
p.patches("xs","ys",source=wi_geojson,
          fill_color = {'field' :'rel_psoe_share', 'transform' : color_mapper})
p.add_layout(color_bar, 'below')
show(p)


# In[81]:


# municipios ganados por el PP al PSOE en 2019
won_municipalities('pp', 'psoe', df_2019)


# In[82]:


# municipios ganados por el PSOE al PP en 2019
won_municipalities('psoe', 'pp', df_2019)


# In[83]:


# municipios ganados por el PP al PSOE en 2021
won_municipalities('pp', 'psoe', df_2021)


# In[84]:


# municipios ganados por el PSOE al PP en 2021
won_municipalities('psoe', 'pp', df_2021)


# Se puede apreciar la gran debacle del PSOE al pasar de 114 municipios en los que obtuvo más apoyos sobre el PP en 2019 a solo 2 en 2021, mientras que el PP pasa de 63 municipios en 2019 a 176 en 2021. En el municipio de Navarredonda y San Mamés se obtiene un empate técnico entre ambos partidos.

# **PP-PSOE (vs) Otros Partidos** 

# In[85]:


# 2019
df_2019 = df_2019.fillna(0)
df_2019['pp_psoe'] = df_2019["pp"] + df_2019["psoe"]
df_2019['otros_partidos'] = df_2019["mas_madrid"] + df_2019["cs"] + df_2019["podemos_iu"] + df_2019["vox"]

df_2019["pp_psoe_share"] = df_2019["pp_psoe"] / df_2019["votos_totales"]
df_2019["rel_pp_psoe_share"] = df_2019["pp_psoe"] / (df_2019["pp"]+df_2019["otros_partidos"])
df_2019["otros_partidos_share"] = df_2019["otros_partidos"] / df_2019["votos_totales"]
df_2019["rel_otros_partidos_share"] = df_2019["otros_partidos"] / (df_2019["pp_psoe"]+df_2019["otros_partidos"])

# 2021
df_2021 = df_2021.fillna(0)
df_2021['pp_psoe'] = df_2021["pp"] + df_2021["psoe"]
df_2021['otros_partidos'] = df_2021["mas_madrid"] + df_2021["cs"] + df_2021["podemos_iu"] + df_2021["vox"]

df_2021["pp_psoe_share"] = df_2021["pp_psoe"] / df_2021["votos_totales"]
df_2021["rel_pp_psoe_share"] = df_2021["pp_psoe"] / (df_2021["pp"]+df_2021["otros_partidos"])
df_2021["otros_partidos_share"] = df_2021["otros_partidos"] / df_2021["votos_totales"]
df_2021["rel_otros_partidos_share"] = df_2021["otros_partidos"] / (df_2021["pp_psoe"]+df_2021["otros_partidos"])


# In[86]:


result = GeoDataFrame(df_2019)
wi_geojson=GeoJSONDataSource(geojson=result.to_json())

color_mapper = LinearColorMapper(palette = brewer['RdBu'][10], low = 0, high = 1)
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,
                     border_line_color=None,location = (0,0), orientation = 'horizontal')
hover = HoverTool(tooltips = [ ('municipio','@municipio'),('pp_psoe', '@pp_psoe'),
                               ('otros_partidos','@otros_partidos'),
                               ('votos_totales','@votos_totales')])
p = figure(title="Elecciones Madrid 2019: PP-PSOE (vs) Otros Partidos", tools=[hover])
p.patches("xs","ys",source=wi_geojson,
          fill_color = {'field' :'rel_otros_partidos_share', 'transform' : color_mapper})
p.add_layout(color_bar, 'below')
show(p)


# In[87]:


result = GeoDataFrame(df_2021)
wi_geojson=GeoJSONDataSource(geojson=result.to_json())

color_mapper = LinearColorMapper(palette = brewer['RdBu'][10], low = 0, high = 1)
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,
                     border_line_color=None,location = (0,0), orientation = 'horizontal')
hover = HoverTool(tooltips = [ ('municipio','@municipio'),('pp_psoe', '@pp_psoe'),
                               ('otros_partidos','@otros_partidos'),
                               ('votos_totales','@votos_totales')])
p = figure(title="Elecciones Madrid 2021: PP-PSOE (vs) Otros Partidos", tools=[hover])
p.patches("xs","ys",source=wi_geojson,
          fill_color = {'field' :'rel_otros_partidos_share', 'transform' : color_mapper})
p.add_layout(color_bar, 'below')
show(p)


# In[88]:


# municipios ganados por PP-PSOE al resto de partidos en 2019
won_municipalities('pp_psoe', 'otros_partidos', df_2019)


# In[89]:


# municipios ganados por el resto de partidos a PP-PSOE en 2019
won_municipalities('otros_partidos', 'pp_psoe', df_2019)


# In[90]:


# municipios ganados por PP-PSOE al resto de partidos en 2021
won_municipalities('pp_psoe', 'otros_partidos', df_2021)


# In[91]:


# municipios ganados por el resto de partidos a PP-PSOE en 2021
won_municipalities('otros_partidos', 'pp_psoe', df_2021)


# Se ve la reconfiguración del eje PP-PSOE frente a otros partidos (Cs, Vox, Podemos-IU y Más Madrid), ya que se pasa de 121 municipios donde obtienen mayoría frente a 58 a 176 municipios frente a 3.

# **Derecha (vs) Izquierda** 

# In[92]:


# 2019
df_2019['derecha'] = df_2019["pp"] + df_2019["cs"] + df_2019["vox"]
df_2019['izquierda'] = df_2019["psoe"]+ df_2019["mas_madrid"] + df_2019["podemos_iu"] 

df_2019["derecha_share"] = df_2019["derecha"] / df_2019["votos_totales"]
df_2019["rel_derecha_share"] = df_2019["derecha"] / (df_2019["derecha"]+df_2019["izquierda"])
df_2019["izquierda_share"] = df_2019["izquierda"] / df_2019["votos_totales"]
df_2019["rel_izquierda_share"] = df_2019["izquierda"] / (df_2019["derecha"]+df_2019["izquierda"])

# 2021
df_2021['derecha'] = df_2021["pp"] + df_2021["cs"] + df_2021["vox"]
df_2021['izquierda'] = df_2021["psoe"]+ df_2021["mas_madrid"] + df_2021["podemos_iu"] 

df_2021["derecha_share"] = df_2021["derecha"] / df_2021["votos_totales"]
df_2021["rel_derecha_share"] = df_2021["derecha"] / (df_2021["derecha"]+df_2021["izquierda"])
df_2021["izquierda_share"] = df_2021["izquierda"] / df_2021["votos_totales"]
df_2021["rel_izquierda_share"] = df_2021["izquierda"] / (df_2021["derecha"]+df_2021["izquierda"])


# In[93]:


result = GeoDataFrame(df_2019)
wi_geojson=GeoJSONDataSource(geojson=result.to_json())

color_mapper = LinearColorMapper(palette = brewer['RdBu'][10], low = 0, high = 1)
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,
                     border_line_color=None,location = (0,0), orientation = 'horizontal')
hover = HoverTool(tooltips = [ ('municipio','@municipio'),('derecha', '@derecha'),
                               ('izquierda','@izquierda'),
                               ('votos_totales','@votos_totales')])
p = figure(title="Elecciones Madrid 2019: Derecha (vs) Izquierda", tools=[hover])
p.patches("xs","ys",source=wi_geojson,
          fill_color = {'field' :'rel_izquierda_share', 'transform' : color_mapper})
p.add_layout(color_bar, 'below')
show(p)


# In[94]:


result = GeoDataFrame(df_2021)
wi_geojson=GeoJSONDataSource(geojson=result.to_json())

color_mapper = LinearColorMapper(palette = brewer['RdBu'][10], low = 0, high = 1)
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,
                     border_line_color=None,location = (0,0), orientation = 'horizontal')
hover = HoverTool(tooltips = [ ('municipio','@municipio'),('derecha', '@derecha'),
                               ('izquierda','@izquierda'),
                               ('votos_totales','@votos_totales')])
p = figure(title="Elecciones Madrid 2021: Derecha (vs) Izquierda", tools=[hover])
p.patches("xs","ys",source=wi_geojson,
          fill_color = {'field' :'rel_izquierda_share', 'transform' : color_mapper})
p.add_layout(color_bar, 'below')
show(p)


# In[95]:


# municipios ganados por el eje de la derecha al eje de la izquierda en 2019
won_municipalities('derecha', 'izquierda', df_2019)


# In[96]:


# municipios ganados por el eje de la izquierda al eje de la derecha en 2019
won_municipalities('izquierda', 'derecha', df_2019)


# In[97]:


# municipios ganados por el eje de la derecha al eje de la izquierda en 2021
won_municipalities('derecha', 'izquierda', df_2021)


# In[98]:


# municipios ganados por el eje de la izquierda al eje de la derecha en 2021
won_municipalities('izquierda', 'derecha', df_2021)


# Se puede apreciar el gran avance general de la derecha en la Comunidad de Madrid: pasa de 127 municipios en 2019 a 159 en 2021; mientras que la izquierda pasa de 51 a solo 19 municipios.

# **PP (vs) Más Madrid** 

# In[99]:


# 2019
df_2019["pp_share"] = df_2019["pp"] / df_2019["votos_totales"]
df_2019["rel_pp_share"] = df_2019["pp"] / (df_2019["pp"]+df_2019["mas_madrid"])
df_2019["mas_madrid_share"] = df_2019["mas_madrid"] / df_2019["votos_totales"]
df_2019["rel_mas_madrid_share"] = df_2019["mas_madrid"] / (df_2019["pp"]+df_2019["mas_madrid"])

# 2021
df_2021["pp_share"] = df_2021["pp"] / df_2021["votos_totales"]
df_2021["rel_pp_share"] = df_2021["pp"] / (df_2021["pp"]+df_2021["mas_madrid"])
df_2021["mas_madrid_share"] = df_2021["mas_madrid"] / df_2021["votos_totales"]
df_2021["rel_mas_madrid_share"] = df_2021["mas_madrid"] / (df_2021["pp"]+df_2021["mas_madrid"])


# In[100]:


result = GeoDataFrame(df_2019)
wi_geojson=GeoJSONDataSource(geojson=result.to_json())

color_mapper = LinearColorMapper(palette = brewer['RdBu'][10], low = 0, high = 1)
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,
                     border_line_color=None,location = (0,0), orientation = 'horizontal')
hover = HoverTool(tooltips = [ ('municipio','@municipio'),('pp', '@pp'),
                               ('mas_madrid','@mas_madrid'),
                               ('votos_totales','@votos_totales')])
p = figure(title="Elecciones Madrid 2019: PP (vs) Más Madrid", tools=[hover])
p.patches("xs","ys",source=wi_geojson,
          fill_color = {'field' :'rel_mas_madrid_share', 'transform' : color_mapper})
p.add_layout(color_bar, 'below')
show(p)


# In[101]:


result = GeoDataFrame(df_2021)
wi_geojson=GeoJSONDataSource(geojson=result.to_json())

color_mapper = LinearColorMapper(palette = brewer['RdBu'][10], low = 0, high = 1)
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,
                     border_line_color=None,location = (0,0), orientation = 'horizontal')
hover = HoverTool(tooltips = [ ('municipio','@municipio'),('pp', '@pp'),
                               ('mas_madrid','@mas_madrid'),
                               ('votos_totales','@votos_totales')])
p = figure(title="Elecciones Madrid 2021: PP (vs) Más Madrid", tools=[hover])
p.patches("xs","ys",source=wi_geojson,
          fill_color = {'field' :'rel_mas_madrid_share', 'transform' : color_mapper})
p.add_layout(color_bar, 'below')
show(p)


# In[102]:


# municipios ganados por el PP a Más Madrid en 2019
won_municipalities('pp', 'mas_madrid', df_2019)


# In[103]:


# municipios ganados por Más Madrid a el PP en 2019
won_municipalities('mas_madrid', 'pp', df_2019)


# In[104]:


# municipios ganados por el PP a Más Madrid en 2019
won_municipalities('pp', 'mas_madrid', df_2021)


# In[105]:


# municipios ganados por Más Madrid a el PP en 2019
won_municipalities('mas_madrid', 'pp', df_2021)


# Más Madrid, que fue el partido dentro del eje de izquierdas y que consiguió dar el sorpaso al PSOE, pasó de tener 10 municipios donde sacó más votos que el PP en las elecciones de 2019 a ninguno en las elecciones de 2021. Por lo tanto, a pesar del sorpaso, el PP mantiene el tipo frente a todos los partidos de izquierdas.
# 
# Es importante destacar cómo Más Madrid ha conseguido tener su caladero de votos en los feudos tradicionales del PSOE (sureste del municipio de Madrid: Rivas, Coslada, San Fernando, Fuenlabrada, Getafe, Parla, Pinto y Mejorada del Campo).

# **Más Madrid (vs) Podemos-IU** 
# 
# Por último vamos a ver dentro del eje de izquierdas la distribución del voto a la izquierda del PSOE entre Podemos-IU y Más Madrid.

# In[106]:


# 2019
df_2019["podemos_iu_share"] = df_2019["podemos_iu"] / df_2019["votos_totales"]
df_2019["rel_podemos_iu_share"] = df_2019["podemos_iu"] / (df_2019["podemos_iu"]+df_2019["mas_madrid"])
df_2019["mas_madrid_share"] = df_2019["mas_madrid"] / df_2019["votos_totales"]
df_2019["rel_mas_madrid_share"] = df_2019["mas_madrid"] / (df_2019["podemos_iu"]+df_2019["mas_madrid"])

# 2021
df_2021["podemos_iu_share"] = df_2021["podemos_iu"] / df_2021["votos_totales"]
df_2021["rel_podemos_iu_share"] = df_2021["podemos_iu"] / (df_2021["podemos_iu"]+df_2021["mas_madrid"])
df_2021["mas_madrid_share"] = df_2021["mas_madrid"] / df_2021["votos_totales"]
df_2021["rel_mas_madrid_share"] = df_2021["mas_madrid"] / (df_2021["podemos_iu"]+df_2021["mas_madrid"])


# In[107]:


result = GeoDataFrame(df_2019)
wi_geojson=GeoJSONDataSource(geojson=result.to_json())

color_mapper = LinearColorMapper(palette = brewer['RdBu'][10], low = 0, high = 1)
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,
                     border_line_color=None,location = (0,0), orientation = 'horizontal')
hover = HoverTool(tooltips = [ ('municipio','@municipio'),('podemos_iu', '@podemos_iu'),
                               ('mas_madrid','@mas_madrid'),
                               ('votos_totales','@votos_totales')])
p = figure(title="Elecciones Madrid 2019: Más Madrid (vs) Podemos-IU", tools=[hover])
p.patches("xs","ys",source=wi_geojson,
          fill_color = {'field' :'rel_mas_madrid_share', 'transform' : color_mapper})
p.add_layout(color_bar, 'below')
show(p)


# In[108]:


result = GeoDataFrame(df_2021)
wi_geojson=GeoJSONDataSource(geojson=result.to_json())

color_mapper = LinearColorMapper(palette = brewer['RdBu'][10], low = 0, high = 1)
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,
                     border_line_color=None,location = (0,0), orientation = 'horizontal')
hover = HoverTool(tooltips = [ ('municipio','@municipio'),('podemos_iu', '@podemos_iu'),
                               ('mas_madrid','@mas_madrid'),
                               ('votos_totales','@votos_totales')])
p = figure(title="Elecciones Madrid 2021: Más Madrid (vs) Podemos-IU", tools=[hover])
p.patches("xs","ys",source=wi_geojson,
          fill_color = {'field' :'rel_mas_madrid_share', 'transform' : color_mapper})
p.add_layout(color_bar, 'below')
show(p)


# In[109]:


# municipios ganados por Más Madrid a Podemos-IU en 2019
won_municipalities('mas_madrid', 'podemos_iu', df_2019)


# In[110]:


# municipios ganados por Podemos-IU a Más Madrid en 2019
won_municipalities('podemos_iu', 'mas_madrid', df_2019)


# In[111]:


# municipios ganados por Más Madrid a Podemos-IU en 2021
won_municipalities('mas_madrid', 'podemos_iu', df_2021)


# In[112]:


# municipios ganados por Podemos-IU a Más Madrid en 2021
won_municipalities('podemos_iu', 'mas_madrid', df_2021)


# Vemos cómo el apoyo a Más Madrid crece entre las dos elecciones con respecto a Podemos-IU, ya que pasa de 160 municipios donde suma más votos frente a 17 a 173 contra 6. Esto puede reflejar que el ser parte del Gobierno a nivel nacional le ha pasado factura a Podemos-IU.
# 
# Destaca cómo Más Madrid es la opción favorita frente a Podemos-IU sobre todo en los principales núcleos urbanos, mientras que Podemos-IU consigue superar a Más Madrid en pequeños municipios alejados del municipio de Madrid, sobre todo en el norte.

# ### 2.4.-Análisis de la abstención

# A continuación vamos a analizar la evolución de la abstención entre las 2 elecciones para ver hasta qué grado pudo influir entre un resultado u otro.

# Definimos unas funciones para obtener la abstención electoral en votos y porcentajes entre las dos elecciones:

# In[113]:


def electoral_abstention(df_year):
    abstention_total_votes = df_year['abstencion'].sum()
    abstention_total_percentage = (df_year['abstencion'].sum()/df_year['votos_totales'].sum())*100
    
    abstention_total_votes = str("{:,}".format(abstention_total_votes)).strip('.0')+' votos'
    abstention_total_percentage = str(round(abstention_total_percentage, 2))+' %'
    
    return [abstention_total_votes, abstention_total_percentage]


# In[114]:


def dif_electoral_abstention(df_year_1, df_year_2):
    abstention_total_votes_1 = df_year_1['abstencion'].sum()
    abstention_total_percentage_1 = (df_year_1['abstencion'].sum()/df_year_1['votos_totales'].sum())*100
    
    abstention_total_votes_2 = df_year_2['abstencion'].sum()
    abstention_total_percentage_2 = (df_year_2['abstencion'].sum()/df_year_2['votos_totales'].sum())*100
    
    diff_abstention_votes = abstention_total_votes_1 - abstention_total_votes_2
    diff_abstention_percentage = abstention_total_percentage_1 - abstention_total_percentage_2
    
    abstencion_total_votes = str("{:,}".format(diff_abstention_votes)).strip('.0')+' votos'
    abstention_total_percentage = str(round(diff_abstention_percentage, 2))+' %'
    
    return [abstencion_total_votes, abstention_total_percentage]


# In[115]:


print('Abstención 2019: '+ electoral_abstention(df_2019)[0] +' / '+ electoral_abstention(df_2019)[1])
print('Abstención 2021: '+ electoral_abstention(df_2021)[0] +' / '+ electoral_abstention(df_2021)[1])
print('Diferencia 2021-2019: '+ dif_electoral_abstention(df_2021, df_2019)[0] +' / '+ dif_electoral_abstention(df_2021, df_2019)[1])


# Podemos ver cómo la abstención pasa de representar el 46.89% del total en las elecciones del 2019 (1,516,826 votos) a el 31.15% (1,135,201 votos), lo que supone una caída porcentual del 15.74% (-381,625 votos). Usualmente se atribuyen una menor a abstención a una mayor movilización de la izquierda, pero aquí vemos lo contrario: en 2019 obtiene más votos el candidato del PSOE, mientras que en 2021 la candidata del PP.

# #### Distribución espacial de la abstención

# Vamos a representar cómo se distribuye la abstención sobre el mapa y analizaremos qué partido sale beneficiado de la reducción/aumento de la abstención en cada municipio:

# In[116]:


# 2019
df_2019["abstencion_share"] = df_2019["abstencion"] / df_2019["votos_totales"]
df_2019["rel_abstencion_share"] = df_2019["abstencion"] / (df_2019["abstencion"]+df_2019["votos_totales"])
df_2019["votos_totales_share"] = df_2019["votos_totales"] / df_2019["votos_totales"]
df_2019["rel_votos_totales_share"] = df_2019["votos_totales"] / (df_2019["abstencion"]+df_2019["votos_totales"])

# 2021
df_2021["abstencion_share"] = df_2021["abstencion"] / df_2021["votos_totales"]
df_2021["rel_abstencion_share"] = df_2021["abstencion"] / (df_2021["abstencion"]+df_2021["votos_totales"])
df_2021["votos_totales_share"] = df_2021["votos_totales"] / df_2021["votos_totales"]
df_2021["rel_votos_totales_share"] = df_2021["votos_totales"] / (df_2021["abstencion"]+df_2021["votos_totales"])


# In[117]:


result = GeoDataFrame(df_2019)
wi_geojson=GeoJSONDataSource(geojson=result.to_json())

color_mapper = LinearColorMapper(palette = brewer['RdBu'][10], low = 0, high = 1)
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,
                     border_line_color=None,location = (0,0), orientation = 'horizontal')
hover = HoverTool(tooltips = [ ('municipio','@municipio'),('votos_totales', '@votos_totales'),
                               ('abstencion','@abstencion'),
                               ('votos_totales','@votos_totales')])
p = figure(title="Elecciones Madrid 2019: distribución de la abstención", tools=[hover])
p.patches("xs","ys",source=wi_geojson,
          fill_color = {'field' :'rel_votos_totales_share', 'transform' : color_mapper})
p.add_layout(color_bar, 'below')
show(p)


# In[118]:


result = GeoDataFrame(df_2021)
wi_geojson=GeoJSONDataSource(geojson=result.to_json())

color_mapper = LinearColorMapper(palette = brewer['RdBu'][10], low = 0, high = 1)
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,
                     border_line_color=None,location = (0,0), orientation = 'horizontal')
hover = HoverTool(tooltips = [ ('municipio','@municipio'),('votos_totales', '@votos_totales'),
                               ('abstencion','@abstencion'),
                               ('votos_totales','@votos_totales')])
p = figure(title="Elecciones Madrid 2021: distribución de la abstención", tools=[hover])
p.patches("xs","ys",source=wi_geojson,
          fill_color = {'field' :'rel_votos_totales_share', 'transform' : color_mapper})
p.add_layout(color_bar, 'below')
show(p)


# Podemos ver en 2019 cómo la abstención se centra sobre todo en grandes núcleos de población (municipio de Madrid y contiguos), así como en municipios del sur (p.ej. Colmenar de Oreja). Contrasta la alta participación de los pequeños municipios del norte de Madrid, Valdemaqueda, Valdaracete, Santorcaz y Olmeda de las Fuentes.
# 
# En cambio en 2021 podemos ver cómo la abstención general se reduce en los grandes núcleos de población, mientras se reduce en algunos municipios del norte.

# In[119]:


import pandas as pd

df_abstenciones = pd.DataFrame()
df_abstenciones['municipio'] = df_2021['municipio']
df_abstenciones['votos_totales_2019'] = df_2019['votos_totales']
df_abstenciones['votos_totales_2021'] = df_2021['votos_totales']
df_abstenciones['abstencion_2019'] = df_2019['abstencion']
df_abstenciones['abstencion_2021'] = df_2021['abstencion']
df_abstenciones['dif_abstencion_votos'] = df_abstenciones['abstencion_2021'] - df_abstenciones['abstencion_2019']
df_abstenciones['dif_abstencion_porcentaje'] = df_2021['abstencion_porcentaje'] - df_2019['abstencion_porcentaje']


# In[120]:


df_abstenciones.info()


# In[121]:


# donde más crece la abstención en 2021 con respecto a 2019:
df_abstenciones.nlargest(15, ['dif_abstencion_porcentaje'])


# In[122]:


# donde más se reduce la abstención en 2021 con respecto a 2019:
df_abstenciones.nsmallest(15, ['dif_abstencion_porcentaje'])


# Como podemos confirmar con la creación de este nuevo dataframe que resume la abstención entre las elecciones de 2019 y 2021: la abstención crece más en pequeños municipios y más en municipios que ya empiezan a tener una población considerable.

# ## 3.- Conclusiones

# Después de haber analizado los resultados de las elecciones de 2019 y 2021 podemos concluir lo siguiente:
# * El PP es el indiscutible ganador de las elecciones de 2021 al ser el partido que más crece de todos los que consiguieron representación parlamentaria. La estrategia de Isabel Díaz Ayuso de anular a nivel interno a la oposición y convertirse a nivel nacional en el principal agente de oposición a la gestión de la pandemia por parte del Gobierno nacional, por encima incluso del líder a nivel nacional del PP, le ha reportado grandes beneficios.
# 
# 
# 
# * El PSOE es el gran perdedor no solo por la pérdida de votos, sino también por la pérdida de apoyos tradicionales entre su electorado que ha optado por el voto castigo hacia el PP o la búsqueda de una nueva opción: Más Madrid. Muchos analistas coinciden en que la pérdida de apoyo viene de una falta de liderazgo por parte de Ángel Gabilondo frente a Isabel Díaz Ayuso, así como ser el partido a nivel nacional que ha gestionado la pandemia de COVID-19.
# 
# 
# 
# * Ciudadanos sufre las consecuencias de formar parte de un gobierno de coalición donde no han sabido hacer frente al liderazgo de Isabel Díaz Ayuso, así como las consecuencias de una política errática a nivel nacional en la que no ha podido hacer frente al PP y al auge de Vox en sus campañas contra el Gobierno nacional en diferentes problemáticas nacionales (Cataluña, COVID-19, etc).
# 
# 
# 
# * Más Madrid es el partido de izquierdas que cosecha más éxitos al aumentar su base electoral y conseguir dar el deseado sorpaso al PSOE que partidos como Podemos-IU han intentado y nunca han conseguido. Se ha beneficiado de ser un partido de izquierdas que no forma parte del Gobierno nacional de PSOE-UnidasPodemos. Por último, desde diferentes analistas se ha dicho que su candidata, Mónica García, era la candidata perfecta para el momento histórico que se vivía: una profesional sanitaria en el contexto de la pandemia de COVID-19.
# 
# 
# 
# * Podemos-IU consigue aumentar mínimamente sus apoyos electorales por la participación de su líder fundador como candidato, Pablo Iglesias Turrión. Indudablemente ha conseguido movilizar a su base electoral para recuperar apoyos perdidos, ya que todas las encuestas indicaban que podían incluso desaparecer como Cs, pero aún así cabe preguntarse si su candidatura movilizó también el voto contra la izquierda a nivel general.
# 
# 
# 
# * Vox a pesar de que en las pasadas elecciones de 2019 mostraron un fuerte músculo para poder crecer y situarse en las instituciones madrileñas, tampoco han podido escapar del liderazgo de Isabel Díaz Ayuso. Consiguen mantener su base de apoyo, pero no consiguen hacerla crecer ni un 1%.
# 
# 
# 
# * En cuanto a la participación, las elecciones de 2021 han desmitificado que una participación alta sea sinónimo de un mayor apoyo hacia la izquierda vistos los resultados. Se podría decir que esta mayor movilización se ha debido a los liderazgos principales de Isabel Díaz Ayuso y Pablo Iglesias Turrión, que han movilizado el voto a uno y otro lado.

# In[124]:


get_ipython().system('pip list')


# In[ ]:




