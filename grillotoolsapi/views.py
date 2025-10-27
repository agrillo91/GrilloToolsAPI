import json
from django.http import JsonResponse
from django.conf import settings
import os

def plugin_info(request):
    # Ruta absoluta al JSON que ya tienes
    json_path = os.path.join(settings.BASE_DIR, "plugin_info.json")

    try:
        with open(json_path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"error": "plugin_info.json not found"}

    return JsonResponse(data)

