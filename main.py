import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from waitress import serve
from azure.communication.email import EmailClient

load_dotenv()
app = Flask(__name__)

connection_string = os.environ.get("CONNECTION_STRING")
client = EmailClient.from_connection_string(connection_string)
sender = os.environ.get("SENDER_ADDRESS")

@app.route('/send_email', methods=['POST'])
def send_email():
    data = request.get_json()

    if 'email' not in data or 'subject' not in data or 'body' not in data:
        return jsonify({'error': 'Missing required fields'})

    try:

        message = {
            "senderAddress": os.environ.get("SENDER_ADDRESS"),
            "recipients":  {
                "to": [{"address": data['email']}],
            },
            "content": {
                "subject": data['subject'],
                "plainText": data['asunto'],
            }
        }

        poller = client.begin_send(message)
        result = poller.result()

    except Exception as ex:
        print(ex)
    return jsonify(data)

@app.route("/send_reset-password_code", methods=["POST"])
def ResetPassword():
    try:
        body = request.get_json()
        user_email = body["email"]
        new_password = body["new_password"]
        template = (
    '<!DOCTYPE html>'
    '<html lang="es">'
    '<head>'
    '    <meta charset="UTF-8">'
    '    <meta name="viewport" content="width=device-width, initial-scale=1.0">'
    '    <title>Código de verificación</title>'
    '    <style>'
    '        body {'
    '            font-family: Arial, sans-serif;'
    '            background-color: #f4f4f4;'
    '            color: #333;'
    '            padding: 20px;'
    '        }'
    '        .container {'
    '            max-width: 600px;'
    '            margin: 50px auto;'
    '            background-color: #fff;'
    '            padding: 20px;'
    '            border-radius: 8px;'
    '            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);'
    '        }'
    '        h3 {'
    '            color: #007bff;'
    '            border-bottom: 2px solid #007bff;'
    '            padding-bottom: 10px;'
    '        }'
    '        p {'
    '            font-size: 18px;'
    '        }'
    '        strong {'
    '            font-weight: bold;'
    '            color: #007bff;'
    '        }'
    '    </style>'
    '</head>'
    '<body>'
    '    <div class="container">'
    '        <h3>Tu código de reseteo de contraseña está listo.</h3>'
    f'        <p>Tu código es: <strong>{new_password}</strong></p>'
    '    </div>'
    '</body>'
    '</html>'
)


        message = {
            "senderAddress": os.environ.get("SENDER_ADDRESS"),
            "recipients": {
                "to": [{"address": user_email}],
            },
            "content": {
                "subject": "Código de autenticación",
                "plainText": "Solicitaste un código de restauración de contraseña.",
                "html": template,
            },
        }

        poller = client.begin_send(message)
        result = poller.result()
        return jsonify({"message": "Email enviado correctamente", "body": result})
                       
    except Exception as e:
        return (
            jsonify(
                {
                    "message": "Error al enviar el correo",
                    "error": e,
                }
            ),
            500,
        )

@app.route("/send_2FAC", methods=["POST"])
def secondFactor():
    try:
        body = request.get_json()
        user_email = body["email"]
        token2FA = body["token2FA"]
        template = (
    '<!DOCTYPE html>'
    '<html lang="es">'
    '<head>'
    '    <meta charset="UTF-8">'
    '    <meta name="viewport" content="width=device-width, initial-scale=1.0">'
    '    <title>Código de verificación</title>'
    '    <style>'
    '        body {'
    '            font-family: Arial, sans-serif;'
    '            background-color: #f4f4f4;'
    '            color: #333;'
    '            padding: 20px;'
    '        }'
    '        .container {'
    '            max-width: 600px;'
    '            margin: 50px auto;'
    '            background-color: #fff;'
    '            padding: 20px;'
    '            border-radius: 8px;'
    '            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);'
    '        }'
    '        h3 {'
    '            color: #007bff;'
    '            border-bottom: 2px solid #007bff;'
    '            padding-bottom: 10px;'
    '        }'
    '        p {'
    '            font-size: 18px;'
    '        }'
    '        strong {'
    '            font-weight: bold;'
    '            color: #007bff;'
    '        }'
    '    </style>'
    '</head>'
    '<body>'
    '    <div class="container">'
    '        <h3>Tu código está listo.</h3>'
    f'        <p>Tu código es: <strong>{token2FA}</strong></p>'
    '    </div>'
    '</body>'
    '</html>'
)


        message = {
            "senderAddress": os.environ.get("SENDER_ADDRESS"),
            "recipients": {
                "to": [{"address": user_email}],
            },
            "content": {
                "subject": "Código de autenticación",
                "plainText": "Solicitaste un código de inicio de sesión.",
                "html": template,
            },
        }

        poller = client.begin_send(message)
        result = poller.result()
        return jsonify({"message": "Email enviado correctamente", "body": result})
                       
    except Exception as e:
        return (
            jsonify(
                {
                    "message": "Error al enviar el correo",
                    "error": e,
                }
            ),
            500,
        )


if __name__ == '__main__':
    print('server running')
    serve(app, host='0.0.0.0', port=5000)
