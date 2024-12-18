import streamlit as st
import random
import datetime
import pandas as pd

# Función para mostrar los datos demográficos


def mostrar_datos_demograficos():
    st.sidebar.header("Datos Demográficos")

    # Recuadro azul para los datos demográficos
    # Usar 'expander' en lugar de 'beta_expander'
    with st.sidebar.expander("Datos Demográficos", expanded=True):
        sexo = st.radio("Sexo", ["Masculino", "Femenino"], key="sexo")
        edad = st.slider("Edad", 18, 100, 25)
        ciudad = st.selectbox("Ciudad", [
                              "Caracas", "Valencia", "Maracay", "Maracaibo", "Barquisimeto"], key="ciudad")
        salario = st.multiselect("Rango de salario", [
                                 "Menos de 1.000.000", "1.000.000 - 2.000.000", "Más de 2.000.000"], key="salario")
        nivel_educativo = st.selectbox("Nivel Educativo", [
                                       "Primaria", "Secundaria", "Técnico", "Universitario"], key="nivel_educativo")

    return sexo, edad, ciudad, salario, nivel_educativo

# Función para mostrar las preguntas y opciones


def mostrar_preguntas():
    # Aquí se simulan las preguntas. Usualmente deberías leerlas de un archivo Excel.
    preguntas = [
        {"item": 1, "pregunta": "Prefiero evitar perder $100 que ganar $200.", "escala": 5, "posibles_respuestas": [
            "Totalmente en desacuerdo", "En desacuerdo", "Neutral", "De acuerdo", "Totalmente de acuerdo"]},
        {"item": 2, "pregunta": "Prefiero ganar $100 que perder $200.", "escala": 5, "posibles_respuestas": [
            "Totalmente en desacuerdo", "En desacuerdo", "Neutral", "De acuerdo", "Totalmente de acuerdo"]},
        {"item": 3, "pregunta": "Prefiero perder $100 que ganar $200.", "escala": 5, "posibles_respuestas": [
            "Totalmente en desacuerdo", "En desacuerdo", "Neutral", "De acuerdo", "Totalmente de acuerdo"]},
        # Añadir más preguntas aquí según el archivo Excel.
    ]

    respuestas = {}

    for pregunta in preguntas:
        # Cambié 'beta_expander' a 'expander'
        with st.expander(f"{pregunta['item']}. {pregunta['pregunta']}", expanded=True):
            opciones = pregunta["posibles_respuestas"]
            respuesta = st.radio(f"Selecciona una opción",
                                 opciones, key=f"respuesta_{pregunta['item']}")
            respuestas[pregunta["item"]] = respuesta

    return respuestas

# Función principal para mostrar la encuesta


def app():
    # Título
    st.title("Encuesta de Tesis Doctoral")

    # Texto introductorio
    st.markdown(
        """
        <div style="background-color:#f2f2f2; padding:10px; border-radius:5px;">
        Gracias por participar en esta encuesta. La misma es anónima y tiene fines estrictamente académicos para una tesis doctoral. 
        Lea cuidadosamente y seleccione la opción que considere pertinente. Al culminar, presione "Enviar".
        </div>
        """, unsafe_allow_html=True)

    # Mostrar datos demográficos
    sexo, edad, ciudad, salario, nivel_educativo = mostrar_datos_demograficos()

    # Mostrar las preguntas
    respuestas = mostrar_preguntas()

    # Botón para enviar respuestas
    if st.button("Enviar"):
        # Validar si todas las preguntas han sido respondidas
        respuestas_incompletas = [
            item for item, respuesta in respuestas.items() if respuesta is None]

        if respuestas_incompletas:
            # Si hay preguntas no respondidas, se marcan en rojo y se muestra mensaje
            for item in respuestas_incompletas:
                st.markdown(f"<div style='border:2px solid red; border-radius:5px; padding:10px;'>Pregunta {
                            item} no respondida</div>", unsafe_allow_html=True)
            st.error("Por favor, responda todas las preguntas antes de enviar.")
        else:
            # Si todas las preguntas están respondidas, mostrar un mensaje de agradecimiento
            st.success("Gracias por participar en la investigación.")
            st.balloons()

            # Guardar las respuestas en un archivo o base de datos (esto lo harás según tus necesidades)
            # ID aleatorio para la encuesta
            encuesta_id = random.randint(1000, 9999)
            fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Guardar respuestas en un DataFrame de ejemplo
            data = {
                "id_encuesta": encuesta_id,
                "fecha_hora": fecha_hora,
                "sexo": sexo,
                "edad": edad,
                "ciudad": ciudad,
                # Convertir lista de salarios seleccionados a cadena
                "salario": ", ".join(salario),
                "nivel_educativo": nivel_educativo,
                "respuestas": respuestas
            }

            df = pd.DataFrame([data])
            # Guardar en CSV como ejemplo
            df.to_csv(f"respuestas_encuesta_{encuesta_id}.csv", index=False)

            # Mostrar nueva página para evitar que se vuelva a contestar
            st.write(
                "Encuesta enviada exitosamente. No puede ser respondida nuevamente.")


# Ejecutar la aplicación
if __name__ == "__main__":
    app()
