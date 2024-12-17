import streamlit as st
import pandas as pd
import qrcode
from datetime import datetime
import random
from io import BytesIO

# Función para generar un ID aleatorio


def generar_id():
    return random.randint(100000, 999999)

# Generar código QR


def generar_qr(numero_control):
    qr = qrcode.make(f"ID de control: {numero_control}")
    img_byte_arr = BytesIO()
    qr.save(img_byte_arr, format="PNG")
    return img_byte_arr.getvalue()

# Cargar preguntas desde Excel


def cargar_preguntas():
    return pd.read_excel("preguntas.xlsx")

# Mostrar encuesta principal


def mostrar_encuesta():
    st.set_page_config(page_title="Encuesta UCAB", layout="wide")

    # --- Encabezado ---
    numero_control = generar_id()
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    qr_img = generar_qr(numero_control)

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
    <div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px; border: 1px solid #ccc;">
        <h4>Instrucciones</h4>
        <p><strong>Gracias por participar en esta encuesta. La misma es anónima y tiene fines estrictamente académicos. Lea cuidadosamente y seleccione la opción que considere pertinente, al culminar presione Enviar.</strong></p>
    </div>
    """, unsafe_allow_html=True)

    # --- Datos demográficos ---
    st.markdown("### **Datos Demográficos**")
    demograficos = {
        "Edad": st.number_input("¿Cuál es su edad?", min_value=18, max_value=99, step=1),
        "Género": st.selectbox("Seleccione su género:", ["", "Masculino", "Femenino", "Otro"]),
        "Ciudad": st.text_input("¿En qué ciudad reside?"),
        "Ingresos": st.selectbox("Rango de ingresos:", ["", "Bajo", "Medio", "Alto"]),
        "Educación": st.selectbox("Nivel educativo:", ["", "Primaria", "Secundaria", "Universitaria", "Posgrado"])
    }

    # --- Cargar y mostrar preguntas ---
    preguntas_df = cargar_preguntas()
    respuestas = {}
    preguntas_faltantes = []

    st.markdown("### **Preguntas de la Encuesta**")
    for idx, row in preguntas_df.iterrows():
        pregunta = row['pregunta']
        opciones = row['escala'].split(";")

        with st.container():
            st.markdown(
                f"<div style='border: 2px solid #007bff; padding: 10px; border-radius: 5px; color: blue;'><b>{
                    idx+1}. {pregunta}</b></div>",
                unsafe_allow_html=True
            )
            respuesta = st.radio("", opciones, key=f"pregunta_{
                                 idx}", index=None, horizontal=True)
            respuestas[idx] = respuesta

    # Contador de preguntas respondidas
    respondidas = sum(1 for r in respuestas.values() if r)
    total_preguntas = len(preguntas_df) + len(demograficos)
    st.info(f"Preguntas respondidas: {respondidas} / {len(preguntas_df)}")

    # --- Botón enviar ---
    if st.button("Enviar Encuesta"):
        # Identificar preguntas no respondidas
        preguntas_faltantes = [idx+1 for idx, r in respuestas.items() if not r]

        if all(demograficos.values()) and not preguntas_faltantes:
            st.success("¡Gracias por participar en la encuesta!")
            st.balloons()

            # Simular guardado en base de datos
            with open("respuestas_guardadas.txt", "w") as file:
                file.write(f"ID de Control: {
                           numero_control}\nFecha y Hora: {fecha_hora}\n")
                for k, v in demograficos.items():
                    file.write(f"{k}: {v}\n")
                for idx, resp in respuestas.items():
                    file.write(f"Pregunta {idx+1}: {resp}\n")

            st.stop()

        else:
            # Mostrar advertencias
            if preguntas_faltantes:
                for faltante in preguntas_faltantes:
                    st.markdown(f"<div style='color: red;'>Falta responder la pregunta {
                                faltante}</div>", unsafe_allow_html=True)

            if not all(demograficos.values()):
                st.error("Por favor, complete todos los datos demográficos.")


# --- Ejecutar aplicación ---
if __name__ == "__main__":
    mostrar_encuesta()
