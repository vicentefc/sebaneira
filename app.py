import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Weather Dashboard", layout="wide")

# Título y descripción
st.title("🌦️ API de OpenWeather – Proyecto de Análisis de Datos Climáticos")
st.markdown("""
Esta aplicación permite visualizar el clima actual y el pronóstico para diferentes ciudades 
utilizando la API de OpenWeather.
""")

# Sidebar para inputs
st.sidebar.header("Configuración")
city = st.sidebar.text_input("Ingrese una ciudad:", "Tokyo")
API_KEY = "a87680221a76bb8bb5f27a4f93ab601f"  # Nota: En producción usar st.secrets o variables de entorno

# Funciones para obtener datos
def get_current_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=es"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def get_forecast(city):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric&lang=es"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# Lógica principal
if city:
    # Obtener datos
    current = get_current_weather(city)
    forecast = get_forecast(city)
    
    if current:
        # Mostrar métricas principales
        st.subheader(f"Clima Actual en {current['name']}, {current['sys']['country']}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Temperatura", f"{current['main']['temp']}°C", f"Sensación: {current['main']['feels_like']}°C")
            
        with col2:
            st.metric("Humedad", f"{current['main']['humidity']}%")
            
        with col3:
            st.metric("Viento", f"{current['wind']['speed']} m/s")
            
        with col4:
            st.metric("Clima", current['weather'][0]['description'].capitalize())
            
        # Gráfico de pronóstico
        if forecast:
            st.markdown("---")
            st.subheader("Pronóstico a 5 Días (Tendencia)")
            
            # Procesar datos para el gráfico
            forecast_list = forecast['list']
            dates = [datetime.fromtimestamp(item['dt']) for item in forecast_list]
            temps = [item['main']['temp'] for item in forecast_list]
            humidity = [item['main']['humidity'] for item in forecast_list]
            
            # Crear DataFrame para facilitar el graficado
            df = pd.DataFrame({
                'Fecha': dates,
                'Temperatura': temps,
                'Humedad': humidity
            })
            
            # Opción de filtro para el gráfico
            metric_to_plot = st.radio("Seleccione métrica para graficar:", ["Temperatura", "Humedad"], horizontal=True)
            
            # Crear gráfico con Matplotlib
            fig, ax = plt.subplots(figsize=(10, 4))
            
            if metric_to_plot == "Temperatura":
                ax.plot(df['Fecha'], df['Temperatura'], color='#FF5733', linewidth=2, marker='o', markersize=4)
                ax.set_ylabel("Temperatura (°C)")
                ax.set_title(f"Evolución de la Temperatura en {city}")
                ax.grid(True, alpha=0.3)
            else:
                ax.plot(df['Fecha'], df['Humedad'], color='#33B5FF', linewidth=2, marker='o', markersize=4)
                ax.set_ylabel("Humedad (%)")
                ax.set_title(f"Evolución de la Humedad en {city}")
                ax.grid(True, alpha=0.3)
                
            plt.xticks(rotation=45)
            st.pyplot(fig)
            
            # Mostrar datos en tabla (opcional)
            with st.expander("Ver datos detallados"):
                st.dataframe(df)
                
    else:
        st.error("No se pudo encontrar la ciudad. Por favor verifique el nombre e intente nuevamente.")
else:
    st.info("Ingrese el nombre de una ciudad en la barra lateral para comenzar.")
