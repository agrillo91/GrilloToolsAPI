from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
import json, hashlib, jwt
from datetime import timedelta, datetime

from .models import LicenseManager as License, DeviceActivation

@csrf_exempt
def verify_license(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get("email")
        key = data.get("key")    
        # machine_id = data.get("machine_id")    
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

        # Verificar si esta máquina ya está registrada    
        # activation = DeviceActivation.objects.filter(license=license_obj, machine_id=machine_id).first()
        activation = DeviceActivation.objects.filter(license=license_obj).first()
        if activation:
            # Ya activada → solo actualizamos la fecha de check-in
            activation.last_checkin = timezone.now()
            activation.save()
        else:
            # Nueva activación → comprobar límite
            if not license_obj.can_activate():
                return JsonResponse({
                    "valid": False,
                    "reason": "Límite de activaciones alcanzado"
                }, status=403)

            DeviceActivation.objects.create(
                license=license_obj,
                # machine_id=machine_id,
                ip_address=request.META.get("REMOTE_ADDR"),
                activated_at=timezone.now(),
                last_checkin=timezone.now(),
            )

        # 🔒 Crear token JWT
        payload = {
            "email": email,
            "key": key,
            "machine_id": machine_id,
            "exp": timezone.now() + timedelta(days=7),
            "iat": timezone.now(),
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
@csrf_exempt
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