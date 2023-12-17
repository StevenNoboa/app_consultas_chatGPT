import pytest
from app_AWS import *
import os

@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()

    yield client

def test_home_route(client):
    response = client.get('http://localhost:3306/')
    assert response.status_code == 200

def test_analizar_documento_route(client):
    script_dir = os.path.dirname(__file__)
    data_dir = os.path.join(script_dir, 'data')
    ruta = os.path.join(data_dir, 'Viggo_Peter_Mortensen_grande.txt')
    with open(ruta,'rb') as archivo:
        response = client.post('http://localhost:3306/analizar_documento', data={'archivo': archivo, 'nombre': 'John', 'pregunta': '¿Qué edad tiene nuestro amigo Viggo?'})
    assert response.status_code == 200

def test_consultas_route(client):
    response = client.get('http://localhost:3306/consultas')
    assert response.status_code == 200

def test_realizar_consulta_route(client):
    response = client.get('http://localhost:3306/realizar_consulta?nombre=Anuel')
    assert response.status_code == 200