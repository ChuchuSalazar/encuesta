# Importar las bibliotecas necesarias
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
        "La variable de entorno FIREBASE_CREDENTIALS no está configurada."
    )

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
        doc_ref = db.collection("encuestas").document(id_encuesta)
        doc_ref.set(data)
        return True
    except Exception as e:
        st.error(f"Error al guardar en Firestore: {e}")
        return False

# Aplicación principal


def app():
    st.set_page_config(page_title="Encuesta Tesis Doctoral", layout="wide")

    st.markdown("""
        <style>
            body {
                font-family: Arial, sans-serif;
            }
            .pregunta {
                border: 2px solid #0078D4;
                padding: 15px;
                margin-bottom: 20px;
                border-radius: 5px;
                background-color: white;
                color: black;
            }
            .pregunta.no-respondida {
                border-color: red;
            }
            .pregunta.respondida {
                border-color: #0078D4;
            }
            .pregunta.bloqueada {
                background-color: #f0f0f0;
                pointer-events: none;
                color: #888;
            }
            .recuadro-control {
                border: 1px solid #0078D4;
                padding: 10px;
                margin-bottom: 10px;
                border-radius: 5px;
                font-size: 0.85em;
            }
            .boton-enviar {
                background-color: #0078D4;
                color: white;
                font-size: 1.1em;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
        </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.image("logo_ucab.jpg", width=150)
        st.subheader("Instrucciones")
        st.markdown("""
            **Gracias por participar en esta encuesta. La misma es anónima y tiene fines estrictamente académicos.**
            Lea cuidadosamente y seleccione la opción que considere pertinente. Al culminar, presione "Enviar".
        """)

    with col2:
        st.title("Encuesta")

        if "nro_control" not in st.session_state:
            st.session_state.nro_control = generar_id_encuesta()

        # Número de control y fecha en recuadro punteado
        st.markdown(f"""
            <div class="recuadro-control">
                <strong>Número de Control:</strong> {st.session_state.nro_control}<br>
                <strong>Fecha y Hora:</strong> {obtener_fecha_hora()}
            </div>
        """, unsafe_allow_html=True)

        preguntas = cargar_preguntas()

        if "respuestas" not in st.session_state:
            st.session_state.respuestas = {
                pregunta['item']: None for pregunta in preguntas
            }
            st.session_state.validacion = {
                pregunta['item']: False for pregunta in preguntas
            }
            st.session_state.bloqueada = False

        # Contador dinámico
        preguntas_respondidas = sum(
            [1 for r in st.session_state.respuestas.values() if r is not None]
        )
        total_preguntas = len(preguntas)
        porcentaje_respondido = (preguntas_respondidas / total_preguntas) * 100

        # Mostrar preguntas principales
        for pregunta in preguntas:
            estado = "respondida" if st.session_state.respuestas[pregunta['item']
                                                                 ] else "no-respondida"
            bloqueado = "bloqueada" if st.session_state.bloqueada else ""
            st.markdown(f"<div class=\"pregunta {estado} {
                        bloqueado}\">", unsafe_allow_html=True)
            st.radio(
                f"{pregunta['pregunta']}",
                pregunta['posibles_respuestas'],
                key=pregunta['item']
            )
            st.markdown("</div>", unsafe_allow_html=True)

        # Actualizar el porcentaje de avance
        st.markdown(f"### Preguntas Respondidas: {
                    preguntas_respondidas}/{total_preguntas} ({porcentaje_respondido:.2f}%)")

        # Botón de envío
        enviar = st.button("Enviar Encuesta",
                           disabled=st.session_state.bloqueada)

        if enviar:
            for pregunta in preguntas:
                if st.session_state.respuestas[pregunta['item']] is None:
                    st.session_state.validacion[pregunta['item']] = True

            if preguntas_respondidas == total_preguntas:
                st.session_state.bloqueada = True
                st.success(
                    "¡Gracias por participar! La encuesta ha sido enviada.")
                st.balloons()
            else:
                st.warning(
                    "Por favor, responda todas las preguntas antes de enviar.")


if __name__ == "__main__":
    app()
