from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Inicializar el cliente de Slack con el Bot User OAuth Token desde la configuración
client = WebClient(token=settings.SLACK_TOKEN)
bot_id = settings.BOT_ID

# Inicializar la aplicación de Slack
app = App(token=settings.SLACK_TOKEN, signing_secret=settings.SLACK_SIGNING_SECRET)

@csrf_exempt
def handle_slack_events(request):
    if request.method == "POST":
        try:
            # Procesar el evento de Slack
            # La biblioteca slack-bolt utiliza la función `app.handle` para manejar eventos.
            # Por lo tanto, es necesario pasar la solicitud al objeto app.
            body = request.body.decode('utf-8')
            headers = {key: value for key, value in request.headers.items()}
            response = app.handle(body, headers)
            return response
        except Exception as e:
            print(f"Error processing Slack event: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "method not allowed"}, status=405)

@csrf_exempt
def send_slack_message(request):
    if request.method == "POST":
        try:
            # Enviar mensaje a Slack
            response = client.chat_postMessage(channel="#apibot", text="Hello World")
            return JsonResponse({"status": "success", "message": "Message sent", "response": response.data})
        except SlackApiError as e:
            print(f"Error sending message: {e.response['error']}")
            return JsonResponse({"status": "error", "message": f"Error sending message: {e.response['error']}"}, status=500)
    return JsonResponse({"status": "method not allowed"}, status=405)

# Manejar mensajes de Slack usando el decorador de slack-bolt
@app.event("message")
def handle_message(event, say):
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    if bot_id != user_id:
        say(text=text, channel=channel_id)
