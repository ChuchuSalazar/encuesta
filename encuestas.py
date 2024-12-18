import streamlit as st
import pandas as pd
import random
from datetime import datetime

# Generar un ID aleatorio


def generar_id():
    return random.randint(100000, 999999)

# Cargar preguntas desde Excel


def cargar_preguntas():
    try:
        # Leer el archivo Excel asegurando que la primera fila sea usada como encabezado
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
        # Actualizado para evitar la advertencia
        st.image("logo_ucab.jpg", use_container_width=True)

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
                width: 150px;
            }
            .radio label {
                margin-right: 10px;
            }
            .boton-sexo {
                display: flex;
                justify-content: space-evenly;
                gap: 5px;
                align-items: center;
            }
            .red-border {
                border: 2px solid red;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 10px;
            }
            .blue-border {
                border: 2px solid blue;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

    # --- Marco Azul Claro para Información General ---
    st.markdown('<div class="marco-azul">', unsafe_allow_html=True)
    st.markdown('<div class="titulo">Información General</div>',
                unsafe_allow_html=True)

    # --- Datos Demográficos ---
    # Género
    st.markdown("**Seleccione su género:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        sexo = st.button("🧑 Hombre", key="hombre")
    with col2:
        sexo = st.button("👩 Mujer", key="mujer")
    with col3:
        sexo = st.button("🌈 Otro", key="otro")

    # Rango de Edad - Usar las opciones del código
    st.markdown("**Seleccione su rango de edad:**")
    rangos_edad = ["18-25", "26-35", "36-45", "46-55", "56+"]
    rango_edad = st.radio("Edad:", options=rangos_edad, key="rango_edad")

    # Rango de Salario - Usar las opciones del código
    st.markdown("**Seleccione su rango de salario mensual (en USD):**")
    rangos_salario = ["0-1000", "1001-5000", "5001-10000", "10001+"]
    salario = st.radio("Salario:", options=rangos_salario, key="rango_salario")

    # Nivel Educativo
    st.markdown("**Seleccione su nivel educativo:**")
    educacion = st.radio(
        "Nivel educativo:",
        options=["Primaria", "Secundaria", "Universitaria", "Posgrado"],
        horizontal=True,
        index=None,
        label_visibility="collapsed"
    )

    # Ciudad
    st.markdown("**Ciudad de residencia:**")
    ciudades = ["Caracas", "Maracaibo", "Valencia",
                "Barquisimeto", "Mérida", "San Cristóbal"]
    ciudad = st.selectbox("Selecciona tu ciudad:", opciones=ciudades, index=0)

    st.markdown("</div>", unsafe_allow_html=True)  # Cerrar marco azul

    # --- Cargar preguntas ---
    st.markdown("### Preguntas de la Encuesta")
    preguntas_df = cargar_preguntas()
    if preguntas_df is not None:
        respuestas = {}
        contador_respondidas = 0

        # Asegurarse de que las filas comienzan desde la segunda fila de datos (evitar usar la primera fila de encabezado)
        for index, row in preguntas_df.iterrows():
            if index == 0:  # Ignorar la primera fila de los nombres de las columnas
                continue

            pregunta = row['pregunta']

            # Validar si la columna 'posibles respuestas' existe
            if 'posibles respuestas' in row:
                posibles_respuestas = str(row['posibles respuestas']).split(
                    ",")  # Convertir a cadena antes de aplicar split()
            else:
                st.error(f"Error: La columna 'posibles respuestas' no se encuentra en la fila {
                         index + 1}")
                continue

            # Si la escala es mayor que 1, mostrar un radio button con las respuestas posibles
            with st.container():
                st.markdown(
                    f"<div style='color: blue; border: 1px solid #0056b3; padding: 10px; border-radius: 5px; margin-bottom: 5px;'>"
                    f"<strong>{index + 1}. {pregunta}</strong></div>",
                    unsafe_allow_html=True
                )
                if len(posibles_respuestas) > 1:
                    respuesta = st.radio("", options=posibles_respuestas, key=f"pregunta_{
                                         index}", index=None)
                else:
                    respuesta = st.text_input("", key=f"pregunta_{index}")
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
            if len(faltantes) == 0 and educacion and ciudad:
                st.success("¡Gracias por responder la encuesta!")
                st.balloons()
            else:
                for faltante in faltantes:
                    st.markdown(f"<div class='red-border'><strong>{
                                faltante}</strong> está incompleta.</div>", unsafe_allow_html=True)
                st.error(
                    "Por favor, responda todas las preguntas y complete los datos demográficos.")


# --- Ejecutar aplicación ---
if __name__ == "__main__":
    mostrar_encuesta()
