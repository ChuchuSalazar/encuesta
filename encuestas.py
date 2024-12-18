import streamlit as st
import pandas as pd
import random
import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# Iniciar la conexión con Firebase
# Asegúrate de usar la ruta correcta
cred = credentials.Certificate("ruta/a/tu/archivo/firebase.json")
firebase_admin.initialize_app(cred)

# Referencia a Firestore
db = firestore.client()

# Cargar las preguntas desde el archivo Excel


def cargar_preguntas():
    # Leer el archivo Excel
    df = pd.read_excel("preguntas.xlsx")

    # Ajustar las columnas a minúsculas
    # Convertir los nombres de las columnas a minúsculas
    df.columns = [col.lower() for col in df.columns]

    preguntas = []
    for _, row in df.iterrows():
        pregunta = {
            "item": row['item'],
            "pregunta": row['pregunta'],
            "escala": row['escala'],
            # Dividir las respuestas posibles por coma
            "posibles_respuestas": row['posibles_respuestas'].split(',')
        }
        preguntas.append(pregunta)
    return preguntas

# Función para generar un ID aleatorio


def generar_id():
    return random.randint(1000, 9999)

# Función para almacenar la respuesta en Firestore


def guardar_respuestas(respuestas, id_encuesta):
    fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Convertir las respuestas a tipo str para evitar el error de tipo
    respuestas_str = {key: str(value) for key, value in respuestas.items()}

    data = {
        "FECHA": fecha_hora,
        "ID": id_encuesta,
        **respuestas_str  # Usar las respuestas convertidas a str
    }

    try:
        db.collection("encuestas").document(str(id_encuesta)).set(data)
        print("Datos guardados en Firestore")
    except Exception as e:
        print(f"Error al guardar en Firestore: {e}")

# Función para mostrar la encuesta


def mostrar_encuesta():
    preguntas = cargar_preguntas()
    id_encuesta = generar_id()

    st.title("Encuesta de Ahorro")

    # Mostrar la fecha, hora y número de control
    st.sidebar.write(f"Fecha y hora: {
                     datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.sidebar.write(f"ID de encuesta: {id_encuesta}")

    # Panel izquierdo con instrucciones
    with st.sidebar:
        # Ajusta la ruta de la imagen si es necesario
        st.image("ucab_logo.jpg", width=200)
        st.markdown("### Instrucciones")
        st.markdown("""
        **Gracias por participar en esta encuesta. La misma es anónima y tiene fines estrictamente académicos para una tesis doctoral.**
        Lea cuidadosamente y seleccione la opción que considere pertinente, al culminar presione Enviar.
        """)

    # Respuestas iniciales
    respuestas = {
        "sexo": None,
        "rango_eda": None,
        "rango_ingreso": None,
        "nivel_educativo": None,
        "ciudad": "Caracas"  # Valor por defecto para ciudad
    }

    # Información General
    st.subheader("Información General")

    sexo = st.radio("Sexo", ['M', 'F'], key="sexo")
    respuestas["sexo"] = sexo

    rango_eda = st.selectbox(
        "Rango de Edad", ['18-24', '25-34', '35-44', '45-54', '55+'], key="rango_eda")
    respuestas["rango_eda"] = rango_eda

    rango_ingreso = st.selectbox("Rango de Ingreso Familiar", [
                                 '1-100', '101-300', '301-600', '601-1000', '1001-1500', '1501-3500', 'más de 3500'], key="rango_ingreso")
    respuestas["rango_ingreso"] = rango_ingreso

    nivel_educativo = st.radio("Nivel Educativo", [
                               'Básico', 'Licenciado', 'Maestría', 'Doctorado'], key="nivel_educativo")
    respuestas["nivel_educativo"] = nivel_educativo

    ciudad = st.selectbox("Ciudad", [
                          'Caracas', 'Maracaibo', 'Valencia', 'Barquisimeto', 'Maracay'], key="ciudad")
    respuestas["ciudad"] = ciudad

    st.markdown("### Preguntas")

    # Mostrar las preguntas
    for pregunta in preguntas:
        st.write(pregunta["pregunta"])
        respuesta = st.radio(
            pregunta["pregunta"], pregunta["posibles_respuestas"], key=pregunta["item"])
        respuestas[pregunta["item"]] = respuesta

    # Validación de respuestas y envío
    submit_button = st.button("Enviar")
    if submit_button:
        preguntas_no_respondidas = [
            key for key, value in respuestas.items() if value is None]
        if preguntas_no_respondidas:
            st.warning(f"Por favor, responda las siguientes preguntas: {
                       ', '.join(map(str, preguntas_no_respondidas))}")
        else:
            # Deshabilitar el botón "Enviar" después de procesar la encuesta
            st.session_state["enviado"] = True
            guardar_respuestas(respuestas, id_encuesta)
            st.success("Gracias por participar en la encuesta.")
            st.balloons()  # Efecto de globos

    # Deshabilitar el botón "Enviar" si ya fue procesada la encuesta
    if "enviado" in st.session_state and st.session_state["enviado"]:
        st.warning(
            "La encuesta ya ha sido enviada y no puede ser respondida nuevamente.")
        st.button("Enviar", disabled=True)


# Ejecutar la aplicación
if __name__ == "__main__":
    mostrar_encuesta()
