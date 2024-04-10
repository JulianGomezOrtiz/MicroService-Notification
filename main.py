from azure.communication.email import EmailClient
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Inicialización de la aplicación Flask
app = Flask(__name__)

def send_email(new_numbers):
    try:
        global email

        connection_string = os.environ.get("CONNECTION_STRING")
        client = EmailClient.from_connection_string(connection_string)

        message = {
            "senderAddress": os.environ.get("SENDER_ADDRESS"),
            "recipients": {
                "to": [{"address": email}],
            },
            "content": {
                "subject": "Sudoku Board",
                "html": create_html_table(new_numbers),
            }
        }

        poller = client.begin_send(message)
        result = poller.result()

        return jsonify({'message': 'Email sent successfully'}), 200

    except Exception as ex:
        print(ex)
        return jsonify({'error': str(ex)}), 500

@app.route('/emails', methods=['GET'])
def get_emails():
    # Aquí deberías implementar la lógica para obtener los correos electrónicos
    # Por ahora, simplemente devuelvo un mensaje de éxito para mantener el código funcionando
    return jsonify({'message': 'List of emails'}), 200

if __name__ == '__main__':
    from waitress import serve
    print("Server running ")
    serve(app, host='0.0.0.0', port=5000)
