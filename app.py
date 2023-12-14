from flask import Flask, request, render_template
import sqlite3
import pickle
import pandas as pd
from langchain.chains import AnalyzeDocumentChain
from langchain.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain

app = Flask(__name__)

'''llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key="")
qa_chain = load_qa_chain(llm, chain_type="map_reduce")
qa_document_chain = AnalyzeDocumentChain(combine_docs_chain=qa_chain)'''


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0')