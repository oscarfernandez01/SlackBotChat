import openai
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import json
import os
# Configura tu clave de API de OpenAI aquí
openai.api_key = settings.OPENAI_API_KEY

# Inicializar el cliente de Slack con el Bot User OAuth Token desde la configuración
client = WebClient(token=settings.SLACK_TOKEN)

# ID del bot
bot_id = settings.BOT_ID

# Nombre del archivo con el texto para generar respuestas

file_name = os.path.join(os.path.dirname(__file__), "informacion.txt")

# Función para cargar el texto desde el archivo
def cargar_texto_desde_archivo(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        return file.read()

# Cargar el texto desde el archivo
texto = cargar_texto_desde_archivo(file_name)

@csrf_exempt
def handle_slack_events(request):
    if request.method == "POST":
        try:
            payload = json.loads(request.body.decode('utf-8'))
            print(f"Payload recibido: {json.dumps(payload, indent=2)}")

            # Manejar verificación de URL
            if payload.get("type") == "url_verification":
                challenge = payload.get("challenge")
                return HttpResponse(challenge, content_type="text/plain")

            event = payload.get("event", {})
            user_id = event.get("user")
            text = event.get("text")
            channel = event.get("channel")

            print(f"Evento recibido: user_id={user_id}, text={text}, channel={channel}")

            # Verificar que el evento provenga del canal específico y no sea un mensaje de bot
            if channel == settings.SLACK_CHANNEL_ID and event.get("type") == "message" and event.get("subtype") is None and user_id != bot_id:
                try:
                    # Generar respuesta utilizando OpenAI
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": texto},
                            {"role": "user", "content": text}
                        ]
                    )
                    respuesta = response["choices"][0]["message"]["content"].strip()

                    # Enviar respuesta al canal de Slack
                    slack_response = client.chat_postMessage(channel=channel, text=respuesta)
                    print(f"Mensaje enviado a {channel}: {respuesta}")
                    return JsonResponse({"status": "ok", "message": "Message sent", "response": respuesta})
                except SlackApiError as e:
                    print(f"Error enviando mensaje a Slack: {e.response['error']}")
                    return JsonResponse({"status": "error", "message": f"Error sending message: {e.response['error']}"}, status=500)
                except Exception as e:
                    print(f"Error generando respuesta de OpenAI: {e}")
                    return JsonResponse({"status": "error", "message": f"Error generating OpenAI response: {e}"}, status=500)

            return JsonResponse({"status": "ok", "message": "Event received but not processed"})
        except Exception as e:
            print(f"Error procesando solicitud: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "method not allowed"}, status=405)

@csrf_exempt
def send_slack_message(request):
    if request.method == "POST":
        try:
            # Enviar mensaje a Slack
            response = client.chat_postMessage(channel=settings.SLACK_CHANNEL_ID, text="Hello World")
            return JsonResponse({"status": "success", "message": "Message sent", "response": response.data})
        except SlackApiError as e:
            print(f"Error enviando mensaje a Slack: {e.response['error']}")
            return JsonResponse({"status": "error", "message": f"Error sending message: {e.response['error']}"}, status=500)
    return JsonResponse({"status": "method not allowed"}, status=405)
