from django.shortcuts import render
import os
import openai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from pathlib import Path
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import time
import json

# Initialize OpenAI and Slack API keys
openai.api_key = os.getenv('OPENAI_API_KEY')
slack_token = os.getenv('SLACK_TOKEN')
slack_signing_secret = os.getenv('SLACK_SIGNING_SECRET')

# Initialize Slack client
client = WebClient(token=slack_token)

# Load text from a file for generating responses
file_name = os.path.join(os.path.dirname(__file__), "informacion.txt")

def cargar_texto_desde_archivo(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        return file.read()

texto = cargar_texto_desde_archivo(file_name)

# Bot ID
bot_id = "U07D8QH38FL"

# Register of recent messages sent by the bot
recent_messages = {}

@csrf_exempt
def handle_slack_events(request):
    global recent_messages
    if request.method == "POST":
        payload = json.loads(request.body.decode("utf-8"))

        # Handle URL verification
        if "challenge" in payload:
            return JsonResponse({"challenge": payload["challenge"]})

        event = payload.get("event", {})

        user_id = event.get("user")
        text = event.get("text")
        channel = event.get("channel")
        ts = event.get("ts")

        # Filter messages so the bot doesn't respond to itself
        if event.get("subtype") is None and user_id != bot_id:
            # If the message is not in the recent messages register, respond
            if ts not in recent_messages:
                # Generate response using OpenAI
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": texto},
                            {"role": "user", "content": text}
                        ]
                    )
                    respuesta = response["choices"][0]["message"]["content"].strip()
                    # Send the generated response to Slack
                    try:
                        client.chat_postMessage(channel=channel, text=respuesta)
                    except SlackApiError as e:
                        print(f"Error sending message to Slack: {e.response['error']}")

                    # Add the message to the recent messages register
                    recent_messages[ts] = True
                    # Clean up old messages from the register (optional)
                    current_time = time.time()
                    recent_messages = {k: v for k, v in recent_messages.items() if current_time - float(k) < 300}  # 5 minutes
                except Exception as e:
                    print(f"Error generating response from OpenAI: {e}")

        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "method not allowed"}, status=405)
