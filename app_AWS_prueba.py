from flask import Flask, request, render_template, redirect, url_for
from langchain.chains import AnalyzeDocumentChain
from langchain.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
import sqlite3
from datetime import datetime
import pymysql

app = Flask(__name__)

# Configuración de la base de datos en AWS RDS
username = "tu_usuario"
password = "tu_contraseña"
host = "tu_endpoint.rds.amazonaws.com"
port = 3306
database = "tu_base_de_datos"

# Configuración de langchain
llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key="tu_clave")
qa_chain = load_qa_chain(llm, chain_type="map_reduce")
qa_document_chain = AnalyzeDocumentChain(combine_docs_chain=qa_chain)

def insertar_registro(fecha_hora, nombre, pregunta, respuesta):
    conn = pymysql.connect(host=host, user=username, port=port, password=password, database=database)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO GPT_database (Registro, Nombre, Consulta, Respuesta) VALUES (?, ?, ?, ?)',
                   (fecha_hora, nombre, pregunta, respuesta))
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analizar_documento', methods=['POST'])
def analizar_documento():
    if 'archivo' in request.files:
        archivo = request.files['archivo']
        if not archivo:
            return "Error: Ningún archivo introducido"
        
    if 'nombre' in request.form:           
        nombre = request.form.get('nombre')  # Obtener el nombre del formulario
        if not nombre:
            return "Error: Debe introducir su nombre"
        
    if 'pregunta' in request.form:   
        pregunta = request.form.get('pregunta')
        if not pregunta:
            return "Error: La pregunta no se proporcionó"

        # Leer el archivo en fragmentos de 4KB
        fragment_size = 4096
        while True:
            parte = archivo.read(fragment_size)
            if not parte:
                break

            try:
                response = qa_document_chain.run(
                    input_document=parte.decode('latin-1'),
                    question=pregunta,
                )

                # Obtener la fecha y hora actual
                fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Insertar en la base de datos
                insertar_registro(fecha_hora_actual, nombre, pregunta, str(response))

                # Procesar la respuesta si es necesario
                return str(response)    
            except Exception as e:
                return f"Error: {str(e)}"

@app.route('/consultar_registros', methods=['GET'])
def consultar_registros():
    try:
        conn = pymysql.connect(host=host, user=username, port=port, password=password, database=database)
        cursor = conn.cursor()

        # Ejecuta una consulta SELECT para obtener todos los registros
        cursor.execute('SELECT * FROM GPT_database')
        registros = cursor.fetchall()

        # Cierra la conexión
        cursor.close()
        conn.close()

        # Renderiza la plantilla con los resultados de la consulta
        return render_template('consultar_registros.html', registros=registros)
    except Exception as e:
        # Maneja cualquier error que pueda ocurrir durante la consulta
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0')
