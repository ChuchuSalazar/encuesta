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

# Verificar si se ha establecido correctamente la variable de entorno
if FIREBASE_CREDENTIALS is None:
    raise ValueError(
        "La variable de entorno FIREBASE_CREDENTIALS no está configurada.")

# Inicializar Firebase si no está inicializado
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS)
    app = initialize_app(cred)
else:
    app = get_app()

# Obtener la referencia a Firestore
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

# Función para generar un ID único para cada encuesta


def generar_id_encuesta():
    return f"ID_{random.randint(100000, 999999)}"

# Función para obtener la fecha y hora actual


def obtener_fecha_hora():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Función para guardar los datos en Firestore


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

    # Estilos personalizados
    st.markdown("""
        <style>
            body {
                font-family: Arial, sans-serif;
            }
            .pregunta {
                border: 1px solid #0078D4;  /* Marco azul simple */
                padding: 10px;
                margin-bottom: 20px;
                border-radius: 5px;
            }
            .boton-enviar {
                background-color: #0078D4;
                color: white;
            }
        </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.image("logo_ucab.jpg", width=150)
        st.subheader("Instrucciones")
        st.markdown("""
            **Gracias por participar en esta encuesta. La misma es anónima y tiene fines estrictamente académicos para una tesis doctoral.**
            Lea cuidadosamente y seleccione la opción que considere pertinente. Al culminar, presione "Enviar".
        """)

    with col2:
        st.title("Encuesta")

        if "nro_control" not in st.session_state:
            st.session_state.nro_control = generar_id_encuesta()

        st.markdown(f"### Fecha y hora: {obtener_fecha_hora()}")
        st.markdown(f"### Número de control: {st.session_state.nro_control}")

        preguntas = cargar_preguntas()

        respuestas = {}
        preguntas_respondidas = 0

        # Preguntas demográficas
        sexo = st.radio("Sexo", ["Masculino", "Femenino"], key="sexo")
        rango_edad = st.radio(
            "Rango de Edad", ["18-24", "25-34", "35-44", "45-54", "55+"], key="rango_edad")
        rango_ingreso = st.radio("Rango de Ingreso Familiar", [
            "1-100", "101-300", "301-600", "601-1000", "1001-1500", "1501-3500", "Más de 3500"], key="rango_ingreso")
        nivel_educ = st.radio("Nivel Educativo", [
                              "Primaria", "Secundaria", "Licenciatura", "Maestría", "Doctorado"], key="nivel_educ")
        ciudad = st.radio("Ciudad", [
                          "Caracas", "Maracay", "Valencia", "Barquisimeto", "Mérida"], key="ciudad")

        info_general = {
            "SEXO": sexo,
            "RANGO_EDA": rango_edad,
            "RANGO_INGRESO": rango_ingreso,
            "NIVEL_PROF": nivel_educ,
            "CIUDAD": ciudad,
            "FECHA": obtener_fecha_hora()
        }

        # Mostrar preguntas principales
        for pregunta in preguntas:
            st.markdown(f'<div class="pregunta">{
                        pregunta["pregunta"]}</div>', unsafe_allow_html=True)
            respuesta = st.radio(
                label="Seleccione una opción:",
                options=pregunta['posibles_respuestas'],
                key=pregunta['item']
            )

            if respuesta:  # Contar como respondida si tiene valor
                preguntas_respondidas += 1
            respuestas[pregunta['item']] = respuesta

        # Actualizar contador de preguntas
        total_preguntas = len(preguntas) + 5
        preguntas_no_respondidas = total_preguntas - preguntas_respondidas

        st.markdown(f"### Preguntas Respondidas: {
                    preguntas_respondidas}/{total_preguntas} - No Respondidas: {preguntas_no_respondidas}")

        # Botón de envío
        if st.button("Enviar Encuesta") and preguntas_respondidas == total_preguntas:
            id_encuesta = st.session_state.nro_control
            data = {**info_general, **respuestas}

            if guardar_en_firestore(id_encuesta, data):
                st.success(
                    "¡Gracias por participar! La encuesta ha sido enviada.")
                st.balloons()
        elif preguntas_respondidas < total_preguntas:
            st.warning(
                "Por favor, responda todas las preguntas antes de enviar.")


if __name__ == "__main__":
    app()
