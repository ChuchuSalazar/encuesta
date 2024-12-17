import streamlit as st
import pandas as pd
import random
import qrcode
from datetime import datetime

# Función para generar el ID aleatorio de la encuesta


def generar_id_encuesta():
    return random.randint(100000, 999999)

# Función para generar el código QR


def generar_qr(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img_qr = qr.make_image(fill='black', back_color='white')
    return img_qr

# Leer las preguntas desde un archivo Excel (ajustar la ruta a tu archivo)


def cargar_preguntas():
    preguntas_df = pd.read_excel('preguntas.xlsx')
    return preguntas_df

# Función para mostrar la encuesta


def mostrar_encuesta():
    # Título y mensaje introductorio
    st.title("Instrucciones")
    st.markdown("**Gracias por participar en esta encuesta. La misma es anónima y tiene fines estrictamente académicos para una tesis doctoral. Lea cuidadosamente y seleccione la opción que considere pertinente, al culminar presione Enviar**")

    # Logo UCAB en la esquina superior derecha
    st.image("logo_ucab.jpg", width=100, use_column_width=False)

    # Mostrar la fecha y hora del llenado
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.write(f"Fecha y Hora: {fecha_hora}")

    # Generar un ID aleatorio para la encuesta
    numero_control = generar_id_encuesta()
    st.write(f"ID Encuesta: {numero_control}")

    # Generar el QR del ID de la encuesta
    qr_img = generar_qr(numero_control)
    st.image(qr_img, width=100)

    # Cargar las preguntas desde el archivo Excel
    preguntas_df = cargar_preguntas()

    # Mostrar preguntas demográficas en un solo recuadro
    st.markdown("### Datos Demográficos")
    with st.container():
        # Recorrido para mostrar las preguntas
        respuestas = {}
        for i, row in preguntas_df.iterrows():
            pregunta = row['Pregunta']
            tipo = row['Tipo']
            # Asegúrate de que la columna Escala sea numérica
            escala = int(row['Escala'])
            key = f"pregunta_{i}"

            # Mostrar preguntas con su tipo correspondiente
            if tipo == 'checklist':
                respuestas[key] = st.multiselect(
                    pregunta, options=[f"Opción {i}" for i in range(1, escala + 1)])
            elif tipo == 'radio':
                respuestas[key] = st.radio(
                    pregunta, options=[f"Option {i}" for i in range(1, escala + 1)])
            elif tipo == 'combo':
                respuestas[key] = st.selectbox(
                    pregunta, options=[f"Option {i}" for i in range(1, escala + 1)])

            # Control de respuesta y color de los recuadros
            if respuestas[key]:
                st.markdown(f'<div style="background-color: #B3D9FF; padding: 10px; border-radius: 5px;">{
                            pregunta}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="background-color: #FF6666; padding: 10px; border-radius: 5px;">{
                            pregunta}</div>', unsafe_allow_html=True)

    # Contador de respuestas
    contador_respuestas = sum(1 for value in respuestas.values() if value)
    st.write(f"Respuestas completadas: {
             contador_respuestas}/{len(preguntas_df)}")

    # Botón para enviar la encuesta
    if contador_respuestas == len(preguntas_df):
        enviar_disabled = False
    else:
        enviar_disabled = True

    # Mostrar el botón
    boton_enviar = st.button('Enviar Encuesta', disabled=enviar_disabled)

    if boton_enviar:
        # Guardar respuestas en la base de datos (esto se asume como un proceso de backend)
        st.write("Gracias por completar la encuesta. ¡Globos de celebración aquí! 🎉🎈")

        # Cambiar la página, mostrar agradecimiento y cerrar la conexión de base de datos (simulado)
        st.write("La encuesta ha sido cerrada.")
        st.stop()


# Ejecutar la función para mostrar la encuesta
if __name__ == "__main__":
    mostrar_encuesta()
