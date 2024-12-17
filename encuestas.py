import streamlit as st
import pandas as pd
import random
from datetime import datetime

# Función para generar un ID aleatorio


def generar_id():
    return random.randint(100000, 999999)

# Cargar preguntas desde Excel


def cargar_preguntas():
    try:
        preguntas_df = pd.read_excel("preguntas.xlsx")
        return preguntas_df
    except FileNotFoundError:
        st.error(
            "Error: No se encontró el archivo preguntas.xlsx. Asegúrate de colocarlo en la misma carpeta.")
        return None

# Función principal


def mostrar_encuesta():
    st.set_page_config(page_title="Encuesta UCAB", layout="wide")

    # --- Encabezado ---
    numero_control = generar_id()
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    col1, col2 = st.columns([8, 2])
    with col1:
        st.title("Encuesta de Investigación - UCAB")
        st.subheader(f"Fecha y hora: {fecha_hora}")
        st.write(f"**Número de Control:** {numero_control}")
    with col2:
        st.image("logo_ucab.jpg", use_column_width=True)

    # --- CSS Personalizado ---
    st.markdown("""
        <style>
            .marco-azul {
                border: 2px solid #0056b3;
                background-color: #e6f0ff;
                padding: 20px;
                border-radius: 10px;
            }
            .titulo {
                color: #0056b3;
                text-align: center;
                font-size: 20px;
                font-weight: bold;
            }
            .boton-grande label {
                display: inline-block;
                padding: 15px;
                margin: 5px;
                border: 2px solid #0056b3;
                border-radius: 5px;
                background-color: #f5f9ff;
                color: #0056b3;
                font-weight: bold;
                text-align: center;
                cursor: pointer;
                width: 120px;
            }
        </style>
    """, unsafe_allow_html=True)

    # --- Marco Azul Claro para Datos Demográficos ---
    st.markdown('<div class="marco-azul">', unsafe_allow_html=True)
    st.markdown('<div class="titulo">Datos Demográficos</div>',
                unsafe_allow_html=True)

    # --- Datos Demográficos ---
    # Género
    st.markdown("**Seleccione su género:**")
    col1, col2, col3 = st.columns(3)
    sexo = None
    with col1:
        if st.button("🧑‍💼 Hombre", key="hombre"):
            sexo = "Masculino"
    with col2:
        if st.button("👩‍💼 Mujer", key="mujer"):
            sexo = "Femenino"
    with col3:
        if st.button("🌈 Otro", key="otro"):
            sexo = "Otro"

    # Rango de Edad
    st.markdown("**Seleccione su rango de edad:**")
    rango_edad = st.slider("Rango de edad:", min_value=18,
                           max_value=99, value=25, step=1)

    # Rango de Salario
    st.markdown("**Indique su rango de salario mensual (en USD):**")
    rango_salario = st.number_input(
        "Ingrese su salario:", min_value=0, max_value=10000, step=50)

    # Nivel Educativo
    st.markdown("**Seleccione su nivel educativo:**")
    educacion = st.radio(
        "Nivel educativo:",
        options=["Primaria", "Secundaria", "Universitaria", "Posgrado"],
        horizontal=True,
        label_visibility="collapsed"
    )

    # Ciudad
    st.markdown("**Ciudad de residencia:**")
    ciudad = st.text_input("Ciudad:", "Caracas")

    st.markdown("</div>", unsafe_allow_html=True)  # Cerrar marco azul

    # --- Cargar preguntas ---
    st.markdown("### Preguntas de la Encuesta")
    preguntas_df = cargar_preguntas()
    if preguntas_df is not None:
        respuestas = {}
        contador_respondidas = 0

        for index, row in preguntas_df.iterrows():
            pregunta = row['pregunta']
            escala = row['escala'].split(";")
            with st.container():
                st.markdown(
                    f"<div style='color: blue; border: 1px solid #0056b3; padding: 10px; border-radius: 5px; margin-bottom: 5px;'>"
                    f"<strong>{index + 1}. {pregunta}</strong></div>",
                    unsafe_allow_html=True
                )
                respuesta = st.radio("", options=escala, key=f"pregunta_{
                                     index}", index=None, horizontal=True)
                respuestas[f"pregunta_{index}"] = respuesta
                if respuesta:
                    contador_respondidas += 1

        # Contador de preguntas respondidas
        st.info(f"Preguntas respondidas: {
                contador_respondidas} / {len(preguntas_df)}")

        # --- Botón de Enviar ---
        enviar_btn = st.button("Enviar Encuesta")
        if enviar_btn:
            faltantes = [k for k, v in respuestas.items() if not v]
            if len(faltantes) == 0 and sexo and educacion and rango_salario and ciudad:
                st.success("¡Gracias por responder la encuesta!")
                st.balloons()

                # Guardar respuestas
                with open("respuestas_guardadas.txt", "w") as file:
                    file.write(f"ID Control: {
                               numero_control}\nFecha y Hora: {fecha_hora}\n")
                    file.write("Datos Demográficos:\n")
                    file.write(f"Género: {sexo}\nEdad: {
                               rango_edad}\nSalario: {rango_salario}\n")
                    file.write(f"Nivel Educativo: {
                               educacion}\nCiudad: {ciudad}\n")
                    file.write("Respuestas de la Encuesta:\n")
                    for k, v in respuestas.items():
                        file.write(f"{k}: {v}\n")
            else:
                st.error(
                    "Por favor, responda todas las preguntas y complete los datos demográficos.")


# --- Ejecutar aplicación ---
if __name__ == "__main__":
    mostrar_encuesta()
