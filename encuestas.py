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
            "escala": row['escala'],  # El número de opciones de la escala
            # Opciones separadas por coma
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
        # Convertir todos los valores del diccionario a cadenas
        data_str = {key: str(value) for key, value in data.items()}
        doc_ref = db.collection("encuestas").document(id_encuesta)
        doc_ref.set(data_str)
        return True
    except Exception as e:
        st.error(f"Error al guardar en Firestore: {e}")
        return False

# Función para mostrar preguntas generales (sexo, edad, etc.)


def mostrar_preguntas_generales():
    sexo = st.radio("Sexo", ["Masculino", "Femenino", "Otro"], key="sexo")
    rango_edad = st.selectbox(
        "Rango de Edad", ["18-25", "26-35", "36-45", "46-60", "60+"], key="rango_edad")
    rango_ingreso = st.selectbox("Rango de Ingreso", [
                                 "<5000", "5000-10000", "10000-20000", "20000+"], key="rango_ingreso")
    ciudad = st.selectbox("Ciudad", [
                          "Caracas", "Maracaibo", "Valencia", "Barquisimeto", "Otras"], key="ciudad")
    nivel_prof = st.selectbox("Nivel Profesional", [
                              "Bachiller", "Licenciatura", "Maestría", "Doctorado"], key="nivel_prof")

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

        # Calcular el porcentaje de progreso basado en las respuestas
        preguntas_respondidas = sum(
            [1 for r in st.session_state.respuestas.values() if r is not None])
        # Incluyendo las 5 preguntas generales
        total_preguntas = len(preguntas) + 5
        porcentaje_respondido = (preguntas_respondidas / total_preguntas) * 100

        # Mostrar el porcentaje de avance
        st.markdown(
            f"<b>Progreso:</b> {porcentaje_respondido:.2f}%", unsafe_allow_html=True)

        # Mostrar preguntas no respondidas
        if preguntas_no_respondidas:
            st.warning(f"Por favor, responda las siguientes preguntas: {
                       ', '.join(preguntas_no_respondidas)}")

        # Botón de envío
        enviar = st.button("Enviar Encuesta", key="enviar")

        if enviar:
            if preguntas_respondidas == total_preguntas:
                # Guardar los datos en Firestore
                datos_encuesta = {
                    "ID": str(st.session_state.nro_control),
                    "FECHA": st.session_state.fecha_hora,
                    "SEXO": sexo,
                    "RANGO_EDA": rango_edad,
                    "RANGO_INGRESO": rango_ingreso,
                    "CIUDAD": ciudad,
                    "NIVEL_PROF": nivel_prof,
                    # Convertir respuestas a cadenas
                    **{key: str(value) for key, value in st.session_state.respuestas.items()},
                }
                if guardar_en_firestore(st.session_state.nro_control, datos_encuesta):
                    st.success(
                        "¡Gracias por participar! La encuesta ha sido enviada.")
                    st.balloons()
            else:
                st.warning(
                    "Por favor, responda todas las preguntas antes de enviar.")


if __name__ == "__main__":
    app()
