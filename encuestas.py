import streamlit as st
import pandas as pd
import random
import datetime
from firebase_admin import credentials, firestore, initialize_app, get_app
import os
from dotenv import load_dotenv
import qrcode
from PIL import Image
import io

# Cargar variables de entorno
load_dotenv()
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")

# Inicializar Firebase, pero solo si no se ha inicializado previamente
try:
    app = get_app()
except ValueError as e:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS)
    app = initialize_app(cred)

# Conectar a Firestore
db = firestore.client()

# Generar un ID único


def generar_id():
    return random.randint(100000, 999999)


# URL del archivo de preguntas
url_preguntas = 'https://raw.githubusercontent.com/ChuchuSalazar/encuesta/main/preguntas.xlsx'

# Cargar preguntas
df_preguntas = pd.read_excel(url_preguntas, header=0)
df_preguntas.columns = ['item', 'pregunta', 'escala', 'posibles_respuestas']

# Guardar respuestas en Firebase


def guardar_respuestas(respuestas, numero_control):
    id_encuesta = f"ID_{numero_control}"
    fecha = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    data = {'FECHA': fecha, 'NUMERO_CONTROL': numero_control}
    for key, value in respuestas.items():
        data[key] = value

    db.collection('respuestas').document(id_encuesta).set(data)

# Generar un código QR con el número de control y agregar logo


def generar_qr(numero_control, logo_path=None):
    qr = qrcode.QRCode(
        version=1,  # Controlar el tamaño del QR
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,  # Ajustar el tamaño de los cuadros
        border=4,
    )
    qr.add_data(numero_control)
    qr.make(fit=True)

    # Crear imagen del QR
    img_qr = qr.make_image(fill='black', back_color='white').convert('RGB')

    if logo_path:
        logo = Image.open(logo_path)
        logo = logo.resize((40, 40))  # Ajustar el tamaño del logo
        qr_width, qr_height = img_qr.size
        logo_pos = ((qr_width - logo.width) // 2,
                    (qr_height - logo.height) // 2)
        img_qr.paste(logo, logo_pos, logo)

    # Convertir la imagen a un formato adecuado para mostrar en Streamlit
    img_byte_arr = io.BytesIO()
    img_qr.save(img_byte_arr)
    img_byte_arr.seek(0)
    return img_byte_arr

# Mostrar encuesta


def mostrar_encuesta():
    st.title("Encuesta de Hábitos de Ahorro")
    st.write("Por favor, responda todas las preguntas obligatorias.")

    # Mostrar la fecha y hora de la encuesta
    fecha_hora = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    st.write(f"Fecha y hora de inicio: {fecha_hora}")

    # Generar un número de control
    numero_control = generar_id()

    # Mostrar el número de control como texto
    st.write(f"**Número de Control:** {numero_control}")

    # Mostrar el número de control en formato QR
    qr_img = generar_qr(numero_control, logo_path="logo_ucab.jpg")
    st.image(qr_img, use_column_width=False, width=150)

    # Crear recuadro para las preguntas demográficas
    st.markdown("<div style='background-color: #e0e0e0; padding: 10px;'>",
                unsafe_allow_html=True)
    st.subheader("Datos Demográficos")

    # Preguntas Demográficas con validación de respuestas
    sexo = st.radio("1. ¿Cuál es su sexo?", [
                    "Masculino", "Femenino", "Otro"], index=0)
    rango_edad = st.radio("2. ¿En qué rango de edad se encuentra?", [
                          "18-24", "25-34", "35-44", "45-54", "55+"])
    ingreso = st.radio("3. ¿Cuál es su rango de ingresos mensuales?", [
                       "Menos de $500", "$500 - $1000", "$1000 - $2000", "Más de $2000"])
    ciudad = st.selectbox("4. ¿En qué ciudad reside?", [
                          "Caracas", "Valencia", "Maracaibo", "Barquisimeto", "Otra"])
    nivel_educacion = st.selectbox("5. ¿Cuál es su nivel de educación?", [
                                   "Secundaria", "Pregrado", "Posgrado"])

    # Aquí agregarías las demás preguntas de la encuesta, pero por ahora mostramos solo las demográficas

    st.markdown("</div>", unsafe_allow_html=True)  # Cerrar recuadro

    # Botón para enviar
    if st.button("Enviar"):
        respuestas = {
            "sexo": sexo,
            "rango_edad": rango_edad,
            "ingreso": ingreso,
            "ciudad": ciudad,
            "nivel_educacion": nivel_educacion,
            # Añadir las respuestas de las otras preguntas
        }

        # Validación de respuestas
        todas_contestadas = all(
            [sexo, rango_edad, ingreso, ciudad, nivel_educacion])

        if todas_contestadas:
            # Guardar respuestas
            guardar_respuestas(respuestas, numero_control)
            st.success("¡Gracias por completar la encuesta!")
            st.balloons()

            # Deshabilitar botón y mostrar mensaje
            st.write(
                "La encuesta ha sido cerrada. No es posible volver a contestar.")

            # Cambiar color de los recuadros a azul (ya respondidos)
            st.markdown("""
                <style>
                    .stRadio, .stSelectbox { 
                        border: 2px solid #2196F3;
                        background-color: #E3F2FD;
                    }
                </style>
                """, unsafe_allow_html=True)
        else:
            st.error("Por favor, responda todas las preguntas.")


# Ejecutar la encuesta
if __name__ == '__main__':
    mostrar_encuesta()
