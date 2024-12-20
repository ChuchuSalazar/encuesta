# Importación de bibliotecas necesarias
import os
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app, get_app
import pandas as pd
import streamlit as st
import random
import datetime
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Inicializar Firebase
# Usar el archivo JSON de Firebase desde el .env
cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_PATH"))
firebase_admin.initialize_app(cred)
db = firestore.client()

# Función para obtener la fecha y hora actual


def obtener_fecha_hora():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Función para generar el ID de la encuesta


def generar_id_encuesta():
    return f"ID_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

# Función para guardar los datos en Firestore


def guardar_en_firestore(id_encuesta, datos):
    try:
        # Guardar la encuesta en Firestore
        db.collection('encuestas').document(id_encuesta).set(datos)
        return True
    except Exception as e:
        st.error(f"Error al guardar en Firestore: {e}")
        return False

# Función para calcular el porcentaje de progreso


def calcular_porcentaje_respuestas(respuestas_llenadas, total_respuestas):
    return (respuestas_llenadas / total_respuestas) * 100

# Función para mostrar preguntas no respondidas al presionar "Enviar"


def mostrar_preguntas_no_respondidas(preguntas_no_respondidas):
    if preguntas_no_respondidas:
        st.markdown(
            f"""
            <div class="recuadro-preguntas-no-respondidas">
                <b>Las siguientes preguntas aún no han sido respondidas:</b><br>
                {', '.join(preguntas_no_respondidas)}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.success("¡Gracias por completar la encuesta!")

# Función para cargar las preguntas de la encuesta


def cargar_preguntas():
    # Aquí deberías cargar las preguntas desde un archivo o base de datos
    # Ejemplo con preguntas predefinidas
    preguntas = [
        {"item": "AV1", "pregunta": "Pregunta 01", "escala": "5", "posibles_respuestas": [
            "Totalmente en desacuerdo", "En desacuerdo", "Neutral", "De acuerdo", "Totalmente de acuerdo"]},
        {"item": "AV2", "pregunta": "Pregunta 02", "escala": "5", "posibles_respuestas": [
            "Totalmente en desacuerdo", "En desacuerdo", "Neutral", "De acuerdo", "Totalmente de acuerdo"]},
        # Agregar más preguntas aquí...
    ]
    return preguntas

# Función para mostrar las preguntas generales (Sexo, Edad, etc.)


def mostrar_preguntas_generales():
    sexo = st.selectbox("Sexo", ["Masculino", "Femenino", "Otro"], key="sexo")
    rango_edad = st.selectbox(
        "Rango de Edad", ["18-24", "25-34", "35-44", "45-54", "55+"], key="rango_edad")
    rango_ingreso = st.selectbox("Rango de Ingreso", [
                                 "Menos de 500", "500-1000", "1000-2000", "Más de 2000"], key="rango_ingreso")
    ciudad = st.selectbox("Ciudad", [
                          "Caracas", "Maracaibo", "Valencia", "Barquisimeto", "Otro"], key="ciudad")
    nivel_prof = st.selectbox("Nivel Educativo", [
                              "Primaria", "Secundaria", "Universitario", "Postgrado"], key="nivel_prof")

    return sexo, rango_edad, rango_ingreso, ciudad, nivel_prof

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
            .recuadro-preguntas-no-respondidas {
                border: 2px solid red;
                padding: 15px;
                margin-top: 20px;
                background-color: #f8d7da;
                color: red;
                font-weight: bold;
                border-radius: 5px;
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

        # Preguntas generales
        sexo, rango_edad, rango_ingreso, ciudad, nivel_prof = mostrar_preguntas_generales()

        # Cargar preguntas adicionales
        preguntas = cargar_preguntas()

        if "respuestas" not in st.session_state:
            st.session_state.respuestas = {
                pregunta['item']: None for pregunta in preguntas}
            # Incluir las preguntas generales en el control de respuestas
            st.session_state.respuestas["sexo"] = None
            st.session_state.respuestas["rango_edad"] = None
            st.session_state.respuestas["rango_ingreso"] = None
            st.session_state.respuestas["ciudad"] = None
            st.session_state.respuestas["nivel_prof"] = None

        # Mostrar preguntas dentro de recuadros azules y calcular el progreso
        preguntas_no_respondidas = []
        for i, pregunta in enumerate(preguntas, start=1):
            # Numera las preguntas del 01 al 25
            pregunta_numero = f"Pregunta {i:02d}"
            st.markdown(
                f"""
                <div class="pregunta">
                    <p><b>{pregunta_numero}: {pregunta['pregunta']}</b></p>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Mostrar las opciones de respuesta según la escala
            # Si la escala es 5 (por ejemplo, Likert 5 puntos)
            if pregunta['escala'] == "5":
                options = pregunta['posibles_respuestas']
                respuesta = st.radio(
                    "",
                    options,
                    key=pregunta['item']
                )
            else:
                # Si la escala no es 5, se ajusta según el número de opciones
                options = pregunta['posibles_respuestas']
                respuesta = st.radio(
                    "",
                    options,
                    key=pregunta['item']
                )

            # Registrar la respuesta
            st.session_state.respuestas[pregunta['item']] = respuesta

            # Verificar si la pregunta está respondida
            if respuesta is None:
                preguntas_no_respondidas.append(pregunta_numero)

        # Calcular el porcentaje de progreso basado en las respuestas dadas
        respuestas_llenadas = sum(
            1 for r in st.session_state.respuestas.values() if r is not None)
        # Incluyendo las 5 preguntas generales
        total_respuestas = len(preguntas) + 5
        porcentaje_respondido = calcular_porcentaje_respuestas(
            respuestas_llenadas, total_respuestas)

        # Mostrar el porcentaje de avance
        st.markdown(
            f"<b>Progreso:</b> {porcentaje_respondido:.2f}%", unsafe_allow_html=True)

        # Mostrar preguntas no respondidas en un recuadro destacado
        mostrar_preguntas_no_respondidas(preguntas_no_respondidas)

        # Botón de envío
        enviar = st.button("Enviar Encuesta", key="enviar")

        if enviar:
            if respuestas_llenadas == total_respuestas:
                # Guardar los datos en Firestore
                datos_encuesta = {
                    "ID"}
