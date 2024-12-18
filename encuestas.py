import streamlit as st
import pandas as pd
import random
from datetime import datetime

# Cargar el archivo Excel


def cargar_preguntas():
    try:
        preguntas_df = pd.read_excel('preguntas.xlsx')
        return preguntas_df
    except Exception as e:
        st.error(f"Error al cargar el archivo Excel: {e}")
        return None

# Mostrar el logo y la fecha/hora


def mostrar_logo_y_fecha():
    st.image('logo_ucab.jpg', width=150, use_column_width=False)
    st.markdown(f"### Encuesta de Investigación")
    st.markdown(
        f"**Fecha y Hora de llenado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**")

# Función para mostrar el texto introductorio


def mostrar_texto_introduccion():
    st.markdown("""
        <div style="background-color:#D3D3D3;padding:10px;border-radius:5px;">
            <h3>Gracias por participar en esta encuesta. La misma es anónima y tiene fines estrictamente académicos para una tesis doctoral.</h3>
            <p>Lea cuidadosamente y seleccione la opción que considere pertinente. Al culminar, presione Enviar.</p>
        </div>
    """, unsafe_allow_html=True)

# Generar ID aleatorio para la encuesta


def generar_id_encuesta():
    return random.randint(100000, 999999)

# Mostrar los datos demográficos


def mostrar_datos_demograficos():
    st.markdown("### Información General")
    sexo = st.radio("Sexo:", ["Hombre", "Mujer"], key="sexo")
    edad = st.slider("Rango de Edad:", min_value=18,
                     max_value=100, step=1, value=(18, 65), key="edad")
    salario = st.slider("Rango de Salario:", min_value=0,
                        max_value=10000, step=500, value=(0, 5000), key="salario")
    ciudad = st.selectbox("Selecciona tu ciudad:", [
                          "Caracas", "Maracaibo", "Valencia", "Barquisimeto", "Mérida"], index=0, key="ciudad")

# Función para mostrar las preguntas


def mostrar_preguntas(preguntas_df):
    preguntas_respondidas = 0
    preguntas_no_respondidas = []
    respuestas = {}

    for index, row in preguntas_df.iterrows():
        pregunta = row['pregunta']
        opciones = row['posibles_respuestas'].split(',')

        respuesta = st.radio(f"{index + 1}. {pregunta}",
                             opciones, key=f"pregunta_{index}")

        if respuesta:
            respuestas[f"pregunta_{index}"] = respuesta
            preguntas_respondidas += 1
        else:
            preguntas_no_respondidas.append(index)

    return respuestas, preguntas_respondidas, preguntas_no_respondidas

# Función de validación


def validar_respuestas(preguntas_no_respondidas):
    if preguntas_no_respondidas:
        for index in preguntas_no_respondidas:
            st.markdown(f"<div style='border:2px solid red;padding:10px;margin:5px;border-radius:5px;'>{
                        index + 1} - Pregunta no respondida</div>", unsafe_allow_html=True)
        st.warning("Por favor, responda todas las preguntas.")
        return False
    return True

# Función principal para mostrar la encuesta


def mostrar_encuesta():
    preguntas_df = cargar_preguntas()
    if preguntas_df is None:
        return

    mostrar_logo_y_fecha()
    mostrar_texto_introduccion()

    # Mostrar datos demográficos
    mostrar_datos_demograficos()

    # Mostrar preguntas
    respuestas, preguntas_respondidas, preguntas_no_respondidas = mostrar_preguntas(
        preguntas_df)

    # Mostrar el contador de preguntas respondidas
    st.sidebar.markdown(
        f"**Preguntas Respondidas:** {preguntas_respondidas}/{len(preguntas_df)}")

    # Botón de envío
    if st.button("Enviar"):
        if validar_respuestas(preguntas_no_respondidas):
            # Guardar las respuestas en la base de datos (esto se debe hacer aquí)
            encuesta_id = generar_id_encuesta()
            st.success(f"Gracias por participar en la investigación. Su ID es: {
                       encuesta_id}")
            st.balloons()  # Efecto de globos
            st.experimental_rerun()  # Recargar la página para bloquear las preguntas
        else:
            st.warning("Por favor, responda todas las preguntas.")


# Ejecutar la encuesta
if __name__ == "__main__":
    mostrar_encuesta()
