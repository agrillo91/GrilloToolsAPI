from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json, hashlib

from .models import LicenseManager as License

@csrf_exempt
def verify_license(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get("email")
        key = data.get("key")        # coincide con tu modelo
        signature = data.get("signature")  # opcional, seguridad extra

        if not email or not key:
            return JsonResponse({"valid": False, "reason": "Datos incompletos"}, status=400)

        # Buscar licencia en la base de datos
        try:
            license_obj = License.objects.get(email=email, key=key)
        except License.DoesNotExist:
            return JsonResponse({"valid": False, "reason": "Licencia no encontrada"})

        # Verificar si la licencia está activa
        if not license_obj.is_active:
            return JsonResponse({"valid": False, "reason": "Licencia inactiva"})

        # Verificación opcional de signature
        if signature:
            data_string = f"{email}|{key}|{settings.LICENSE_SERVER_SECRET}"
            expected_signature = hashlib.sha256(data_string.encode()).hexdigest()
            if signature != expected_signature:
                return JsonResponse({"valid": False, "reason": "Firma inválida"})

        # Todo correcto: licencia activa y firma (si se proporcionó) válida
        return JsonResponse({"valid": True, "user": license_obj.email})

    except Exception as e:
        return JsonResponse({"valid": False, "error": str(e)}, status=500)
