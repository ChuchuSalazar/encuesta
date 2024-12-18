import streamlit as st
import pandas as pd
import random
import datetime

# Cargar el archivo de preguntas
df_preguntas = pd.read_excel("preguntas.xlsx")

# Función para generar ID aleatorio


def generar_id():
    return random.randint(100000, 999999)

# Mostrar instrucciones y logo


def mostrar_instrucciones():
    st.markdown(
        """
        <style>
        .titulo {font-size: 20px; color: #000; font-weight: bold;}
        .texto-intro {background-color: #f2f2f2; padding: 10px; border-radius: 5px;}
        .recuadro {border: 2px solid #4A90E2; border-radius: 5px; padding: 10px;}
        .rojo {border: 2px solid red; border-radius: 5px; padding: 10px;}
        </style>
        <div class="titulo">Instrucciones</div>
        <div class="texto-intro">
        Gracias por participar en esta encuesta. La misma es anónima y tiene fines estrictamente académicos para una tesis doctoral.
        Lea cuidadosamente y seleccione la opción que considere pertinente. Al culminar, presione "Enviar".
        </div>
    """
    )

# Mostrar datos demográficos


def mostrar_datos_demograficos():
    st.sidebar.header("Datos Demográficos")
    # Aquí se podrían agregar los datos a través de SelectBox, etc.
    sexo = st.sidebar.radio("Sexo", ["Masculino", "Femenino"])
    edad = st.sidebar.slider("Edad", 18, 100, 25)
    ciudad = st.sidebar.selectbox(
        "Ciudad", ["Caracas", "Valencia", "Maracay", "Maracaibo", "Barquisimeto"])
    salario = st.sidebar.multiselect("Rango de salario", [
                                     "Menos de 1.000.000", "1.000.000 - 2.000.000", "Más de 2.000.000"])
    nivel_educativo = st.sidebar.selectbox(
        "Nivel Educativo", ["Primaria", "Secundaria", "Técnico", "Universitario"])

    return sexo, edad, ciudad, salario, nivel_educativo

# Mostrar preguntas


def mostrar_preguntas():
    respuestas = {}
    for idx, row in df_preguntas.iterrows():
        pregunta = row["pregunta"]
        # Suponiendo que las respuestas son separadas por comas
        opciones = row["posibles_respuestas"].split(",")

        # Mostrar pregunta en marco azul
        st.markdown(f'<div class="recuadro"><b>{
                    idx + 1}. {pregunta}</b></div>', unsafe_allow_html=True)

        # Mostrar las opciones de respuesta
        respuesta = st.radio(f"Pregunta {idx + 1}", opciones, key=idx)

        # Almacenar las respuestas
        respuestas[idx] = respuesta

    return respuestas

# Validación antes de enviar


def validar_respuestas(respuestas):
    no_respondidas = [i+1 for i,
                      resp in enumerate(respuestas.values()) if resp is None]
    return no_respondidas


def app():
    st.title("Encuesta de Tesis Doctoral")
    mostrar_instrucciones()

    # Datos demográficos
    sexo, edad, ciudad, salario, nivel_educativo = mostrar_datos_demograficos()

    # Mostrar preguntas
    respuestas = mostrar_preguntas()

    # Botón de enviar
    if st.button("Enviar"):
        no_respondidas = validar_respuestas(respuestas)

        if no_respondidas:
            for i in no_respondidas:
                st.markdown(
                    f"**Pregunta {i} no respondida!**", unsafe_allow_html=True)
            st.warning(
                "Por favor, responda todas las preguntas antes de enviar.")
        else:
            # Guardar respuestas y mostrar mensaje final
            # Aquí se pueden guardar en una base de datos si es necesario
            st.success(
                "Gracias por participar. Sus respuestas han sido registradas.")
            st.balloons()  # Efecto de globos al finalizar
            st.stop()  # Detener el proceso después de enviar


if __name__ == "__main__":
    app()
