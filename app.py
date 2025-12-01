import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# --- CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="API OpenWeather - Análisis Climático", layout="wide")

# API KEY: Usamos una variable en la sesión para controlarla
# ⚠️ ADVERTENCIA: Esta clave está codificada directamente (hardcoded). 
# Para la entrega final, se recomienda usar st.sidebar.text_input.
API_KEY_DEFAULT = "a87680221a76bb8bb5f27a4f93ab601f" 

# --- FUNCIONES DE ADQUISICIÓN Y CACHÉ (Mejora de Rendimiento) ---

@st.cache_data(ttl=3600) # Caching: Los datos se guardan por 1 hora.
def get_current_weather(city, api_key):
    """Obtiene y devuelve datos del clima actual (cacheado)."""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=es"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.error("Error 401: La API Key es inválida. Por favor, verifique la clave.")
            return None
        elif response.status_code == 404:
            st.error(f"Error 404: No se encontró la ciudad '{city}'. Verifique el nombre.")
            return None
        else:
            st.error(f"Error {response.status_code} al obtener datos actuales.")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Error de conexión a internet.")
        return None

@st.cache_data(ttl=3600) # Caching: Los datos se guardan por 1 hora.
def get_forecast(city, api_key):
    """Obtiene el pronóstico y devuelve los datos JSON (cacheado)."""
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric&lang=es"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        # Los errores 401 y 404 son manejados por la función de clima actual
        return None
    except requests.exceptions.ConnectionError:
        return None

# --- ESTRUCTURA PRINCIPAL DE LA APLICACIÓN ---

def main():
    st.title("🌦️ API de OpenWeather – Proyecto de Análisis Climático")
    st.markdown("Esta aplicación permite visualizar el clima actual y el pronóstico para diferentes ciudades.")

    # Sidebar para inputs
    st.sidebar.header("Configuración")
    
    # Filtro 1: Ciudad (Input principal)
    city = st.sidebar.text_input("1. Ingrese una ciudad:", "Tokyo")
    
    # Opción de la API Key: Se muestra solo para fines de prueba/verificación
    st.sidebar.markdown(f"**Clave API en uso:** `{API_KEY_DEFAULT[:4]}...{API_KEY_DEFAULT[-4:]}`")

    # Filtro 2: Cantidad de Registros para Gráfico (Nuevo Filtro Interactivo)
    # Esto asegura tener al menos dos filtros interactivos para la evaluación.
    forecast_points = st.sidebar.slider("2. Puntos del Pronóstico (Cada 3 horas)", min_value=8, max_value=40, value=16)

    # Lógica principal
    if city:
        current = get_current_weather(city, API_KEY_DEFAULT)
        forecast = get_forecast(city, API_KEY_DEFAULT)
        
        if current:
            # 1. Mostrar métricas principales
            st.subheader(f"Clima Actual en {current['name']}, {current['sys']['country']}")
            
            # Usando contenedores de columna para un mejor layout
            col1, col2, col3, col4, col5 = st.columns(5)
            
            # Columna 1: Temperatura
            col1.metric("🌡️ Temperatura", f"{current['main']['temp']:.1f}°C", f"Sensación: {current['main']['feels_like']:.1f}°C")
            
            # Columna 2: Humedad
            col2.metric("💧 Humedad", f"{current['main']['humidity']}%")
            
            # Columna 3: Viento
            col3.metric("💨 Viento", f"{current['wind']['speed']:.1f} m/s")
            
            # Columna 4: Presión (Métrica adicional para robustez)
            col4.metric("📊 Presión", f"{current['main']['pressure']} hPa")
            
            # Columna 5: Clima
            col5.metric("🌤️ Condición", current['weather'][0]['description'].capitalize())
            
            # 2. Gráfico de pronóstico
            if forecast:
                st.markdown("---")
                st.subheader(f"Tendencia de Pronóstico a {int(forecast_points/8)} Días")
                
                # Procesar datos para el gráfico (Fase 2)
                forecast_list = forecast['list'][:forecast_points] # Usamos el filtro de puntos
                
                dates = [datetime.fromtimestamp(item['dt']) for item in forecast_list]
                temps = [item['main']['temp'] for item in forecast_list]
                humidity = [item['main']['humidity'] for item in forecast_list]
                
                # Crear DataFrame
                df = pd.DataFrame({
                    'Fecha': dates,
                    'Temperatura': temps,
                    'Humedad': humidity
                })
                
                # Filtro 3: Seleccionar métrica para el gráfico (st.radio)
                metric_to_plot = st.radio("Seleccione la métrica a visualizar:", ["Temperatura", "Humedad"], horizontal=True)
                
                # Crear gráfico con Matplotlib
                fig, ax = plt.subplots(figsize=(12, 5))
                
                if metric_to_plot == "Temperatura":
                    ax.plot(df['Fecha'], df['Temperatura'], color='#FF5733', linewidth=2, marker='o', markersize=4)
                    ax.set_ylabel("Temperatura (°C)", color='#FF5733')
                    ax.set_title(f"Evolución de la Temperatura en {city}", fontsize=16)
                else:
                    ax.plot(df['Fecha'], df['Humedad'], color='#33B5FF', linewidth=2, marker='s', markersize=4)
                    ax.set_ylabel("Humedad (%)", color='#33B5FF')
                    ax.set_title(f"Evolución de la Humedad en {city}", fontsize=16)
                    
                ax.set_xlabel("Fecha y Hora")
                ax.tick_params(axis='x', rotation=45)
                ax.grid(True, alpha=0.5, linestyle='--')
                plt.tight_layout()
                st.pyplot(fig)
                
                # Mostrar datos en tabla (opcional)
                with st.expander("Ver tabla de datos detallada (DataFrame)"):
                    st.dataframe(df, use_container_width=True)
            
        elif current is None:
             # Si current es None, el error ya fue mostrado por get_current_weather
             pass
    else:
        st.info("Ingrese el nombre de una ciudad en la barra lateral para comenzar.")

if __name__ == "__main__":
    main()
