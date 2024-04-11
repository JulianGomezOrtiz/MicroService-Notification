from flask import Flask, request, jsonify
import os
import random
from dotenv import load_dotenv
from azure.communication.email import EmailClient
from pymongo import MongoClient
from bson import ObjectId

# Carga las variables de entorno desde el archivo .env
load_dotenv()
app = Flask(__name__)


def get_database():
    connection_string = os.environ.get("CONNECTION_STRING_Mongo")
    client = MongoClient(connection_string)
    return client['security']

#ruta para el reseteo de contraseña
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

    # Enviar correo electrónico de restablecimiento de contraseña
    try:
        connection_string = os.environ.get("CONNECTION_STRING")
        client = EmailClient.from_connection_string(connection_string)

        message = {
            "senderAddress": os.environ.get("SENDER_ADDRESS"),
            "recipients": {
                #(sin conexion a ms-seguridad aún)
                "to": [{"address": email}],
            },
            "content": {
                "subject": "Restablecimiento de contraseña",
                "html": f'<p>Haga clic en el siguiente enlace para restablecer su contraseña: <a href="http://example.com/reset_password?token={reset_token}">Restablecer contraseña</a></p>'
            }
        }

        poller = client.begin_send(message)
        result = poller.result()

    except Exception as ex:
        print(ex)
        return jsonify({'error': 'Error al enviar el correo electrónico'}), 500

    return jsonify({'message': 'Correo electrónico de restablecimiento de contraseña enviado correctamente'}), 200


@app.route('/send_verification_code', methods=['POST'])
def send_verification_code():
    data = request.json
    email = data.get("email")

    # Generar un código de verificación único
    verification_code = ''.join(random.choices('1234567890', k=6))

    # Enviar correo electrónico con el código de verificación
    try:
        connection_string = os.environ.get("CONNECTION_STRING")
        client = EmailClient.from_connection_string(connection_string)

        message = {
            "senderAddress": os.environ.get("SENDER_ADDRESS"),
            "recipients": {
                "to": [{"address": email}],
            },
            "content": {
                "subject": "Código de verificación",
                "html": f'<p>Su código de verificación es: {verification_code}</p>'
            }
        }

        poller = client.begin_send(message)
        result = poller.result()

    except Exception as ex:
        print(ex)
        return jsonify({'error': 'Error al enviar el correo electrónico'}), 500

    return jsonify({'message': 'Correo electrónico con código de verificación enviado correctamente'}), 200


if __name__ == '__main__':
    from waitress import serve
    print("Server running ")
    serve(app, host='0.0.0.0', port=5000)
