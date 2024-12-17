import streamlit as st
import pandas as pd
import qrcode
from datetime import datetime
import random
from io import BytesIO

# --- Función para generar un ID aleatorio ---


def generar_id():
    return random.randint(100000, 999999)

# --- Función para generar un código QR a partir del ID de control ---


def generar_qr(numero_control):
    qr = qrcode.make(f"ID de control: {numero_control}")
    img_byte_arr = BytesIO()
    qr.save(img_byte_arr, format="PNG")
    return img_byte_arr.getvalue()

# --- Cargar preguntas desde Excel ---


def cargar_preguntas():
    try:
        preguntas_df = pd.read_excel("preguntas.xls")
        return preguntas_df
    except Exception as e:
        st.error(f"Error al cargar el archivo Excel: {e}")
        return pd.DataFrame()

# --- Función principal ---


def mostrar_encuesta():
    st.set_page_config(page_title="Encuesta UCAB", layout="wide")

    # --- Generar ID de control y fecha/hora ---
    numero_control = generar_id()
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    qr_img = generar_qr(numero_control)

    # --- Encabezado con el logo y QR ---
    col1, col2 = st.columns([8, 2])
    with col1:
        st.title("Encuesta de Investigación - UCAB")
        st.subheader(f"Fecha y hora: {fecha_hora}")
        st.write(f"**Número de Control:** {numero_control}")
    with col2:
        st.image("logo_ucab.jpg", use_container_width=True)
        st.image(qr_img, width=100)

    # --- Texto introductorio ---
    st.markdown("""
    <div style="border: 1px solid #888; background-color: #f0f0f0; padding: 10px; border-radius: 5px;">
        <h4 style="color: #333;">Instrucciones</h4>
        <p><strong>Gracias por participar en esta encuesta. La misma es anónima y tiene fines estrictamente académicos para una tesis doctoral. Lea cuidadosamente y seleccione la opción que considere pertinente, al culminar presione Enviar.</strong></p>
    </div>
    """, unsafe_allow_html=True)

    # --- Preguntas Demográficas ---
    st.markdown("### **Datos Demográficos**")
    with st.container():
        col1, col2 = st.columns(2)
        demograficos = {}
        demograficos['Edad'] = col1.number_input(
            "¿Cuál es su edad?", min_value=18, max_value=99, step=1)
        demograficos['Género'] = col2.selectbox(
            "Seleccione su género:", ["", "Masculino", "Femenino", "Otro"])
        demograficos['Ciudad'] = col1.text_input("¿En qué ciudad reside?")
        demograficos['Ingresos'] = col2.selectbox(
            "Rango de ingresos:", ["", "Bajo", "Medio", "Alto"])
        demograficos['Educación'] = col1.selectbox(
            "Nivel educativo:", ["", "Primaria", "Secundaria", "Universitaria", "Posgrado"])

    # --- Cargar preguntas desde Excel ---
    preguntas_df = cargar_preguntas()
    if preguntas_df.empty:
        st.stop()

    # --- Mostrar preguntas ---
    st.markdown("### **Preguntas de la Encuesta**")
    respuestas = {}
    contador_respondidas = 0

    for index, row in preguntas_df.iterrows():
        pregunta = row['pregunta']
        escala = str(row['escala']).split(";") if pd.notnull(
            row['escala']) else []  # Manejo seguro

        # Pregunta dentro de un marco azul
        with st.container():
            st.markdown(
                f"<div style='border: 2px solid blue; padding: 10px; border-radius: 5px; margin: 5px;'>"
                f"**{index + 1}. {pregunta}**</div>",
                unsafe_allow_html=True
            )
            respuesta = st.radio("", options=escala, key=f"pregunta_{
                                 index}", index=None, horizontal=True)
            respuestas[f"pregunta_{index}"] = respuesta
            if respuesta:
                contador_respondidas += 1

    # --- Contador de preguntas respondidas ---
    st.info(f"Preguntas respondidas: {
            contador_respondidas} / {len(preguntas_df)}")

    # --- Botón de enviar ---
    enviar_btn = st.button("Enviar Encuesta")
    if enviar_btn:
        faltantes = [k for k, v in respuestas.items() if not v]
        if len(faltantes) == 0 and all(demograficos.values()):
            # Guardar respuestas
            with open("respuestas_guardadas.txt", "w") as file:
                file.write(f"ID Control: {
                           numero_control}\nFecha y Hora: {fecha_hora}\n")
                file.write("Datos Demográficos:\n")
                for k, v in demograficos.items():
                    file.write(f"{k}: {v}\n")
                file.write("\nRespuestas de la Encuesta:\n")
                for k, v in respuestas.items():
                    file.write(f"{k}: {v}\n")

            # Mensaje de éxito
            st.success("¡Gracias por responder la encuesta!")
            st.balloons()
            st.stop()
        else:
            # Mostrar preguntas faltantes
            st.error("Por favor, responda todas las preguntas antes de enviar.")
            for k, v in respuestas.items():
                if not v:
                    numero_pregunta = int(k.split("_")[1]) + 1
                    st.markdown(f"<div style='color: red;'>Falta responder la pregunta: {numero_pregunta}</div>",
                                unsafe_allow_html=True)


# --- Ejecutar aplicación ---
if __name__ == "__main__":
    mostrar_encuesta()
