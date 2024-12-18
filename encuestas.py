import streamlit as st
import pandas as pd
import random
import datetime
from firebase_admin import credentials, firestore, initialize_app

# Inicializar Firebase
cred = credentials.Certificate("path/to/your/serviceAccountKey.json")
initialize_app(cred)
db = firestore.client()

# Función para cargar las preguntas desde el archivo Excel


def cargar_preguntas():
    archivo_preguntas = "preguntas.xlsx"  # Ruta del archivo Excel
    df = pd.read_excel(archivo_preguntas)

    preguntas = []
    for index, row in df.iterrows():
        pregunta = {
            "item": row['item'],
            "pregunta": row['pregunta'],
            "escala": row['escala'],
            "posibles_respuestas": ["Selecciona una opción"] + row['posibles_respuestas'].split(',')
        }
        preguntas.append(pregunta)
    return preguntas

# Función para mostrar los datos demográficos


def mostrar_datos_demograficos():
    st.sidebar.header("Datos Demográficos")

    # Recuadro azul para los datos demográficos
    with st.sidebar:
        st.markdown(
            """
            <div style="background-color:#add8e6; padding:10px; border-radius:5px;">
            <strong>Por favor complete los datos demográficos:</strong>
            </div>
            """, unsafe_allow_html=True)

        sexo = st.radio(
            "Sexo:", ["Selecciona una opción", "Masculino", "Femenino"], key="sexo")
        edad = st.selectbox("Rango de Edad:", [
                            "Selecciona una opción", "18-24", "25-34", "35-44", "45-54", "55+"], key="edad")
        ciudad = st.selectbox("Ciudad:", [
                              "Caracas", "Valencia", "Maracay", "Maracaibo", "Barquisimeto"], key="ciudad")
        salario = st.selectbox("Rango de Salario:", [
            "Selecciona una opción", "1-100", "101-300", "301-600", "601-1000", "1001-1500", "1501-3500", "Más de 3500"
        ], key="salario")
        nivel_educativo = st.radio("Nivel Educativo:", [
            "Selecciona una opción", "Primaria", "Secundaria", "Técnico", "Universitario"
        ], key="nivel_educativo")

    return sexo, edad, ciudad, salario, nivel_educativo

# Función para mostrar las preguntas y opciones


def mostrar_preguntas(preguntas):
    st.markdown(
        """
        <div style="background-color:#f2f2f2; padding:10px; border-radius:5px;">
        <strong>Responda las siguientes preguntas:</strong>
        </div>
        """, unsafe_allow_html=True)

    respuestas = {}
    preguntas_no_respondidas = []

    for pregunta in preguntas:
        with st.container():
            st.markdown(
                f"""
                <div style="background-color:#add8e6; padding:10px; border-radius:5px; margin-bottom:10px;">
                <strong>{pregunta['item']}. {pregunta['pregunta']}</strong>
                </div>
                """, unsafe_allow_html=True)

            respuesta = st.radio(
                "", options=pregunta["posibles_respuestas"], key=f"respuesta_{pregunta['item']}")

            if respuesta == "Selecciona una opción":
                preguntas_no_respondidas.append(pregunta["item"])

            respuestas[pregunta["item"]] = respuesta

    return respuestas, preguntas_no_respondidas

# Función principal para mostrar la encuesta


def app():
    st.title("Encuesta de Tesis Doctoral")

    # Fecha y hora del llenado de la encuesta
    fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.write(f"Fecha y hora de llenado: {fecha_hora}")

    # ID aleatorio para la encuesta
    encuesta_id = random.randint(1000, 9999)
    st.write(f"ID de Encuesta: {encuesta_id}")

    # Texto introductorio
    st.markdown(
        """
        <div style="background-color:#f2f2f2; padding:10px; border-radius:5px;">
        <strong>Gracias por participar en esta encuesta.</strong><br>
        La misma es anónima y tiene fines estrictamente académicos para una tesis doctoral.<br>
        Lea cuidadosamente y seleccione la opción que considere pertinente. Al culminar, presione "Enviar".
        </div>
        """, unsafe_allow_html=True)

    # Mostrar datos demográficos
    sexo, edad, ciudad, salario, nivel_educativo = mostrar_datos_demograficos()

    # Validar datos demográficos
    if sexo == "Selecciona una opción" or ciudad == "Selecciona una opción" or salario == "Selecciona una opción" or nivel_educativo == "Selecciona una opción":
        st.warning(
            "Por favor complete todos los datos demográficos antes de continuar.")
        return

    # Cargar las preguntas desde el archivo Excel
    preguntas = cargar_preguntas()

    # Mostrar las preguntas
    respuestas, preguntas_no_respondidas = mostrar_preguntas(preguntas)

    # Contador de preguntas respondidas
    total_preguntas = len(preguntas)
    preguntas_respondidas = total_preguntas - len(preguntas_no_respondidas)
    st.markdown(
        f"**Preguntas respondidas: {preguntas_respondidas}/{total_preguntas}**")

    # Botón para enviar respuestas
    if st.button("Enviar"):
        if preguntas_no_respondidas:
            st.error(
                f"Faltan responder {len(preguntas_no_respondidas)} preguntas. Revise los números: {preguntas_no_respondidas}.")
            for item in preguntas_no_respondidas:
                st.markdown(
                    f"<div style='border:2px solid red; border-radius:5px; padding:10px;'>Pregunta {
                        item} no respondida</div>",
                    unsafe_allow_html=True)
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

            db.collection("encuestas").document(str(encuesta_id)).set(data)

            st.write("Encuesta enviada exitosamente.")


# Ejecutar la aplicación
if __name__ == "__main__":
    app()
