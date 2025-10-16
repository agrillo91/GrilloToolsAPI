from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json, hashlib, jwt
from datetime import timedelta, datetime

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
            data_string = f"{email}|{key}|{settings.SECRET_KEY}"
            expected_signature = hashlib.sha256(data_string.encode()).hexdigest()
            if signature != expected_signature:
                return JsonResponse({"valid": False, "reason": "Firma inválida"})

        # 🔒 Crear token JWT
        payload = {
            "email": email,
            "key": key,
            "exp": datetime.now(datetime.timezone.utc()) + timedelta(days=7),  # Expira en 7 días
            "iat": datetime.now(datetime.timezone.utc()),
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        if isinstance(token, bytes):
            token = token.decode("utf-8")


        return JsonResponse({
            "valid": True,
            "user": license_obj.email,
            "token": token
        })
    
    except Exception as e:
        return JsonResponse({"valid": False, "error": str(e)}, status=500)

# Validate Token
def validate_token(request):
    """Valida el JWT enviado por el plugin."""
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        import json
        data = json.loads(request.body)
        token = data.get("token")

        if not token:
            return JsonResponse({"valid": False, "reason": "Token no proporcionado"}, status=400)

        try:
            # Decodificar el token
            decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            email = decoded.get("email")
            key = decoded.get("key")

            # Buscar la licencia en la base de datos
            license_obj = License.objects.filter(email=email, key=key).first()

            if not license_obj:
                return JsonResponse({"valid": False, "reason": "Licencia no encontrada"})
            if not license_obj.is_active:
                return JsonResponse({"valid": False, "reason": "Licencia inactiva"})

            # Si todo es correcto
            return JsonResponse({"valid": True, "user": email})

        except jwt.ExpiredSignatureError:
            return JsonResponse({"valid": False, "reason": "Token expirado"})
        except jwt.InvalidTokenError:
            return JsonResponse({"valid": False, "reason": "Token inválido"})

    except Exception as e:
        return JsonResponse({"valid": False, "error": str(e)}, status=500)