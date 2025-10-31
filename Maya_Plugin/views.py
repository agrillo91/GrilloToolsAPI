from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import JsonResponse
import os
import json
from django.conf import settings

def index(request):

    return render(request, "index.html")

def plugin_info(request):
    # Ruta absoluta al JSON que ya tienes
    json_path = os.path.join(settings.BASE_DIR, "Maya_Plugin/plugin_info.json")

    try:
        with open(json_path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"error": "plugin_info.json not found"}

    return JsonResponse(data)

def docs(request):
    return render(request, "docs.html")

def Contact(request):
    return render(request, "Contact.html")
# def plugin_info_json(request):
#     latest = PluginVersion.objects.order_by('-created_at').first()
#     data = {
#         "version": latest.version if latest else "",
#         "download_url": request.build_absolute_uri(latest.file.url) if latest else "",
#     }
#     return JsonResponse(data)
