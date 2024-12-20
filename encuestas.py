import os
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
import pandas as pd
import streamlit as st
import random
import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Función para generar un ID único para cada encuesta


def generar_id_encuesta():
    return str(random.randint(100000, 999999))

# Función para obtener la fecha y hora actual


def obtener_fecha_hora():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Función para cargar las preguntas desde el archivo Excel


def cargar_preguntas():
    # Lee el archivo Excel (asegúrate de que el archivo Excel esté en la misma carpeta que el script o proporciona la ruta)
    df = pd.read_excel('preguntas_encuesta.xlsx')
    preguntas = df.to_dict(orient='records')
    return preguntas

# Inicialización de Firebase


def inicializar_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_PATH"))
        initialize_app(cred)
    db = firestore.client()
    return db

# Función para guardar los datos en Firestore


def guardar_en_firestore(nro_control, datos_encuesta):
    db = inicializar_firebase()
    ref = db.collection('encuestas').document(nro_control)
    ref.set(datos_encuesta)
    return True  # Devuelve True para simular un guardado exitoso

# Aplicación principal


def app():
    st.set_page_config(page_title="Encuesta Tesis Doctoral", layout="wide")

    st.markdown(
        """
        <style>
            .pregunta {
                border: 2px solid #0078D4;
                padding: 10px;
                margin-bottom: 20px;
                border-radius: 5px;
                background-color: white;
            }
            .recuadro-control {
                border: 1px solid #0078D4;
                padding: 15px;
                margin-bottom: 20px;
                border-radius: 5px;
                background-color: white;
                font-size: 1em;
            }
            .boton-enviar {
                background-color: #0078D4;
                color: white;
                font-weight: bold;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        st.image("logo_ucab.jpg", width=150)
        st.subheader("Instrucciones")
        st.markdown(
            """
            **Gracias por participar en esta encuesta.**
            - Lea cuidadosamente las preguntas.
            - Seleccione la opción que considere pertinente.
            - Al finalizar, presione el botón "Enviar".
            """
        )

    with col2:
        st.title("Encuesta")

        if "nro_control" not in st.session_state:
            st.session_state.nro_control = generar_id_encuesta()
            st.session_state.fecha_hora = obtener_fecha_hora()

        # Mostrar número de control y fecha en un recuadro
        st.markdown(
            f"""
            <div class="recuadro-control">
                <b>Número de Control:</b> {st.session_state.nro_control}<br>
                <b>Fecha y Hora:</b> {st.session_state.fecha_hora}
            </div>
            """,
            unsafe_allow_html=True
        )

        preguntas = cargar_preguntas()

        if "respuestas" not in st.session_state:
            st.session_state.respuestas = {
                pregunta['item']: None for pregunta in preguntas}

        # Mostrar preguntas numeradas correlativamente
        for i, pregunta in enumerate(preguntas, start=1):
            st.markdown(
                f"""
                <div class="pregunta">
                    <p><b>{i}. {pregunta['pregunta']}</b></p>
                </div>
                """,
                unsafe_allow_html=True
            )
            respuesta = st.radio(
                "",
                pregunta['posibles_respuestas'].split(','),
                key=pregunta['item']
            )

            # Guardar las respuestas
            if respuesta is not None:
                st.session_state.respuestas[pregunta['item']] = respuesta

        # Validación de respuestas antes de enviar
        preguntas_respondidas = sum(
            [1 for r in st.session_state.respuestas.values() if r is not None])
        total_preguntas = len(preguntas)
        porcentaje_respondido = (preguntas_respondidas / total_preguntas) * 100

        # Mostrar el porcentaje de progreso
        st.markdown(
            f"<b>Progreso:</b> {porcentaje_respondido:.2f}%", unsafe_allow_html=True)

        # Botón de envío
        enviar = st.button("Enviar Encuesta", key="enviar")

        if enviar:
            if preguntas_respondidas == total_preguntas:
                # Guardar respuestas en Firestore
                datos_encuesta = {
                    "nro_control": st.session_state.nro_control,
                    "fecha_hora"
