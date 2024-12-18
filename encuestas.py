import streamlit as st
import pandas as pd
import random
import datetime

# Función para cargar las preguntas desde el archivo Excel


def cargar_preguntas():
    archivo_preguntas = "preguntas.xlsx"  # Ruta de tu archivo Excel
    df = pd.read_excel(archivo_preguntas)

    preguntas = []
    for index, row in df.iterrows():
        pregunta = {
            "item": row['item'],
            "pregunta": row['pregunta'],
            "escala": row['escala'],
            # Separar las opciones si están en una cadena
            "posibles_respuestas": row['posibles_respuestas'].split(',')
        }
        preguntas.append(pregunta)

    return preguntas

# Función para mostrar los datos demográficos


def mostrar_datos_demograficos():
    st.sidebar.header("Datos Demográficos")

    # Recuadro azul para los datos demográficos
    with st.sidebar.expander("Datos Demográficos", expanded=True):
        sexo = st.radio("Sexo", ["Masculino", "Femenino"], key="sexo")
        edad = st.slider("Edad", 18, 100, 25)
        ciudad = st.selectbox("Ciudad", [
                              "Caracas", "Valencia", "Maracay", "Maracaibo", "Barquisimeto"], key="ciudad")

        # Rango de salario como selección única
        salario = st.selectbox("Rango de salario",
                               ["1-100", "101-300", "301-600", "601-1000",
                                "1001-1500", "1501-3500", "Más de 3500"],
                               key="salario")

        nivel_educativo = st.selectbox("Nivel Educativo", [
                                       "Primaria", "Secundaria", "Técnico", "Universitario"], key="nivel_educativo")

    return sexo, edad, ciudad, salario, nivel_educativo

# Función para mostrar las preguntas y opciones


def mostrar_preguntas(preguntas):
    respuestas = {}
    preguntas_no_respondidas = []

    for pregunta in preguntas:
        with st.expander(f"{pregunta['item']}. {pregunta['pregunta']}", expanded=True):
            opciones = pregunta["posibles_respuestas"]
            respuesta = st.radio(f"Selecciona una opción",
                                 opciones, key=f"respuesta_{pregunta['item']}")

            # Validación: Si no se responde, agregar a la lista de no respondidas
            if not respuesta:
                preguntas_no_respondidas.append(pregunta["item"])

            respuestas[pregunta["item"]] = respuesta

    return respuestas, preguntas_no_respondidas

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

    # Cargar las preguntas desde el archivo Excel
    preguntas = cargar_preguntas()

    # Mostrar las preguntas
    respuestas, preguntas_no_respondidas = mostrar_preguntas(preguntas)

    # Contador de preguntas no respondidas
    contador_respuestas = len(respuestas) - len(preguntas_no_respondidas)
    st.sidebar.write(f"Preguntas Respondidas: {
                     contador_respuestas}/{len(preguntas)}")

    # Botón para enviar respuestas
    if st.button("Enviar"):
        if preguntas_no_respondidas:
            # Si hay preguntas no respondidas, se marcan en rojo
            for item in preguntas_no_respondidas:
                st.markdown(f"<div style='border:2px solid red; border-radius:5px; padding:10px;'>Pregunta {
                            item} no respondida</div>", unsafe_allow_html=True)
            st.error("Por favor, responda todas las preguntas antes de enviar.")
        else:
            # Si todas las preguntas están respondidas
            st.success("Gracias por participar en la investigación.")
            st.balloons()

            # Guardar las respuestas en un archivo o base de datos (esto lo harás según tus necesidades)
            encuesta_id = random.randint(1000, 9999)
            fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Guardar respuestas en un DataFrame de ejemplo
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
            # Guardar en CSV como ejemplo
            df.to_csv(f"respuestas_encuesta_{encuesta_id}.csv", index=False)

            # Mostrar nueva página para evitar que se vuelva a contestar
            st.write(
                "Encuesta enviada exitosamente. No puede ser respondida nuevamente.")
            st.stop()  # Detiene la ejecución para no permitir más interacción


# Ejecutar la aplicación
if __name__ == "__main__":
    app()
