"""Panel de control de anuncios de venta de coches en EE. UU.

Aplicación web construida con Streamlit y Plotly para explorar de forma
interactiva un conjunto de 51 525 anuncios de vehículos de segunda mano.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

# Paleta categórica validada para daltonismo (separación CVD suficiente)
AZUL, NARANJA, MORADO = '#3b6fd4', '#e08b2f', '#8a5cd0'

st.set_page_config(page_title='Anuncios de coches en EE. UU.',
                   page_icon='🚗',
                   layout='wide')


@st.cache_data
def cargar_datos():
    """Lee el CSV y aplica una limpieza mínima.

    Se guarda en caché para que los filtros de la interfaz no releean
    el archivo en cada interacción.
    """
    datos = pd.read_csv('vehicles_us.csv')

    # is_4wd solo contiene 1.0 o ausente: el ausente significa "no es 4x4"
    datos['is_4wd'] = datos['is_4wd'].fillna(0).astype(int)

    # El color sin declarar es información que falta, no un color
    datos['paint_color'] = datos['paint_color'].fillna('unknown')

    # La antigüedad del anuncio se calcula desde el año de publicación
    datos['date_posted'] = pd.to_datetime(datos['date_posted'])
    datos['model_year'] = datos['model_year'].fillna(
        datos.groupby('model')['model_year'].transform('median'))
    datos['marca'] = datos['model'].str.split().str[0]

    return datos


car_data = cargar_datos()

# ----------------------------------------------------------------------
# Encabezado
# ----------------------------------------------------------------------
st.header('🚗 Anuncios de venta de coches en EE. UU.')

st.write("""
Panel interactivo para explorar **{:,} anuncios** de vehículos de segunda mano.
Usa los filtros de la barra lateral para acotar la muestra y marca las casillas
para generar cada gráfico.
""".format(len(car_data)).replace(',', ' '))

# ----------------------------------------------------------------------
# Filtros
# ----------------------------------------------------------------------
st.sidebar.header('Filtros')

tipos = sorted(car_data['type'].unique())
tipos_sel = st.sidebar.multiselect('Tipo de vehículo', tipos, default=tipos)

precio_min, precio_max = st.sidebar.slider(
    'Rango de precio (USD)',
    min_value=0,
    max_value=100000,
    value=(0, 60000),
    step=1000)

solo_4wd = st.sidebar.checkbox('Solo vehículos 4x4')

datos = car_data[
    car_data['type'].isin(tipos_sel)
    & car_data['price'].between(precio_min, precio_max)
]
if solo_4wd:
    datos = datos[datos['is_4wd'] == 1]

st.sidebar.markdown('---')
st.sidebar.write('Anuncios seleccionados: **{}**'.format(len(datos)))

if datos.empty:
    st.warning('Ningún anuncio cumple los filtros seleccionados. '
               'Amplía el rango de precio o añade tipos de vehículo.')
    st.stop()

# ----------------------------------------------------------------------
# Métricas resumen
# ----------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric('Anuncios', '{:,}'.format(len(datos)).replace(',', ' '))
col2.metric('Precio mediano', '{:,} USD'.format(int(datos['price'].median())).replace(',', ' '))
col3.metric('Kilometraje mediano', '{:,} mi'.format(int(datos['odometer'].median())).replace(',', ' '))
col4.metric('Días en venta (mediana)', int(datos['days_listed'].median()))

st.markdown('---')

# ----------------------------------------------------------------------
# Gráfico 1 — Histograma
# ----------------------------------------------------------------------
st.subheader('Distribución del kilometraje')

construir_histograma = st.checkbox('Construir un histograma', value=True)

if construir_histograma:
    st.write('Distribución del odómetro de los vehículos anunciados.')

    fig_hist = px.histogram(
        datos,
        x='odometer',
        nbins=50,
        title='Distribución del kilometraje (odómetro)',
        labels={'odometer': 'Kilometraje (millas)', 'count': 'Número de anuncios'},
        color_discrete_sequence=[AZUL])

    fig_hist.update_layout(yaxis_title='Número de anuncios', bargap=0.02)

    st.plotly_chart(fig_hist)

    st.caption(
        'La distribución está sesgada a la derecha: la mayoría de los coches '
        'ronda las {:,} millas, con una cola de vehículos muy rodados.'
        .format(int(datos['odometer'].median())).replace(',', ' '))

# ----------------------------------------------------------------------
# Gráfico 2 — Dispersión
# ----------------------------------------------------------------------
st.subheader('Relación entre kilometraje y precio')

construir_dispersion = st.checkbox('Construir un gráfico de dispersión', value=True)

if construir_dispersion:
    st.write('Cada punto es un anuncio: kilometraje frente a precio de venta.')

    fig_disp = px.scatter(
        datos,
        x='odometer',
        y='price',
        opacity=0.4,
        title='Kilometraje frente a precio',
        labels={'odometer': 'Kilometraje (millas)', 'price': 'Precio (USD)'},
        color_discrete_sequence=[AZUL],
        hover_data=['model', 'model_year', 'condition'])

    st.plotly_chart(fig_disp)

    correlacion = datos['odometer'].corr(datos['price'])
    st.caption(
        'Correlación entre kilometraje y precio en la selección actual: '
        '**{:+.3f}**. Cuanto más rodado está un coche, más barato se anuncia.'
        .format(correlacion))

# ----------------------------------------------------------------------
# Gráfico 3 — Comparación por transmisión (máximo 3 series)
# ----------------------------------------------------------------------
st.subheader('Comparar precios por tipo de transmisión')

comparar = st.checkbox('Comparar la distribución de precios')

if comparar:
    st.write('Distribución del precio según el tipo de transmisión.')

    fig_comp = px.histogram(
        datos,
        x='price',
        color='transmission',
        nbins=50,
        barmode='overlay',
        opacity=0.6,
        title='Distribución del precio según la transmisión',
        labels={'price': 'Precio (USD)', 'transmission': 'Transmisión'},
        color_discrete_sequence=[AZUL, NARANJA, MORADO])

    fig_comp.update_layout(yaxis_title='Número de anuncios', bargap=0.02)

    st.plotly_chart(fig_comp)

    resumen = (datos.groupby('transmission')['price']
               .agg(['count', 'median', 'mean'])
               .round(0)
               .astype(int)
               .rename(columns={'count': 'Anuncios',
                                'median': 'Precio mediano',
                                'mean': 'Precio medio'}))
    st.dataframe(resumen)

# ----------------------------------------------------------------------
# Datos en bruto
# ----------------------------------------------------------------------
st.markdown('---')

if st.checkbox('Mostrar los datos en bruto'):
    st.dataframe(datos.head(500))
    st.caption('Se muestran las primeras 500 filas de la selección.')
