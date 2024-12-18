import streamlit as st
import pandas as pd
import random
import datetime
from firebase_admin import credentials, firestore, initialize_app, get_app
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()  # Asegurarse de que el archivo .env sea cargado
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")

if not FIREBASE_CREDENTIALS:
    st.error(
        "Error: No se encontró la credencial de Firebase. Verifica tu archivo .env.")
    st.stop()

# Inicializar Firebase, pero solo si no se ha inicializado previamente
try:
    app = get_app()
except ValueError:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS)
    app = initialize_app(cred)

# Conectar a Firestore
db = firestore.client()

# Función para cargar las preguntas desde el archivo Excel


def cargar_preguntas():
    archivo_preguntas = "preguntas.xlsx"  # Ruta del archivo Excel
    try:
        df = pd.read_excel(archivo_preguntas)
        preguntas = []
        for _, row in df.iterrows():
            pregunta = {
                "item": row['ITEM'],
                "pregunta": row['PREGUNTA'],
                "escala": row['ESCALA'],
                "posibles_respuestas": ["Selecciona una opción"] + row['posibles_respuestas'].split(',')
            }
            preguntas.append(pregunta)
        return preguntas
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo {
                 archivo_preguntas}. Verifica su existencia.")
        st.stop()

# Función para mostrar los datos demográficos


def mostrar_datos_demograficos():
    st.sidebar.header("Información General")
    sexo = st.radio("Sexo:", ["Selecciona una opción",
                    "Masculino", "Femenino"], key="sexo")
    edad = st.selectbox("Rango de Edad:", [
                        "Selecciona una opción", "18-24", "25-34", "35-44", "45-54", "55+"], key="edad")
    salario = st.selectbox("Rango de Salario:", ["Selecciona una opción", "1-100", "101-300",
                           "301-600", "601-1000", "1001-1500", "1501-3500", "Más de 3500"], key="salario")
    ciudad = st.selectbox("Ciudad:", ["Selecciona una opción", "Caracas",
                          "Valencia", "Maracay", "Maracaibo", "Barquisimeto"], key="ciudad")
    nivel_educativo = st.radio("Nivel Educativo:", [
                               "Selecciona una opción", "Primaria", "Secundaria", "Técnico", "Universitario"], key="nivel_educativo")

    return sexo, edad, ciudad, salario, nivel_educativo

# Función para mostrar las preguntas y opciones


def mostrar_preguntas(preguntas):
    respuestas = {}
    preguntas_no_respondidas = []

    for pregunta in preguntas:
        with st.container():
            st.markdown(f"<div style='background-color:#add8e6; padding:10px; border-radius:5px; margin-bottom:10px;'>"
                        f"<strong>{pregunta['item']}. {pregunta['pregunta']}</strong></div>", unsafe_allow_html=True)

            respuesta = st.radio(
                "", options=pregunta["posibles_respuestas"], key=f"respuesta_{pregunta['item']}")

            if respuesta == "Selecciona una opción":
                preguntas_no_respondidas.append(pregunta["item"])

            respuestas[pregunta["item"]] = respuesta

    return respuestas, preguntas_no_respondidas

# Función principal para mostrar la encuesta


def app():
    st.title("Encuesta de Tesis Doctoral")

    # Panel izquierdo con el logo y las instrucciones
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("logo_ucab.jpg", width=200)
    with col2:
        st.markdown("<h3>Instrucciones</h3>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="background-color:#f2f2f2; padding:10px; border-radius:5px;">
            <strong>Gracias por participar en esta encuesta.</strong><br>
            La misma es anónima y tiene fines estrictamente académicos para una tesis doctoral.<br>
            Lea cuidadosamente y seleccione la opción que considere pertinente. Al culminar, presione "Enviar".
            </div>
            """, unsafe_allow_html=True)

    # Fecha y hora del llenado de la encuesta
    fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    encuesta_id = random.randint(1000, 9999)
    st.markdown(f"<div style='border:2px solid blue; padding:10px;'><strong>Fecha y hora: {fecha_hora}</strong><br>"
                f"<strong>ID de Encuesta: {encuesta_id}</strong></div>", unsafe_allow_html=True)

    # Mostrar datos demográficos
    sexo, edad, ciudad, salario, nivel_educativo = mostrar_datos_demograficos()

    # Validación de datos demográficos
    if any(dato == "Selecciona una opción" for dato in [sexo, ciudad, salario, nivel_educativo]):
        st.warning(
            "Por favor complete todos los datos demográficos antes de continuar.")
        return

    # Cargar las preguntas desde el archivo Excel
    preguntas = cargar_preguntas()

    # Mostrar las preguntas
    respuestas, preguntas_no_respondidas = mostrar_preguntas(preguntas)

    # Botón para enviar respuestas
    if st.button("Enviar"):
        if preguntas_no_respondidas:
            st.error(f"Faltan responder las preguntas: {
                     ', '.join(map(str, preguntas_no_respondidas))}")
        else:
            st.success("Gracias por participar en la investigación.")
            st.balloons()

            # Guardar las respuestas en Firestore
            data = {
                "ID": encuesta_id,
                "FECHA": fecha_hora,
                "SEXO": sexo,
                "RANGO_EDA": edad,
                "RANGO_INGRESO": salario,
                "CIUDAD": ciudad,
                "NIVEL_PROF": nivel_educativo,
            }

            # Agregar respuestas de las preguntas
            for key, value in respuestas.items():
                data[key] = value

            try:
                db.collection("encuestas").document(str(encuesta_id)).set(data)
                st.write("Encuesta enviada exitosamente.")
            except Exception as e:
                st.error(f"Error al guardar en Firestore: {e}")

            # Bloquear la encuesta
            st.stop()


# Ejecutar la aplicación
if __name__ == "__main__":
    app()
