import streamlit as st
import pandas as pd
import random
import datetime
from firebase_admin import credentials, firestore, initialize_app, get_app
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")

# Inicializar Firebase, pero solo si no se ha inicializado previamente
try:
    app = get_app()
except ValueError as e:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS)
    app = initialize_app(cred)

# Conectar a Firestore
db = firestore.client()

# Función para generar un ID único


def generar_id():
    return random.randint(100000, 999999)


# URL del archivo de preguntas
url_preguntas = 'https://raw.githubusercontent.com/ChuchuSalazar/encuesta/main/preguntas.xlsx'

# Función para cargar preguntas con un spinner


def cargar_preguntas(url):
    with st.spinner('Cargando las preguntas...'):
        df = pd.read_excel(url, header=0)
        df['escala'] = pd.to_numeric(
            df['escala'], errors='coerce').dropna().astype(int)
    return df


# Cargar preguntas
df_preguntas = cargar_preguntas(url_preguntas)

# Función para guardar respuestas en Firebase


def guardar_respuestas(respuestas, id_encuesta):
    fecha = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for pregunta_id, respuesta in respuestas.items():
        data = {'FECHA': fecha, 'RESPUESTA': respuesta}
        db.collection('respuestas').document(
            f"{id_encuesta}_{pregunta_id}").set(data)

# Función para mostrar la encuesta


def mostrar_encuesta():
    # Logo UCAB y fecha actual
    col_logo, col_fecha = st.columns([5, 1])
    with col_logo:
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/2/2c/Logo_UCAB.png", width=100)
    with col_fecha:
        st.write(
            f"**Fecha y Hora:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Título e instrucciones en recuadro gris
    st.markdown("""
    <div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px;">
    <h2>Instrucciones</h2>
    <p><strong>Gracias por participar en esta encuesta. La misma es anónima y tiene fines estrictamente académicos para una tesis doctoral. 
    Lea cuidadosamente y seleccione la opción que considere pertinente, al culminar presione Enviar.</strong></p>
    </div>
    """, unsafe_allow_html=True)

    # Datos demográficos
    st.header("Datos Demográficos")
    respuestas = {}
    col1, col2 = st.columns(2)
    with col1:
        respuestas['sexo'] = st.radio(
            "1. Sexo:", ["Masculino", "Femenino", "Otro"], horizontal=True, index=None)
        respuestas['rango_edad'] = st.radio("2. Rango de Edad:", [
                                            "18-25", "26-35", "36-45", "46-60", "60+"], horizontal=True, index=None)
    with col2:
        respuestas['rango_ingresos'] = st.radio(
            "3. Rango de Ingresos:", ["<500", "500-1000", "1000-2000", ">2000"], index=None)
        respuestas['nivel_educacion'] = st.selectbox("4. Nivel de Educación:", [
                                                     "Primaria", "Secundaria", "Pregrado", "Posgrado", "Doctorado"], index=None)
        respuestas['ciudad'] = st.text_input("5. Ciudad:", "")

    # Preguntas del Excel
    st.header("Preguntas de la Encuesta")
    preguntas_faltantes = []
    all_answered = True
    for i, row in df_preguntas.iterrows():
        pregunta_id = row['item']
        pregunta_texto = row['pregunta']
        escala = row['escala']
        opciones = row['posibles_respuestas'].split(',')[:escala]

        # Estilo de pregunta
        borde = "2px solid blue"
        if st.session_state.get(f"respuesta_{pregunta_id}") is None:
            borde = "3px solid red"  # Si no está respondida, se marca en rojo
            all_answered = False

        # Mostrar la pregunta
        st.markdown(
            f"""<div style="border: {borde}; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            <b>{i+1}. {pregunta_texto}</b>
            </div>""",
            unsafe_allow_html=True
        )
        respuesta = st.radio(
            f"Seleccione una opción para la Pregunta {i+1}:",
            opciones,
            index=None,
            key=f"respuesta_{pregunta_id}"
        )
        respuestas[pregunta_id] = respuesta

    # Contador de respuestas
    num_respuestas = sum(1 for v in respuestas.values() if v is not None)
    total_preguntas = len(df_preguntas)

    # Mostrar el contador de respuestas
    st.markdown(f"**Respuestas: {num_respuestas}/{total_preguntas}**")

    # Mostrar el botón solo si todas las respuestas están contestadas
    if all_answered:
        submit_disabled = False
    else:
        submit_disabled = True

    # Definir el botón de Enviar
    submit_button = st.button("Enviar", disabled=submit_disabled)

    if submit_button:
        preguntas_faltantes.clear()
        for i, row in df_preguntas.iterrows():
            pregunta_id = row['item']
            if respuestas[pregunta_id] is None:
                preguntas_faltantes.append(i+1)

        if preguntas_faltantes:
            st.error("Por favor, responda las siguientes preguntas:")
            for num_pregunta in preguntas_faltantes:
                st.write(f"❗ **Pregunta {num_pregunta}**",
                         unsafe_allow_html=True)
        else:
            # Guardar respuestas
            id_encuesta = f"ID_{generar_id()}"
            guardar_respuestas(respuestas, id_encuesta)

            # Mostrar mensaje de agradecimiento
            st.success("¡Gracias por completar la encuesta!")
            st.balloons()

            # Desactivar las preguntas y el botón de enviar
            st.stop()

    # Mostrar mensaje si todas las preguntas han sido respondidas
    if all_answered:
        st.markdown(
            "### Todas las preguntas han sido respondidas correctamente.", unsafe_allow_html=True)


# Ejecutar la aplicación
if __name__ == '__main__':
    mostrar_encuesta()
