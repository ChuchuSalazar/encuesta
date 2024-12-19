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
        doc_ref = db.collection("encuestas").document(id_encuesta)
        doc_ref.set(data)
        return True
    except Exception as e:
        st.error(f"Error al guardar en Firestore: {e}")
        return False

# Aplicación principal


def app():
    st.set_page_config(page_title="Encuesta Tesis Doctoral", layout="wide")

    # Estilo para la aplicación
    st.markdown("""
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
            .pregunta-no-contestada {
                border: 2px solid red;
            }
            .pregunta-contestada {
                border: 2px solid blue;
            }
        </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.image("logo_ucab.jpg", width=150)
        st.subheader("Instrucciones")
        st.markdown("""
            **Gracias por participar en esta encuesta.**
            - Lea cuidadosamente las preguntas.
            - Seleccione la opción que considere pertinente.
            - Al finalizar, presione el botón "Enviar".
        """)

    with col2:
        st.title("Encuesta")

        # Generar y almacenar número de control y fecha
        if "nro_control" not in st.session_state:
            st.session_state.nro_control = generar_id_encuesta()
            st.session_state.fecha_hora = obtener_fecha_hora()

        # Mostrar número de control y fecha en un recuadro
        st.markdown(f"""
            <div class="recuadro-control">
                <b>Número de Control:</b> {st.session_state.nro_control}<br>
                <b>Fecha y Hora:</b> {st.session_state.fecha_hora}
            </div>
        """, unsafe_allow_html=True)

        preguntas = cargar_preguntas()

        if "respuestas" not in st.session_state:
            st.session_state.respuestas = {
                pregunta['item']: None for pregunta in preguntas}

        # Contador dinámico de preguntas respondidas
        preguntas_respondidas = sum(
            [1 for r in st.session_state.respuestas.values() if r is not None])
        # Incluye las preguntas de "Información General"
        total_preguntas = len(preguntas) + 5
        porcentaje_respondido = (preguntas_respondidas / total_preguntas) * 100

        # Mostrar preguntas de Información General
        st.markdown("""
            <div class="recuadro-control">
                <b>Información General</b>
            </div>
        """, unsafe_allow_html=True)

        st.radio("Sexo", ["Masculino", "Femenino"], key="sexo", index=-1)
        st.selectbox("Rango de Edad", [
                     "18-24", "25-34", "35-44", "45-54", "55+"], key="edad", index=-1)
        st.selectbox("Rango de Ingreso Familiar", [
                     "1-100", "101-300", "301-600", "601-1000", "1001-1500", "1501-3500", "más de 3500"], key="ingreso", index=-1)
        st.selectbox("Nivel Educativo", [
                     "Primaria", "Secundaria", "Licenciado", "Postgrado"], key="educacion", index=-1)
        st.selectbox("Ciudad", ["Caracas", "Maracaibo", "Valencia",
                     "Barquisimeto", "Maracay"], key="ciudad", index=-1)

        # Mostrar preguntas adicionales
        for pregunta in preguntas:
            st.markdown(f"""
                <div class="pregunta">
                    <b>{pregunta['pregunta']}</b>
                </div>
            """, unsafe_allow_html=True)
            respuesta = st.radio(
                "", pregunta['posibles_respuestas'], key=pregunta['item'], index=-1)

            # Guardar las respuestas
            if respuesta:
                st.session_state.respuestas[pregunta['item']] = respuesta

        # Mostrar el porcentaje de progreso
        st.markdown(
            f"<b>Progreso:</b> {porcentaje_respondido:.2f}%", unsafe_allow_html=True)

        # Botón de envío
        enviar = st.button("Enviar Encuesta", key="enviar")

        if enviar:
            # Validar que todas las preguntas sean respondidas
            if preguntas_respondidas == total_preguntas:
                guardar_en_firestore(
                    st.session_state.nro_control, st.session_state.respuestas)
                st.success(
                    "¡Gracias por participar! La encuesta ha sido enviada.")
                st.balloons()
            else:
                st.warning(
                    "Por favor, responda todas las preguntas antes de enviar.")
                for pregunta_item, respuesta in st.session_state.respuestas.items():
                    if respuesta is None:
                        st.markdown(
                            f"**Pregunta {pregunta_item} no respondida**", unsafe_allow_html=True)


if __name__ == "__main__":
    app()
