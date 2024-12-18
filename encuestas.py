import streamlit as st
import pandas as pd
from datetime import datetime
import random

# Leer el archivo Excel con las preguntas
df_preguntas = pd.read_excel("preguntas.xlsx")

# Función para generar un ID aleatorio para la encuesta


def generar_id():
    return str(random.randint(1000, 9999))

# Función para mostrar la encuesta


def mostrar_encuesta():
    # Mostrar la fecha y hora del llenado de la encuesta
    fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    st.write(f"Fecha y Hora de llenado: {fecha_hora}")

    # Título y texto introductorio
    st.title("Instrucciones")
    st.markdown("""
        **Gracias por participar en esta encuesta. La misma es anónima y tiene fines estrictamente académicos para una tesis doctoral.**
        Lea cuidadosamente y seleccione la opción que considere pertinente. Al culminar presione Enviar.
    """, unsafe_allow_html=True)

    # Contenedor de preguntas demográficas con fondo azul claro
    with st.container():
        st.markdown("""
            <div style="background-color: lightblue; border-radius: 10px; padding: 10px;">
            <h3>Datos Demográficos</h3>
            """, unsafe_allow_html=True)

        # Número de control (ID aleatorio)
        id_encuesta = generar_id()
        st.write(f"ID de la encuesta: {id_encuesta}")

        # Mostrar preguntas demográficas
        sexo = st.radio("Sexo:", ("Masculino", "Femenino"),
                        key="sexo", help="Selecciona tu sexo.")
        edad = st.selectbox("Rango de edad:", [
                            "18-25", "26-35", "36-45", "46-60", "60+"], key="edad")
        salario = st.slider("Rango de salario:", 0, 1000000,
                            (20000, 50000), step=5000, key="salario")
        ciudad = st.selectbox("Ciudad:", [
                              "Caracas", "Maracaibo", "Valencia", "Barquisimeto", "Maracay"], key="ciudad")

        st.markdown("</div>", unsafe_allow_html=True)

    # Mostrar preguntas adicionales (más allá de las demográficas)
    st.markdown("<div style='background-color: lightgray; padding: 10px;'>",
                unsafe_allow_html=True)
    st.markdown("<h3>Preguntas</h3>", unsafe_allow_html=True)

    respuestas = {}
    preguntas_respondidas = set()
    preguntas_no_respondidas = set()

    for index, row in df_preguntas.iterrows():
        pregunta = row['pregunta']
        posibles_respuestas = row['posibles_respuestas'].split(',')
        respuesta = None
        key = f"pregunta_{index}"

        # Enmarcar las preguntas en un recuadro azul
        with st.expander(pregunta, expanded=True):
            respuesta = st.radio(pregunta, posibles_respuestas, key=key)

        # Controlar las preguntas respondidas y no respondidas
        if respuesta:
            preguntas_respondidas.add(index)
        else:
            preguntas_no_respondidas.add(index)

        respuestas[index] = respuesta

    # Contar las preguntas respondidas
    total_preguntas = len(df_preguntas)
    preguntas_respondidas_count = len(preguntas_respondidas)
    st.write(f"Preguntas respondidas: {
             preguntas_respondidas_count} / {total_preguntas}")

    # Botón de envío
    enviar = st.button("Enviar", key="enviar")

    # Validación de que todas las preguntas sean respondidas
    if enviar:
        if len(preguntas_respondidas) == total_preguntas:
            st.balloons()  # Mostrar globos
            st.success(
                "Gracias por participar en la investigación. ¡Tu encuesta ha sido completada!")
            # Aquí puedes agregar código para guardar las respuestas en la base de datos (Firebase)
        else:
            # Colorear en rojo las preguntas no respondidas
            st.error("Por favor, responda todas las preguntas antes de enviar.")
            for index in preguntas_no_respondidas:
                st.markdown(
                    f"**Pregunta {index + 1}: No respondida**", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# Ejecutar la función principal
if __name__ == "__main__":
    mostrar_encuesta()
