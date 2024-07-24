from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import json

# Inicializar el cliente de Slack con el Bot User OAuth Token desde la configuración
client = WebClient(token=settings.SLACK_TOKEN)

# ID del bot
bot_id = settings.BOT_ID

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

            # Verificar que el evento provenga del canal específico
            if channel == settings.SLACK_CHANNEL_ID:
                # Filtrar mensajes para que el bot no responda a sí mismo
                if event.get("subtype") is None and user_id != bot_id:
                    try:
                        # Enviar "Hola" al canal
                        response = client.chat_postMessage(channel=channel, text="Hola")
                        print(f"Mensaje enviado a {channel}: Hola")
                    except SlackApiError as e:
                        print(f"Error enviando mensaje a Slack: {e.response['error']}")
            
            return JsonResponse({"status": "ok"})
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
