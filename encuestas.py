import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import uuid

# Configuración inicial de Firebase
if not firebase_admin._apps:
    # Ajustar con la ruta correcta
    cred = credentials.Certificate("ruta/credenciales_firebase.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Configuración de la página
st.set_page_config(page_title="Encuesta - UCAB", layout="wide")

# Cargar archivo Excel con las preguntas
archivo_excel = "preguntas.xlsx"  # Ajustar con la ruta correcta
preguntas_df = pd.read_excel(archivo_excel)

# Diseño de la encuesta
col1, col2 = st.columns([1, 2], gap="large")

with col1:
    # Ajustar con el logo correcto
    st.image("logo_ucab.jpg", use_column_width=True)
    st.markdown(
        """<div style='text-align: justify;'>Bienvenido/a a la encuesta de investigación. Por favor, responda todas las preguntas de manera honesta y complete todos los campos antes de enviar.</div>""",
        unsafe_allow_html=True,
    )

with col2:
    # Generar un ID único para la encuesta
    encuesta_id = str(uuid.uuid4())
    st.markdown(f"### Número de control: {encuesta_id}")

    # Crear un diccionario para almacenar las respuestas
    respuestas = {}

    # Sección de preguntas demográficas
    st.markdown("## Información Demográfica")
    respuestas["sexo"] = st.radio(
        "Sexo:", ["Femenino", "Masculino", "Otro"], index=0)
    respuestas["edad"] = st.slider(
        "Edad:", min_value=18, max_value=100, step=1)
    respuestas["salario"] = st.selectbox(
        "Rango de salario:", ["< $500", "$500 - $1000", "$1000 - $2000", "> $2000"])
    respuestas["educacion"] = st.selectbox(
        "Nivel educativo:", ["Secundaria",
                             "Universitario", "Postgrado", "Doctorado"]
    )

    # Sección de preguntas de la encuesta
    st.markdown("## Preguntas de la Encuesta")
    for index, row in preguntas_df.iterrows():
        pregunta_id = row["item"]
        pregunta_texto = row["pregunta"]
        escala = row["escala"].split(",")
        respuestas[pregunta_id] = st.radio(
            pregunta_texto, options=escala, index=0, key=pregunta_id)

    # Validación de respuestas
    if st.button("Enviar Encuesta"):
        preguntas_no_respondidas = [
            k for k, v in respuestas.items() if v is None or v == ""]

        if preguntas_no_respondidas:
            st.error("Por favor, responde todas las preguntas antes de enviar.")
        else:
            # Guardar las respuestas en Firestore
            db.collection("encuestas").document(encuesta_id).set(respuestas)

            st.success(
                "¡Encuesta enviada con éxito! Gracias por tu participación.")
            st.balloons()
