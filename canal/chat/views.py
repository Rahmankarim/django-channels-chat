from django.shortcuts import render
from django.views.generic import TemplateView
import json


class ChatView(TemplateView):
    template_name = 'chat/index.html'


def room(request, room_name):
    # Encode the room name as JSON, but pass it as a regular string
    # The template will handle it securely using JavaScript
    return render(request, 'chat/room.html', {
        'room_name': room_name,  # Pass the raw room name
        'room_name_json': json.dumps(room_name)  # Pass JSON-encoded string
    })
