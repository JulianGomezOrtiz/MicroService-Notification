from flask import Flask, request, jsonify
import os
import random
from dotenv import load_dotenv
from azure.communication.email import EmailClient
from pymongo import MongoClient
from bson import ObjectId
import requests

# Carga las variables de entorno desde el archivo .env
load_dotenv()
app = Flask(__name__)


def get_database():
    connection_string = os.environ.get("CONNECTION_STRING_Mongo")
    client = MongoClient(connection_string)
    return client['security']

# Ruta para el restablecimiento de contraseña


@app.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.json
    user_id = data.get("user_id")

    # Obtener el correo electrónico del usuario desde MongoDB
    db = get_database()
    users_collection = db['users']
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    email = user.get("email")

    # Generar un token único para el restablecimiento de contraseña
    reset_token = ''.join(random.choices(
        'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890', k=16))

    # Llamar al endpoint de ms-security para enviar el correo electrónico de restablecimiento de contraseña
    try:
        response = requests.post('http://localhost:8181/api/security/reset_password',
                                 json={"email": email, "reset_token": reset_token})
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error al llamar al microservicio de seguridad: {str(e)}'}), 500

    return jsonify({'message': 'Correo electrónico de restablecimiento de contraseña enviado correctamente'}), 200


@app.route('/send_verification_code', methods=['POST'])
def send_verification_code():
    data = request.json
    email = data.get("email")

    # Generar un código de verificación único
    verification_code = ''.join(random.choices('1234567890', k=6))

    # Llamar al endpoint de ms-security para enviar el correo electrónico con el código de verificación
    try:
        response = requests.post('http://localhost:8181/api/security/send_verification_code',
                                 json={"email": email, "verification_code": verification_code})
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error al llamar al microservicio de seguridad: {str(e)}'}), 500

    return jsonify({'message': 'Correo electrónico con código de verificación enviado correctamente'}), 200


if __name__ == '__main__':
    from waitress import serve
    print("Server running ")
    serve(app, host='0.0.0.0', port=5000)
