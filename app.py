import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
import os

st.set_page_config(page_title="Bluetek Offshore Analysis", layout="wide")

@st.cache_data
def load_data():
    folder_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(folder_path, 'offshore_sales_opportunity_final.csv')
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

# --- BARRA LATERAL ---
st.sidebar.header("Filtros de Análisis")
year_selected = st.sidebar.selectbox("Seleccionar Año", sorted(df['year'].unique(), reverse=True))
countries = st.sidebar.multiselect("Países", df['country'].unique(), default=df['country'].unique())

# Filtrado dinámico
filtered_df = df[(df['year'] == year_selected) & (df['country'].isin(countries))]

# --- TÍTULO ---
st.title("📊 Estrategia Comercial Bluetek Supply Inc.")
st.markdown(f"### Análisis de Oportunidades Offshore ({year_selected})")

# --- 1. GRÁFICA DE LÍNEAS (PRODUCCIÓN) ---
st.header("1. Evolución de la Producción Mensual")
line_chart = alt.Chart(df[df['country'].isin(countries)]).mark_line(point=True).encode(
    x=alt.X('date:T', title='Fecha'),
    y=alt.Y('sum(oil_production_mbd):Q', title='Producción Total (Mb/d)'),
    color='country:N',
    tooltip=['country', 'year', 'month', 'sum(oil_production_mbd)']
).properties(height=350).interactive()
st.altair_chart(line_chart, use_container_width=True)

# --- 2. MAPA ---
st.header("2. Mapa de Inversión por Plataforma (Consolidado Anual)")
# Agrupación por plataforma y país
map_data = filtered_df.groupby(['field_name', 'country']).agg({
    'lat': 'first',
    'lon': 'first',
    'total_imports_usd': 'sum',
    'oil_production_mbd': 'mean'
}).reset_index()

fig_map = px.scatter_geo(
    map_data, lat='lat', lon='lon', color="country",
    size="total_imports_usd", 
    hover_name="field_name",
    hover_data={'lat':False, 'lon':False, 'total_imports_usd':':.2f'},
    projection="natural earth", 
    scope="north america",
    height=600,
    template="plotly_dark"
)
st.plotly_chart(fig_map, use_container_width=True)

# --- 3. MATRIZ DE DECISIÓN ---
st.header("3. Matriz de Prioridad: Incidentes vs Oportunidad")
st.markdown(f"""
Análisis específico para el año **{year_selected}**. 
La línea de tendencia muestra cómo los incidentes impactan en nuestra oportunidad de negocio.
""")

# Aviso si es un año bajo regulación
if year_selected >= 2024:
    st.warning("⚠️ Nota: En este periodo la normativa IMO 2025 ya influye en la demanda de equipos certificados.")

fig_scatter = px.scatter(
    filtered_df, 
    x="safety_incidents",
    y="sales_opportunity_index",
    size="oil_production_mbd",
    color="imo_regulation_active",
    hover_name="field_name",
    trendline="ols", 
    labels={
        "safety_incidents": "Nº de Incidentes Reportados",
        "sales_opportunity_index": "Índice Oportunidad Bluetek",
        "imo_regulation_active": "Normativa IMO 2025 Activa"
    },
    color_discrete_map={True: "#EF553B", False: "#636EFA"}
)
st.plotly_chart(fig_scatter, use_container_width=True)