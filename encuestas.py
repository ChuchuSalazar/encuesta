import os
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app, get_app
import pandas as pd
import streamlit as st
import random
import datetime
from dotenv import load_dotenv

# Cargar las credenciales de Firebase desde la variable de entorno
load_dotenv()
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")

if FIREBASE_CREDENTIALS is None:
    raise ValueError(
        "La variable de entorno FIREBASE_CREDENTIALS no está configurada.")

if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS)
    app = initialize_app(cred)
else:
    app = get_app()

db = firestore.client()

# Cargar preguntas desde el archivo Excel


def cargar_preguntas():
    preguntas_df = pd.read_excel("preguntas.xlsx")
    preguntas = []

    for _, row in preguntas_df.iterrows():
        pregunta = {
            "item": row['item'],
            "pregunta": row['pregunta'],
            "escala": row['escala'],
            "posibles_respuestas": row['posibles_respuestas'].split(',')
        }
        preguntas.append(pregunta)
    return preguntas

# Función para generar un ID único


def generar_id_encuesta():
    return f"ID_{random.randint(100000, 999999)}"

# Función para obtener la fecha y hora actual


def obtener_fecha_hora():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Guardar en Firestore


def guardar_en_firestore(id_encuesta, data):
    try:
        if any(value is None or value == "" for value in data.values()):
            raise ValueError(
                "One or more components is not a string or is empty.")
        doc_ref = db.collection("encuestas").document(id_encuesta)
        doc_ref.set(data)
        return True
    except Exception as e:
        st.error(f"Error al guardar en Firestore: {e}")
        return False

# Función de validación de respuestas


def validar_respuestas(respuestas):
    no_respondidas = []
    for key, value in respuestas.items():
        if value is None or value == "Seleccione una opción":
            no_respondidas.append(key)
    return no_respondidas

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
                font-family: Arial, sans-serif;
            }
            .recuadro-control {
                border: 1px solid #0078D4;
                padding: 15px;
                margin-bottom: 20px;
                border-radius: 5px;
                background-color: white;
                font-size: 1em;
                font-family: Arial, sans-serif;
            }
            .boton-enviar {
                background-color: #0078D4;
                color: white;
                font-weight: bold;
                font-family: Arial, sans-serif;
            }
            .rojo {
                background-color: #FF6B6B;
                border: 2px solid red;
            }
            .bloqueado {
                background-color: #F0F0F0;
                pointer-events: none;
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
                pregunta['item']: "Seleccione una opción" for pregunta in preguntas}

        # Inicializar la lista de preguntas no respondidas
        no_respondidas = []

        # Mostrar preguntas dentro de recuadros azules
        for pregunta in preguntas:
            respuesta = st.radio(
                pregunta['pregunta'],
                pregunta['posibles_respuestas'],
                key=pregunta['item'],
                index=0  # No hay respuesta por defecto
            )
            st.session_state.respuestas[pregunta['item']] = respuesta

            # Marcar en rojo las preguntas no respondidas
            if respuesta == "Seleccione una opción":
                no_respondidas.append(pregunta['item'])

        # Calcular el porcentaje de respuestas
        preguntas_respondidas = len(preguntas) - len(no_respondidas)
        total_preguntas = len(preguntas)
        porcentaje_respondido = (preguntas_respondidas / total_preguntas) * 100

        # Mostrar el porcentaje de avance
        st.markdown(
            f"<b>Progreso:</b> {porcentaje_respondido:.2f}%", unsafe_allow_html=True)

        # Mostrar el número de preguntas no respondidas
        if len(no_respondidas) > 0:
            st.warning(
                f"Por favor, responda las siguientes preguntas: {', '.join(no_respondidas)}")

        # Botón de envío
        enviar = st.button("Enviar Encuesta", key="enviar")

        if enviar:
            if len(no_respondidas) == 0:
                if guardar_en_firestore(st.session_state.nro_control, st.session_state.respuestas):
                    st.success(
                        "¡Gracias por participar! La encuesta ha sido enviada.")
                    st.balloons()

                    # Bloquear la encuesta después de enviarla
                    st.markdown(
                        """
                        <style>
                            .stApp {
                                background-color: #F0F0F0;
                                pointer-events: none;
                            }
                        </style>
                        """, unsafe_allow_html=True)
            else:
                st.warning(
                    f"Por favor, responda las siguientes preguntas: {', '.join(no_respondidas)}")


if __name__ == "__main__":
    app()
