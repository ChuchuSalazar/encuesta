import streamlit as st
import pandas as pd

# Cargar el archivo Excel
df = pd.read_excel("preguntas.xlsx")

# Función para mostrar la encuesta


def mostrar_encuesta():
    # Si no se ha definido el número de la pregunta en session_state, establecerlo en 0
    if "respuestas" not in st.session_state:
        st.session_state.respuestas = {}

    # Establecer una tipografía estándar para el formulario
    st.markdown("""
        <style>
        body {
            font-family: 'Arial', sans-serif;
        }
        .pregunta {
            border: 2px solid #ddd;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        }
        .escala {
            display: flex;
            justify-content: space-between;
        }
        .escala-nombre {
            font-weight: bold;
            margin-bottom: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Muestra las preguntas de manera continua
    for idx, row in df.iterrows():
        # Enmarcar la pregunta con un borde y mantener la tipografía
        with st.container():
            st.markdown(f'<div class="pregunta"><strong>Pregunta {
                        idx + 1}:</strong> {row["pregunta"]}</div>', unsafe_allow_html=True)

            # Mostrar las opciones de la escala desde la columna "posibles respuestas"
            escala_nombre = row['posibles respuestas']
            escala_opciones = [opcion.strip()
                               for opcion in escala_nombre.split(',')]

            # Mostrar las opciones correspondientes (sin el texto adicional de la escala)
            if len(escala_opciones) > 2:  # Escala Likert
                seleccion = st.radio(
                    f"Seleccione una opción", escala_opciones, key=f"likert_{idx}")
                if seleccion:
                    st.session_state.respuestas[row['pregunta']] = seleccion

            elif len(escala_opciones) == 2:  # Escala binaria (Sí/No)
                seleccion = st.radio(
                    f"Seleccione una opción", escala_opciones, key=f"binario_{idx}")
                if seleccion:
                    st.session_state.respuestas[row['pregunta']] = seleccion

    # Deshabilitar el botón Enviar hasta que todas las preguntas sean respondidas
    all_responded = len(st.session_state.respuestas) == len(df)

    # Mostrar el botón "Enviar" solo si todas las preguntas han sido respondidas
    enviar_disabled = not all_responded

    enviar_button = st.button("Enviar", disabled=enviar_disabled)

    if enviar_button and all_responded:
        st.session_state.encuesta_completada = True
        st.session_state.iniciado = False  # Previene la re-apertura del formulario

# Mostrar el formulario inicial (sexo, ciudad, etc.)


def formulario_inicial():
    st.title("Formulario Inicial")

    # Checkbox para seleccionar una sola opción de sexo
    sexo = st.radio("Sexo", ["Masculino", "Femenino", "Otro"], key="sexo")

    # Checkbox para seleccionar una sola opción de rango de edad
    rango_edad = st.selectbox(
        "Rango de Edad", ["18-25", "26-35", "36-45", "46-60", "60+"], key="rango_edad")

    # Rango de ingresos numérico, con un solo checkbox seleccionado
    rango_ingreso = st.selectbox("Rango de Ingreso", [
                                 "0-1000", "1001-3000", "3001-5000", "5001-7000", "7001+"], key="rango_ingreso")

    # Usamos selectbox para un solo nivel educativo
    nivel_educativo = st.selectbox("Nivel Educativo", [
                                   "Primaria", "Secundaria", "Universitario", "Postgrado"], key="nivel_educativo")

    if st.button("Iniciar Encuesta"):
        st.session_state.iniciado = True


# Comprobar si el formulario ha sido completado
if "iniciado" not in st.session_state or not st.session_state.iniciado:
    formulario_inicial()
elif "encuesta_completada" not in st.session_state or not st.session_state.encuesta_completada:
    mostrar_encuesta()
else:
    # Aquí ya se ha completado la encuesta y se muestra el agradecimiento
    st.markdown("<h1 style='text-align:center;'>Gracias Econ. Jesus Salazar / UCAB</h1>",
                unsafe_allow_html=True)
    st.balloons()  # Efecto visual para celebrar el envío de la encuesta
    st.empty()  # Esto vacía la página para hacerla en blanco
