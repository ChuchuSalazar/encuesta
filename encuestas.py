import os
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import streamlit as st
import random
import datetime
import json

# Cargar las credenciales de Firebase desde la variable de entorno
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")

# Verificar si se ha establecido correctamente la variable de entorno
if FIREBASE_CREDENTIALS is None:
    raise ValueError(
        "La variable de entorno FIREBASE_CREDENTIALS no está configurada.")

# Inicializar Firebase con el archivo de credenciales
cred = credentials.Certificate(FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(cred)

# Obtener la referencia a la base de datos Firestore
db = firestore.client()

# Cargar preguntas desde el archivo Excel


def cargar_preguntas():
    # Asegúrate de que el archivo esté en el directorio correcto
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

# Función para crear la encuesta y mostrarla en Streamlit


def app():
    # Configuración de Streamlit
    st.set_page_config(page_title="Encuesta Tesis Doctoral", layout="wide")

    # Panel izquierdo para instrucciones y logo
    col1, col2 = st.columns([1, 2])

    with col1:
        # Ajusta el nombre del archivo de tu logo
        st.image("logo_ucab.jpg", width=150)
        st.subheader("Instrucciones")
        st.markdown("""
            **Gracias por participar en esta encuesta. La misma es anónima y tiene fines estrictamente académicos para una tesis doctoral.**
            Lea cuidadosamente y seleccione la opción que considere pertinente, al culminar presione Enviar.
        """)

    # Panel derecho para las preguntas
    with col2:
        st.markdown(f"### Fecha y hora: {obtener_fecha_hora()}")
        st.markdown(f"### Número de control: {generar_id_encuesta()}")

        # Cargar las preguntas
        preguntas = cargar_preguntas()

        # Mostrar las preguntas "Información General"
        sexo = st.radio("Sexo", ["M", "F"], key="sexo")
        rango_edad = st.selectbox(
            "Rango de Edad", ["18-24", "25-34", "35-44", "45-54", "55+"], key="rango_edad")
        rango_ingreso = st.selectbox("Rango de Ingreso Familiar", [
                                     "1-100", "101-300", "301-600", "601-1000", "1001-1500", "1501-3500", "Más de 3500"], key="rango_ingreso")
        nivel_educ = st.radio("Nivel Educativo", [
                              "Primaria", "Secundaria", "Licenciatura", "Maestría", "Doctorado"], key="nivel_educ")
        ciudad = st.selectbox("Ciudad", [
                              "Caracas", "Maracay", "Valencia", "Barquisimeto", "Mérida"], key="ciudad")

        # Crear un diccionario con la información general
        info_general = {
            "SEXO": sexo,
            "RANGO_EDA": rango_edad,
            "RANGO_INGRESO": rango_ingreso,
            "NIVEL_PROF": nivel_educ,
            "CIUDAD": ciudad,
            "FECHA": obtener_fecha_hora()
        }

        # Mostrar las preguntas principales
        respuestas = {}
        for pregunta in preguntas:
            st.subheader(pregunta['pregunta'])
            respuesta = st.radio(
                pregunta['pregunta'], pregunta['posibles_respuestas'], key=pregunta['item'])
            respuestas[pregunta['item']] = respuesta

        # Botón para enviar los datos
        if st.button("Enviar Encuesta"):
            # Obtener el ID único para la encuesta
            id_encuesta = generar_id_encuesta()

            # Crear un objeto de datos que incluirá la información general y las respuestas
            data = {**info_general, **respuestas}

            # Guardar los datos en Firestore
            if guardar_en_firestore(id_encuesta, data):
                st.success(
                    "¡Gracias por participar! La encuesta ha sido enviada.")
                st.balloons()  # Mostrar globos de despedida
                # Inhabilitar el botón de enviar
                st.button("Enviar Encuesta", disabled=True)


if __name__ == "__main__":
    app()
