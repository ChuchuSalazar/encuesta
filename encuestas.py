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

# Inicializar Firebase, pero solo si no se ha inicializado previamente
try:
    app = get_app()
except ValueError as e:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS)
    app = initialize_app(cred)

# Conectar a la base de datos Firestore
db = firestore.client()

# Función para generar un ID aleatorio


def generar_id():
    return random.randint(100000, 999999)


# URL del archivo de preguntas en GitHub
url_preguntas = 'https://raw.githubusercontent.com/ChuchuSalazar/encuesta/main/preguntas.xlsx'

# Cargar las preguntas del archivo de Excel desde GitHub, sin usar la primera fila como encabezado
df_preguntas = pd.read_excel(url_preguntas, header=None)

# Asignar los nombres de las columnas: 'item', 'pregunta', 'escala' y 'posibles_respuestas'
df_preguntas.columns = ['item', 'pregunta', 'escala', 'posibles_respuestas']

# Función para guardar las respuestas en Firebase


def guardar_respuestas(respuestas):
    # Asegurando un ID coherente con la estructura
    id_encuesta = f"ID_{generar_id()}"
    fecha = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Crear un diccionario con todas las respuestas y los datos adicionales
    data = {
        'FECHA': fecha,
        'SEXO': respuestas.get('sexo', ''),
        'RANGO_EDA': respuestas.get('rango_edad', ''),
        'RANGO_INGRESO': respuestas.get('rango_ingreso', ''),
        'CIUDAD': respuestas.get('ciudad', ''),
        'NIVEL_PROF': respuestas.get('nivel_educativo', ''),
    }

    # Añadir las respuestas de las preguntas
    for i, row in df_preguntas.iterrows():
        pregunta_id = row['item']
        data[f'AV{pregunta_id}'] = respuestas.get(f'AV{pregunta_id}', '')

    # Guardar en Firebase
    db.collection('respuestas').document(id_encuesta).set(data)

# Función para mostrar la encuesta


def mostrar_encuesta():
    respuestas = {}

    # Mostrar el logo de la universidad
    st.image('logo_ucab.jpg', width=150,
             caption="Universidad Católica Andrés Bello")

    # Mostrar los datos demográficos en forma horizontal
    st.header("Datos Demográficos")

    sexo = st.radio("Sexo:", ['M - Masculino', 'F - Femenino',
                    'O - Otro'], key='sexo', horizontal=True)
    respuestas['sexo'] = sexo.split()[0]

    rango_edad = st.radio("Rango de edad:", [
                          '1 - 18-25', '2 - 26-35', '3 - 36-45', '4 - 46-60', '5 - Más de 60'], key='rango_edad', horizontal=True)
    respuestas['rango_edad'] = rango_edad.split()[0]

    rango_ingreso = st.radio("Rango de ingresos (US$):", [
                             '1 - 0-300', '2 - 301-700', '3 - 701-1100', '4 - 1101-1500', '5 - 1501-3000', '6 - Más de 3000'], key='rango_ingreso', horizontal=True)
    respuestas['rango_ingreso'] = rango_ingreso.split()[0]

    ciudad = st.selectbox("Ciudad:", ['1 - Ciudad A', '2 - Ciudad B',
                          '3 - Ciudad C', '4 - Ciudad D', '5 - Ciudad E'], key='ciudad')
    respuestas['ciudad'] = ciudad.split()[0]

    nivel_educativo = st.radio("Nivel educativo:", [
                               '1 - Primaria', '2 - Secundaria', '3 - Universitario', '4 - Postgrado'], key='nivel_educativo', horizontal=True)
    respuestas['nivel_educativo'] = nivel_educativo.split()[0]

    # Mostrar las preguntas numeradas y enmarcadas
    st.header("Preguntas de la Encuesta")

    # Diccionario para almacenar el borde de las preguntas
    bordes = {}

    for i, row in df_preguntas.iterrows():
        pregunta_id = row['item']
        pregunta_texto = row['pregunta']
        escala = int(row['escala'])  # Número de opciones
        posibles_respuestas = row['posibles_respuestas'].split(
            ',')  # Dividir las respuestas por coma

        # Crear una lista de opciones basadas en la escala
        # Sin la opción de "No responder"
        opciones = posibles_respuestas[:escala]

        # Establecer el borde inicial a azul (delgado)
        borde = '2px solid blue'

        # Mostrar la pregunta con el borde
        st.markdown(f"**Pregunta {i+1}:**")
        st.markdown(f'<div style="border: {
                    borde}; padding: 10px; border-radius: 5px; font-size: 16px; font-family: Arial, sans-serif;">{pregunta_texto}</div>', unsafe_allow_html=True)

        # Mostrar las opciones para cada pregunta
        respuesta = st.radio(f"Respuesta:", opciones, key=f'AV{pregunta_id}')
        respuestas[f'AV{pregunta_id}'] = respuesta

        # Almacenar el borde para validación después de hacer clic en "Enviar"
        bordes[pregunta_id] = borde

    # Botón para enviar las respuestas
    if st.button("Enviar"):
        # Validar que todas las preguntas hayan sido respondidas
        preguntas_faltantes = []  # Lista de preguntas sin respuesta
        for i, row in df_preguntas.iterrows():
            pregunta_id = row['item']
            # Si la respuesta está vacía
            if respuestas.get(f'AV{pregunta_id}', '') == '':
                preguntas_faltantes.append(pregunta_id)
                # Cambiar el borde a rojo grueso
                bordes[pregunta_id] = '3px solid red'

        # Si alguna pregunta falta, mostrar un mensaje de advertencia
        if preguntas_faltantes:
            st.error(f"Por favor, responde las siguientes preguntas: {
                     ', '.join([f'Pregunta {i+1}' for i in preguntas_faltantes])}")
        else:
            guardar_respuestas(respuestas)
            st.balloons()
            st.success(
                "Gracias por completar la encuesta. ¡Tu respuesta ha sido registrada!")

            # Bloquear las preguntas después de enviar
            st.write(
                "¡Gracias por participar! La encuesta ha sido enviada exitosamente.")

        # Mostrar los recuadros actualizados con borde rojo para las preguntas sin respuesta
        for i, row in df_preguntas.iterrows():
            pregunta_id = row['item']
            st.markdown(f"**Pregunta {i+1}:**")
            st.markdown(f'<div style="border: {bordes[pregunta_id]}; padding: 10px; border-radius: 5px; font-size: 16px; font-family: Arial, sans-serif;">{
                        row["pregunta"]}</div>', unsafe_allow_html=True)


# Llamar la función para mostrar la encuesta
if __name__ == '__main__':
    mostrar_encuesta()
