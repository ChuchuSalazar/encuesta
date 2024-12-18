import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, db

# Configuración de Firebase
if not firebase_admin._apps:
    # Cambia por la ruta de tu archivo JSON
    cred = credentials.Certificate("ruta_a_tu_archivo_de_clave.json")
    firebase_admin.initialize_app(
        # Cambia por tu URL
        cred, {'databaseURL': "https://tu-base-de-datos.firebaseio.com/"})

# Función para mostrar los datos demográficos


def mostrar_datos_demograficos():
    st.sidebar.header("Datos Demográficos")

    # Recuadro gris ajustado (ancho aumentado en un 25%)
    with st.sidebar.container():
        st.markdown(
            """
            <div style="background-color:#f2f2f2; padding:15px; border-radius:5px; width:125%; margin-left:-10%; box-sizing:border-box;">
            <strong>Por favor complete los datos demográficos:</strong>
            </div>
            """, unsafe_allow_html=True)

        sexo = st.radio(
            "Sexo:", ["Selecciona una opción", "Masculino", "Femenino"], key="sexo")
        edad = st.slider("Edad:", 18, 100, 25, key="edad")
        ciudad = st.selectbox("Ciudad:", ["Selecciona una opción", "Caracas",
                              "Valencia", "Maracay", "Maracaibo", "Barquisimeto"], key="ciudad")
        salario = st.selectbox("Rango de salario:", [
                               "Selecciona una opción", "1-100", "101-300", "301-600", "601-1000", "1001-1500", "1501-3500", "Más de 3500"], key="salario")
        nivel_educativo = st.radio("Nivel Educativo:", [
                                   "Selecciona una opción", "Primaria", "Secundaria", "Técnico", "Universitario"], key="nivel_educativo")

    return sexo, edad, ciudad, salario, nivel_educativo

# Función para mostrar las preguntas del cuestionario


def mostrar_preguntas(preguntas):
    respuestas = {}
    preguntas_no_respondidas = []

    for i, row in preguntas.iterrows():
        item = row['item']
        pregunta = row['pregunta']
        opciones = row['posibles_respuestas'].split(",")

        # Inicializa la pregunta como no respondida
        respuesta = st.radio(
            f"{pregunta}", ["Selecciona una opción"] + opciones, key=f"pregunta_{item}")

        # Colorea en rojo si no se ha respondido
        if respuesta == "Selecciona una opción":
            st.markdown(
                f'<div style="color: red; font-size: 12px;">Por favor responde esta pregunta</div>',
                unsafe_allow_html=True,
            )
            preguntas_no_respondidas.append(item)
        else:
            respuestas[item] = respuesta

    return respuestas, preguntas_no_respondidas

# Validación y guardado en Firebase


def guardar_respuestas(datos_demograficos, respuestas):
    data = {**datos_demograficos, **respuestas}
    ref = db.reference("respuestas")
    ref.push(data)
    st.success("¡Respuestas enviadas con éxito!")

# Función principal


def app():
    st.title("Cuestionario")
    st.markdown(
        "<div style='text-align: right;'><img src='https://upload.wikimedia.org/wikipedia/commons/4/4a/Logo_UCAB.png' alt='Logo UCAB' width='150'/></div>",
        unsafe_allow_html=True,
    )
    st.subheader("Por favor, responde todas las preguntas antes de enviar.")

    # Carga de las preguntas desde un archivo Excel
    preguntas_df = pd.DataFrame({
        "item": [1, 2, 3, 4, 5],
        "pregunta": [
            "¿Qué tan satisfecho estás con tus hábitos de ahorro?",
            "¿Sueles ahorrar de manera regular cada mes?",
            "¿Te sientes cómodo manejando tu presupuesto mensual?",
            "¿Ahorras con un propósito específico en mente?",
            "¿Crees que podrías ahorrar más de lo que actualmente ahorras?"
        ],
        "posibles_respuestas": [
            "Muy insatisfecho,Insatisfecho,Neutral,Satisfecho,Muy satisfecho",
            "Nunca,Rara vez,A veces,A menudo,Siempre",
            "Nada cómodo,Poco cómodo,Neutral,Bastante cómodo,Muy cómodo",
            "Nunca,Rara vez,A veces,A menudo,Siempre",
            "Totalmente en desacuerdo,En desacuerdo,Neutral,De acuerdo,Totalmente de acuerdo"
        ]
    })

    # Mostrar datos demográficos
    sexo, edad, ciudad, salario, nivel_educativo = mostrar_datos_demograficos()
    datos_demograficos = {
        "sexo": sexo,
        "edad": edad,
        "ciudad": ciudad,
        "salario": salario,
        "nivel_educativo": nivel_educativo
    }

    # Mostrar preguntas
    st.subheader("Preguntas del cuestionario")
    respuestas, preguntas_no_respondidas = mostrar_preguntas(preguntas_df)

    # Botón para enviar respuestas
    if st.button("Enviar"):
        if "Selecciona una opción" in datos_demograficos.values():
            st.error("Por favor, completa todos los campos de datos demográficos.")
        elif preguntas_no_respondidas:
            st.error("Por favor, responde todas las preguntas antes de enviar.")
        else:
            guardar_respuestas(datos_demograficos, respuestas)


if __name__ == "__main__":
    app()
