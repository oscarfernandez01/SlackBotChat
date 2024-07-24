from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slackeventsapi import SlackEventAdapter
import json

# Inicializar el cliente de Slack con el Bot User OAuth Token desde la configuración
client = WebClient(token=settings.SLACK_TOKEN)

# Inicializar el adaptador de eventos de Slack con el secreto de firma y el prefijo de ruta
slack_events_adapter = SlackEventAdapter(settings.SLACK_SIGNING_SECRET, '/slack/events/')

@csrf_exempt
def send_slack_message(request):
    if request.method == "POST":
        try:
            # Enviar mensaje a Slack
            response = client.chat_postMessage(channel="#apibot", text="Hello World")
            return JsonResponse({"status": "success", "message": "Message sent", "response": response.data})
        except SlackApiError as e:
            return JsonResponse({"status": "error", "message": f"Error sending message: {e.response['error']}"}, status=500)
    return JsonResponse({"status": "method not allowed"}, status=405)

@csrf_exempt
def handle_slack_events(request):
    if request.method == "POST":
        try:
            # Pasar la solicitud al adaptador de eventos de Slack
            response = slack_events_adapter.handle(request)
            return response
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "method not allowed"}, status=405)
