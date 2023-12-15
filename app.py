from flask import Flask, request, render_template
from langchain.chains import AnalyzeDocumentChain
from langchain.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain

app = Flask(__name__)

llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key="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")
qa_chain = load_qa_chain(llm, chain_type="map_reduce")
qa_document_chain = AnalyzeDocumentChain(combine_docs_chain=qa_chain)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analizar_documento', methods=['POST'])
def analizar_documento():
    if 'archivo' in request.files:
        archivo = request.files['archivo']
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
                # Procesar la respuesta si es necesario
                return str(response)    
            except Exception as e:
                return f"Error: {str(e)}"

        

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0')
