# 🚗 Panel de anuncios de venta de coches en EE. UU.

Aplicación web interactiva que permite explorar un conjunto de **51 525 anuncios**
de vehículos de segunda mano publicados en Estados Unidos.

**🔗 Aplicación desplegada:** https://sprint7bc2026.onrender.com

> Nota: en el plan gratuito de Render la aplicación se suspende tras unos minutos
> de inactividad. Si al abrir el enlace no carga a la primera, espera unos
> segundos y actualiza la página: el servicio necesita ese tiempo para despertar.

---

## ¿Para qué sirve?

El panel resuelve una pregunta sencilla pero práctica: **¿qué determina el precio
de un coche de segunda mano?** En lugar de entregar un informe estático, ofrece
una herramienta interactiva donde cualquiera puede filtrar la muestra y ver cómo
cambian las distribuciones.

## Funcionalidad

**Filtros** (barra lateral):

- Selección múltiple por **tipo de vehículo** (SUV, sedán, camioneta, etc.).
- **Rango de precio** ajustable mediante un deslizador, útil para excluir los
  valores extremos que aplastan la escala de los gráficos.
- Casilla para mostrar **solo vehículos 4x4**.

**Métricas resumen:** número de anuncios, precio mediano, kilometraje mediano y
días en venta, todo recalculado según los filtros activos.

**Gráficos**, cada uno activable con una casilla de verificación:

1. **Histograma** de la distribución del kilometraje.
2. **Gráfico de dispersión** de kilometraje frente a precio, con el coeficiente
   de correlación de la selección actual.
3. **Histograma comparativo** del precio según el tipo de transmisión, con una
   tabla resumen.

También puede mostrarse una vista de los **datos en bruto**.

## Estructura del proyecto

```
.
├── app.py                 # Aplicación Streamlit
├── vehicles_us.csv        # Conjunto de datos
├── requirements.txt       # Dependencias
├── .streamlit/
│   └── config.toml        # Configuración del servidor
└── notebooks/
    └── EDA.ipynb          # Análisis exploratorio de datos
```

## Los datos

`vehicles_us.csv` contiene 51 525 anuncios con 13 columnas: precio, año del
modelo, modelo, estado, cilindros, combustible, kilometraje, transmisión, tipo,
color, tracción 4x4, fecha de publicación y días en venta.

Hallazgos del análisis exploratorio (detallado en `notebooks/EDA.ipynb`):

- La relación entre **kilometraje y precio es negativa y no lineal**: el valor cae
  con fuerza en las primeras 100 000 millas y después se estabiliza.
- La columna `is_4wd` no tiene ausentes reales: el hueco **codifica el valor "no"**,
  por lo que se rellena con `0`.
- Existen valores extremos legítimos —precios de hasta 375 000 USD— que el filtro
  de precio permite acotar.

## Ejecutar en local

```bash
# Crear el entorno virtual
python -m venv vehicles_env
source vehicles_env/bin/activate        # Windows: vehicles_env\Scripts\activate

# Instalar las dependencias
pip install -r requirements.txt

# Lanzar la aplicación
streamlit run app.py
```

La aplicación queda disponible en `http://localhost:8501`.

## Despliegue en Render

Configuración del servicio web:

| Campo | Valor |
|---|---|
| **Build Command** | `pip install --upgrade pip && pip install -r requirements.txt` |
| **Start Command** | `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0` |

> El comando de arranque incluye `--server.port=$PORT` de forma explícita porque
> Render asigna el puerto mediante esa variable de entorno, y Streamlit no la lee
> por su cuenta. Sin ese parámetro el despliegue compila pero el servicio no
> responde.

## Tecnologías

- **[Streamlit](https://streamlit.io/)** — interfaz de la aplicación web
- **[Plotly](https://plotly.com/python/)** — gráficos interactivos
- **[pandas](https://pandas.pydata.org/)** — manipulación de datos

---

Proyecto del Sprint 7 del bootcamp de análisis de datos de TripleTen.
