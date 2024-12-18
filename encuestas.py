import streamlit as st
import pandas as pd
import random
import datetime


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
            "posibles_respuestas": row['posibles_respuestas'].split(',')
        }
        preguntas.append(pregunta)
    return preguntas


# Función para mostrar los datos demográficos
def mostrar_datos_demograficos():
    st.sidebar.header("Datos Demográficos")

    # Recuadro azul para los datos demográficos
    with st.sidebar.container():
        st.markdown(
            """
            <div style="background-color:#add8e6; padding:10px; border-radius:5px;">
            <strong>Por favor complete los datos demográficos:</strong>
            </div>
            """, unsafe_allow_html=True)

        sexo = st.radio(
            "Sexo:", ["Masculino", "Femenino"], index=-1, key="sexo")
        edad = st.slider("Edad:", 18, 100, 25, key="edad")
        ciudad = st.selectbox("Ciudad:", [
            "Caracas", "Valencia", "Maracay", "Maracaibo", "Barquisimeto"], key="ciudad")
        salario = st.selectbox("Rango de salario:", [
            "1-100", "101-300", "301-600", "601-1000", "1001-1500", "1501-3500", "Más de 3500"], index=0, key="salario")
        nivel_educativo = st.radio("Nivel Educativo:", [
            "Primaria", "Secundaria", "Técnico", "Universitario"], index=-1, key="nivel_educativo")

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

            respuesta = st.radio("", options=pregunta["posibles_respuestas"],
                                 index=-1, key=f"respuesta_{pregunta['item']}")

            respuestas[pregunta["item"]] = respuesta

            if not respuesta:  # Si no hay respuesta seleccionada
                preguntas_no_respondidas.append(pregunta["item"])

    return respuestas, preguntas_no_respondidas


# Función principal para mostrar la encuesta
def app():
    st.title("Encuesta de Tesis Doctoral")

    # Fecha y hora del llenado de la encuesta
    fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.write(f"Fecha y hora de llenado: {fecha_hora}")

    # Texto introductorio
    st.markdown(
        """
        <div style="background-color:#f2f2f2; padding:10px; border-radius:5px;">
        <strong>Gracias por participar en esta encuesta.</strong><br>
        La misma es anónima y tiene fines estrictamente académicos para una tesis doctoral.<br>
        Lea cuidadosamente y seleccione la opción que considere pertinente. Al culminar, presione "Enviar".
        </div>
        """, unsafe_allow_html=True)

    # ID aleatorio para la encuesta
    encuesta_id = random.randint(1000, 9999)
    st.write(f"ID de Encuesta: {encuesta_id}")

    # Mostrar datos demográficos
    sexo, edad, ciudad, salario, nivel_educativo = mostrar_datos_demograficos()

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

            # Guardar las respuestas en un archivo o base de datos
            data = {
                "id_encuesta": encuesta_id,
                "fecha_hora": fecha_hora,
                "sexo": sexo,
                "edad": edad,
                "ciudad": ciudad,
                "salario": salario,
                "nivel_educativo": nivel_educativo,
                "respuestas": respuestas
            }
            df = pd.DataFrame([data])
            df.to_csv(f"respuestas_encuesta_{encuesta_id}.csv", index=False)
            st.write("Encuesta enviada exitosamente.")


# Ejecutar la aplicación
if __name__ == "__main__":
    app()
