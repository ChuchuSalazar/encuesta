import streamlit as st
import pandas as pd
import random
import datetime
from firebase_admin import credentials, firestore, initialize_app, get_app
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")

# Inicializar Firebase solo si no se ha inicializado previamente
try:
    app = get_app()
except ValueError as e:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS)
    app = initialize_app(cred)

# Conectar a Firestore
db = firestore.client()

# Función para generar un ID único


def generar_id():
    return random.randint(100000, 999999)


# URL del archivo de preguntas
url_preguntas = 'https://raw.githubusercontent.com/ChuchuSalazar/encuesta/main/preguntas.xlsx'

# Función para cargar preguntas


def cargar_preguntas(url):
    try:
        # Leer el archivo Excel y tomar la primera fila como encabezados
        # header=0 indica que la primera fila son los nombres de columnas
        df = pd.read_excel(url, header=0)

        # Verificar que las columnas esperadas existan
        columnas_esperadas = ['item', 'pregunta',
                              'escala', 'posibles_respuestas']
        if not all(col in df.columns for col in columnas_esperadas):
            st.error(
                "El archivo no contiene las columnas esperadas: 'item', 'pregunta', 'escala', 'posibles_respuestas'")
            st.stop()

        # Validar y limpiar la columna 'escala'
        # Convierte 'escala' a numérico; NaN si falla
        df['escala'] = pd.to_numeric(df['escala'], errors='coerce')
        # Elimina filas donde 'escala' no es numérico
        df = df.dropna(subset=['escala'])
        # Asegura que 'escala' sea entero
        df['escala'] = df['escala'].astype(int)

        return df
    except Exception as e:
        st.error(f"Error al cargar las preguntas: {e}")
        st.stop()


# Cargar preguntas desde el archivo
df_preguntas = cargar_preguntas(url_preguntas)

# Función para guardar respuestas en Firebase


def guardar_respuestas(respuestas):
    id_encuesta = f"ID_{generar_id()}"
    fecha = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    data = {'FECHA': fecha}
    for key, value in respuestas.items():
        data[key] = value

    db.collection('respuestas').document(id_encuesta).set(data)

# Función para mostrar la encuesta


def mostrar_encuesta():
    st.title("Encuesta de Hábitos de Ahorro")
    st.write("Por favor, responda todas las preguntas obligatorias.")

    # Diccionario para almacenar respuestas
    respuestas = {}
    preguntas_faltantes = []  # Para rastrear preguntas sin respuesta

    # Sección de preguntas
    st.header("Preguntas de la Encuesta")
    for i, row in df_preguntas.iterrows():
        pregunta_id = row['item']
        pregunta_texto = row['pregunta']
        escala = int(row['escala'])
        opciones = row['posibles_respuestas'].split(',')[:escala]

        # Inicializar estilos
        estilo_borde = f"2px solid blue"  # Azul por defecto
        texto_bold = ""

        # Validar preguntas no respondidas
        if st.session_state.get(f"respuesta_{pregunta_id}", None) is None and pregunta_id in preguntas_faltantes:
            estilo_borde = f"3px solid red"  # Borde rojo para preguntas sin respuesta
            texto_bold = "font-weight: bold;"

        # Mostrar pregunta con estilo
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
            index=None,  # Sin selección predeterminada
            key=f"respuesta_{pregunta_id}",
        )
        respuestas[pregunta_id] = respuesta

    # Botón para enviar respuestas
    if st.button("Enviar"):
        preguntas_faltantes.clear()

        # Validar que todas las preguntas tengan respuesta
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
            # Guardar respuestas en Firebase
            guardar_respuestas(respuestas)
            st.success("¡Gracias por completar la encuesta!")
            st.balloons()
            st.write("La encuesta ha sido enviada exitosamente.")
            st.stop()


# Ejecutar la encuesta
if __name__ == '__main__':
    mostrar_encuesta()
