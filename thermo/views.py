import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Patient

@require_POST
@csrf_exempt
def save(request):
    p = Patient()
    p.data = json.loads(request.body)
    p.save()
    return JsonResponse({'status':'saved'})
