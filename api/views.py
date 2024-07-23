from django.shortcuts import render
import os
import openai
import slack
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from pathlib import Path
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import time
import json

# Inicializar las claves de API de OpenAI y Slack
openai.api_key = os.getenv('OPENAI_API_KEY')
slack_token = os.getenv('SLACK_TOKEN')
slack_signing_secret = os.getenv('SLACK_SIGNING_SECRET')

# Inicializar el cliente de Slack
client = WebClient(token=slack_token)

# Nombre del archivo con el texto para generar respuestas
# Nombre del archivo con el texto para generar respuestas
file_name = os.path.join(os.path.dirname(__file__), "informacion.txt")

# Función para cargar el texto desde el archivo
def cargar_texto_desde_archivo(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        return file.read()

# Cargar el texto desde el archivo
texto = cargar_texto_desde_archivo(file_name)

# ID del bot
bot_id = "U07D8QH38FL"

# Registro de mensajes recientes enviados por el bot
recent_messages = {}

@csrf_exempt
def handle_slack_events(request):
    global recent_messages
    if request.method == "POST":
        payload = json.loads(request.body.decode("utf-8"))
        event = payload.get("event", {})

        user_id = event.get("user")
        text = event.get("text")
        channel = event.get("channel")
        ts = event.get("ts")

        # Filtrar mensajes para que el bot no responda a sí mismo
        if event.get("subtype") is None and user_id != bot_id:
            # Si el mensaje no está en el registro de mensajes recientes, responder
            if ts not in recent_messages:
                # Generar respuesta utilizando OpenAI
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": texto},
                            {"role": "user", "content": text}
                        ]
                    )
                    respuesta = response["choices"][0]["message"]["content"].strip()
                    # Enviar la respuesta generada a Slack
                    try:
                        client.chat_postMessage(channel=channel, text=respuesta)
                    except SlackApiError as e:
                        print(f"Error al enviar mensaje a Slack: {e.response['error']}")
                    
                    # Agregar el mensaje al registro de mensajes recientes
                    recent_messages[ts] = True
                    # Limpiar mensajes antiguos del registro (opcional)
                    current_time = time.time()
                    recent_messages = {k: v for k, v in recent_messages.items() if current_time - float(k) < 300}  # 5 minutos
                except Exception as e:
                    print(f"Error al generar respuesta de OpenAI: {e}")

        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "method not allowed"}, status=405)
