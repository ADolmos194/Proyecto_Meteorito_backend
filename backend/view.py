from django.http import JsonResponse
from .supabase_config import register_user

def register_view(request):
    email = request.POST.get("email")
    password = request.POST.get("password")
    result = register_user(email, password)
    return JsonResponse(result)
