from flask import Flask, request, render_template
from langchain.chains import AnalyzeDocumentChain
from langchain.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
import sqlite3
from datetime import datetime
import pymysql
from keys import *

app = Flask(__name__)

#langchain
llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=openai_api_key)
qa_chain = load_qa_chain(llm, chain_type="map_reduce")
qa_document_chain = AnalyzeDocumentChain(combine_docs_chain=qa_chain)

#AWS
username = "admin"
password = AWS_password
host = "gpt-database.cjlljwohiugl.eu-north-1.rds.amazonaws.com" 
port = 3306
database="gpt_database"

def insertar_registro(fecha_hora, nombre, pregunta, respuesta):
    
    conn = pymysql.connect(host = host,
                     user = username,
                     port=port,
                     password = password,
                     database=database
                     )

    cursor = conn.cursor()
    cursor.execute('INSERT INTO gpt_table (Registro, Nombre, Consulta, Respuesta) VALUES (%s, %s, %s, %s)',
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
                
        nombre = request.form.get('nombre')
        if not nombre:
            return "Error: Debe introducir su nombre"
        
        pregunta = request.form.get('pregunta')
        if not pregunta:
            return "Error: La pregunta no se proporcionó"

        # leer el archivo en fragmentos de 4KB
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

                fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                insertar_registro(fecha_hora_actual, nombre, pregunta, str(response))

                return render_template('respuestas.html', pregunta=pregunta, respuesta=str(response))
            except Exception as e:
                return render_template('results.html', pregunta=pregunta, respuesta='', error=str(e))

        

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0')