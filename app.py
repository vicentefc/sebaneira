import streamlit as st
import requests
import matplotlib.pyplot as plt
import pandas as pd

api_key = st.sidebar.text_input("ingresa tu api key", type="password") # Línea para la entrega final

st.set_page_config(page_title="clima tokio & más", layout="centered")

def clima_actual(ciudad, key):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={key}&units=metric&lang=es"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"error de conexión: {e}")
        return None

def pronostico_5_dias(ciudad, key):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={ciudad}&appid={key}&units=metric&lang=es"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            lista_datos = []
            for item in data['list']:
                lista_datos.append({
                    "fecha": item['dt_txt'],
                    "temperatura": item['main']['temp'],
                    "descripción": item['weather'][0]['description']
                })
            df = pd.DataFrame(lista_datos) # Implementación de Pandas (Requisito Fase 2)
            return df
        else:
            return None
    except:
        return None

def graficar_pronostico(df_filtrado, ciudad):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df_filtrado['fecha'], df_filtrado['temperatura'], marker='o', color='tab:blue')
    ax.set_xlabel("fecha / hora")
    ax.set_ylabel("temperatura (°c)")
    ax.set_title(f"pronóstico del clima en {ciudad}")
    plt.xticks(rotation=45, ha='right')
    ax.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    st.pyplot(fig) # Uso de st.pyplot() para Streamlit

st.title("api openweather - proyecto final")
st.markdown("consulta el clima actual y el pronóstico de cualquier ciudad.")

st.sidebar.header("configuración")
# Si usaste la Opción 2 arriba, esta línea ya no pide la clave al usuario.
# Si quieres el input, descomenta la línea de arriba y comenta la de la clave hardcodeada.
ciudad_input = st.sidebar.text_input("ingresa una ciudad", value="tokyo")
cant_registros = st.sidebar.slider("puntos de pronóstico a graficar", 5, 20, 10)

if st.sidebar.button("consultar clima"):
    if api_key:
        st.subheader(f"clima actual en {ciudad_input}")
        data_clima = clima_actual(ciudad_input, api_key)

        if data_clima:
            col1, col2, col3 = st.columns(3)
            col1.metric("temperatura", f"{data_clima['main']['temp']} °c")
            col2.metric("humedad", f"{data_clima['main']['humidity']}%")
            col3.metric("clima", data_clima['weather'][0]['description'].capitalize())
        else:
            st.error("no se pudo obtener el clima. verifica la ciudad o tu api key.")

        st.divider()

        st.subheader("pronóstico extendido")
        df_pronostico = pronostico_5_dias(ciudad_input, api_key)

        if df_pronostico is not None:
            df_filtrado = df_pronostico.head(cant_registros)
            graficar_pronostico(df_filtrado, ciudad_input)

            with st.expander("ver tabla de datos detallada"):
                st.dataframe(df_filtrado)
        else:
            st.error("no se pudo cargar el pronóstico.")
    else:
        st.warning("por favor ingresa tu api key en la barra lateral.")
else:
    st.info("ingresa tu api key y presiona 'consultar clima' para empezar.")
