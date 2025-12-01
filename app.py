import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="WeatherOS Pro", 
    layout="wide", 
    page_icon=None,
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .metric-card {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #41444d;
    }
    </style>
""", unsafe_allow_html=True)

API_KEY = "1e7384891579bbb19d20c7b62e5b7f49" 

@st.cache_data(ttl=600) 
def get_weather_data(city, units='metric'):
    unit_url = "metric" if units == "Celsius" else "imperial"
    
    try:
        current_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units={unit_url}&lang=es"
        current_res = requests.get(current_url)
        current_res.raise_for_status() 
        
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units={unit_url}&lang=es"
        forecast_res = requests.get(forecast_url)
        forecast_res.raise_for_status()
        
        return current_res.json(), forecast_res.json()
        
    except requests.exceptions.HTTPError as err:
        return None, None
    except Exception as e:
        st.error(f"Error: {e}")
        return None, None

def process_forecast_data(forecast_json):
    data = []
    for item in forecast_json['list']:
        data.append({
            'Fecha': datetime.fromtimestamp(item['dt']),
            'Temperatura': item['main']['temp'],
            'Sensación Térmica': item['main']['feels_like'],
            'Humedad': item['main']['humidity'],
            'Descripción': item['weather'][0]['description'],
            'Velocidad Viento': item['wind']['speed']
        })
    return pd.DataFrame(data)

with st.sidebar:
    st.header("Configuración")
    city_input = st.text_input("Ciudad", "Tokyo")
    units = st.radio("Unidades", ["Celsius", "Fahrenheit"], horizontal=True)
    st.divider()

if city_input:
    current, forecast = get_weather_data(city_input, units)
    
    if current and forecast:
        col_head_1, col_head_2 = st.columns([3, 1])
        with col_head_1:
            st.title(f"{current['name']}, {current['sys']['country']}")
            st.caption(f"Coordenadas: {current['coord']['lat']}, {current['coord']['lon']}")
        with col_head_2:
            temp_unit = "°C" if units == "Celsius" else "°F"
            st.markdown(f"<h1 style='text-align: right; color: #00ccff;'>{current['main']['temp']}{temp_unit}</h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: right;'>{current['weather'][0]['description'].title()}</p>", unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["Dashboard", "Mapa", "Datos"])
        
        with tab1:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Sensación", f"{current['main']['feels_like']}{temp_unit}", delta_color="off")
            c2.metric("Humedad", f"{current['main']['humidity']}%")
            c3.metric("Presión", f"{current['main']['pressure']} hPa")
            c4.metric("Viento", f"{current['wind']['speed']} m/s")
            
            st.markdown("---")
            
            df_forecast = process_forecast_data(forecast)
            
            st.subheader("Pronóstico a 5 Días")
            
            fig_temp = go.Figure()
            fig_temp.add_trace(go.Scatter(x=df_forecast['Fecha'], y=df_forecast['Temperatura'], mode='lines+markers', name='Temperatura', line=dict(color='#00ccff', width=3)))
            fig_temp.add_trace(go.Scatter(x=df_forecast['Fecha'], y=df_forecast['Sensación Térmica'], mode='lines', name='Sensación', line=dict(color='#ff9900', dash='dot')))
            
            fig_temp.update_layout(
                title="Evolución Térmica",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                hovermode="x unified"
            )
            st.plotly_chart(fig_temp, use_container_width=True)
            
            col_graph_1, col_graph_2 = st.columns(2)
            
            with col_graph_1:
                fig_hum = px.bar(df_forecast, x='Fecha', y='Humedad', title="Humedad Relativa (%)", color='Humedad', color_continuous_scale='Blues')
                fig_hum.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
                st.plotly_chart(fig_hum, use_container_width=True)
                
            with col_graph_2:
                fig_wind = px.line(df_forecast, x='Fecha', y='Velocidad Viento', title="Velocidad del Viento", markers=True)
                fig_wind.update_traces(line_color='#00ff99')
                fig_wind.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
                st.plotly_chart(fig_wind, use_container_width=True)

        with tab2:
            st.subheader("Ubicación Geográfica")
            map_data = pd.DataFrame({
                'lat': [current['coord']['lat']],
                'lon': [current['coord']['lon']]
            })
            st.map(map_data, zoom=10)

        with tab3:
            st.subheader("Exportar Datos")
            st.markdown("Descarga los datos del pronóstico para tu propio análisis.")
            
            st.dataframe(df_forecast, use_container_width=True)
            
            csv = df_forecast.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descargar CSV",
                data=csv,
                file_name=f'pronostico_{city_input}.csv',
                mime='text/csv',
            )

    else:
        st.error("Ciudad no encontrada. Por favor verifica el nombre.")
else:
    st.info("Bienvenido! Ingresa una ciudad en el menú lateral para comenzar.")

