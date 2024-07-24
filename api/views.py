from django.http import JsonResponse
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from django.conf import settings
import json

# Inicializar el cliente de Slack con el Bot User OAuth Token
client = WebClient(token="xoxb-7495939536864-7473046446739-z4zYmhBvN1FTZPtZAUNYsJHq")

def send_slack_message(request):
    try:
        # Enviar mensaje a Slack
        response = client.chat_postMessage(channel="#apibot", text="Hello World")
        return JsonResponse({"status": "success", "message": "Message sent", "response": response.data})
    except SlackApiError as e:
        return JsonResponse({"status": "error", "message": f"Error sending message: {e.response['error']}"}, status=500)
