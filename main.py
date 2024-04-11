from azure.communication.email import EmailClient
from flask import Flask, request, jsonify
import os
from bson import DBRef, ObjectId
from dotenv import load_dotenv
# Carga las variables de entorno desde el archivo .env
load_dotenv()
app = Flask(__name__)

def get_database():
   connection_string = os.environ.get("CONNECTION_STRING_Mongo")
   client = MongoClient(connection_string)
 
   return client['security']


email = "juliangomezortiz.05@gmail.com"

@app.route('/send_email', methods=['POST'])
def main():
    try:
        connection_string = os.environ.get("CONNECTION_STRING")
        client = EmailClient.from_connection_string(connection_string)

        message = {
            "senderAddress": os.environ.get("SENDER_ADDRESS"),
            "recipients":  {
                "to": [{"address": email }],
            },
            "content": {
                "subject": "Correo electrónico de prueba",
                "plainText": "Hola mundo por correo electrónico.",
            }
        }

        poller = client.begin_send(message)
        result = poller.result()

    except Exception as ex:
        print(ex)
    return jsonify({'message': 'Email sent successfullsy'}), 200


@app.route('/change_password', methods=['POST'])
def change_password():
    data = request.json

    random_digits = ''.join(random.choices('123456789', k=4))

    databaseConnection = get_database()
    collection_session = databaseConnection['session']
    collection_users = databaseConnection['user'] 

    user_document=collection_users.find_one({"_id": ObjectId(data["_id"])})
    findEmail = collection_session.find_one({"user": DBRef('user', user_document["_id"])})

    if findEmail:
        collection_session.update_one(
        {"user": DBRef('user', user_document["_id"])},
        {"$set": {"code": random_digits}}
    )
    else:

        newData = {
            "user": DBRef('user', user_document["_id"]),
            "active": False,
            "code": random_digits,
            "_class": "com.msurbaNavSecurity.msurbaNavSecurity.Models.Session"
        }

        collection_session.insert_one(newData)


    html_file_path = "plantillas/change_password.html"
    html_content = ''

    # Lee el contenido del archivo HTML
    with open(html_file_path, 'r', encoding= 'utf8') as file:
        html_content = file.read()

    print(f"Email: {data['email']}")

    # Genera los 4 dígitos aleatorios para el "body"
    html_content_number = html_content.replace("$$$", random_digits)

    try:
        connection_string =os.environ.get("CONNECTION_STRING")
        client = EmailClient.from_connection_string(connection_string)
        print(connection_string)
        message = {
            "senderAddress": os.environ.get("SENDER_ADDRESS"),
            "recipients":  {
                "to": [{"address": data['email']}],
            },
            "content": {
                "subject": "Código para cambiar contraseña UrbanNav",
                "html": html_content_number
            }
        }

        poller = client.begin_send(message)
        result = poller.result()

    except Exception as ex:
        print(ex)
    return jsonify({'message': 'Email sent successfully'}), 200


if __name__ == '__main__':
    from waitress import serve
    print("Server running ")
    serve(app, host='0.0.0.0', port=5000)
