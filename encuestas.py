import streamlit as st
import pandas as pd
import random
import datetime
from firebase_admin import credentials, initialize_app, db, get_app
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")

# Inicializar Firebase, pero solo si no se ha inicializado previamente
try:
    app = get_app()
except ValueError as e:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS)
    app = initialize_app(cred, {
        # Asegúrate de usar la URL correcta de tu Realtime Database
        "databaseURL": "https://encuestas-pca-default-rtdb.firebaseio.com/"
    })

# Conectar a Realtime Database
ref = db.reference("/respuestas")

# Generar un ID único


def generar_id():
    return random.randint(100000, 999999)


# URL del archivo de preguntas
url_preguntas = 'https://raw.githubusercontent.com/ChuchuSalazar/encuesta/main/preguntas.xlsx'

# Cargar preguntas
df_preguntas = pd.read_excel(url_preguntas, header=None)
df_preguntas.columns = ['item', 'pregunta', 'escala', 'posibles_respuestas']

# Guardar respuestas en Realtime Database


def guardar_respuestas(respuestas):
    id_encuesta = f"ID_{generar_id()}"
    fecha = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    data = {'FECHA': fecha}
    for key, value in respuestas.items():
        data[key] = value

    # Guardar los datos en Realtime Database
    ref.child(id_encuesta).set(data)

# Mostrar encuesta


def mostrar_encuesta():
    st.title("Encuesta de Hábitos de Ahorro")
    st.write("Por favor, responda todas las preguntas obligatorias.")

    # Diccionario para respuestas
    respuestas = {}
    preguntas_faltantes = []  # Para rastrear preguntas sin responder

    # Sección de preguntas
    st.header("Preguntas de la Encuesta")
    for i, row in df_preguntas.iterrows():
        # Esto debe ser el código del sesgo (AV, SQ, CM, DH)
        pregunta_id = row['item']
        pregunta_texto = row['pregunta']
        escala = int(row['escala'])
        opciones = row['posibles_respuestas'].split(',')[:escala]

        # Inicializar el estilo de la pregunta
        estilo_borde = f"2px solid blue"  # Borde azul por defecto
        texto_bold = ""

        # Si la pregunta no ha sido respondida antes, añadir a respuestas
        if pregunta_id not in respuestas:
            respuestas[pregunta_id] = None

        # Validación dinámica: marcar las preguntas sin respuesta
        if st.session_state.get(f"respuesta_{pregunta_id}", None) is None and pregunta_id in preguntas_faltantes:
            estilo_borde = f"3px solid red"  # Borde rojo para preguntas no respondidas
            texto_bold = "font-weight: bold;"  # Texto en negrita

        # Mostrar la pregunta con estilo
        st.markdown(
            f"""<div style="border: {estilo_borde}; padding: 10px; border-radius: 5px; {texto_bold}">
                    {pregunta_texto}
                </div>""",
            unsafe_allow_html=True,
        )

        # Crear opciones de respuesta
        respuesta = st.radio(
            f"Seleccione una opción para la Pregunta {i+1}:",
            opciones,
            index=None,  # No hay selección por defecto
            key=f"respuesta_{pregunta_id}",
        )
        respuestas[pregunta_id] = respuesta

    # Botón para enviar
    if st.button("Enviar", key="enviar_btn"):
        preguntas_faltantes.clear()

        # Validar respuestas
        for i, row in df_preguntas.iterrows():
            pregunta_id = row['item']
            if respuestas[pregunta_id] is None:
                preguntas_faltantes.append((i + 1, pregunta_id))

        # Si hay preguntas faltantes, mostrar advertencias
        if preguntas_faltantes:
            st.error("Por favor, responda las siguientes preguntas:")
            for num_pregunta, _ in preguntas_faltantes:
                st.write(f"❗ Pregunta {num_pregunta}")
        else:
            # Guardar las respuestas en Realtime Database
            guardar_respuestas(respuestas)
            st.success("¡Gracias por completar la encuesta!")
            st.balloons()

            # Bloquear preguntas después del envío
            st.write("La encuesta ha sido enviada exitosamente.")
            # Desactivar el botón de enviar
            st.session_state["enviar_btn"] = True
            st.stop()


# Ejecutar la encuesta
if __name__ == '__main__':
    mostrar_encuesta()
