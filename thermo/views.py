import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings

from .models import Record, Patient
import functools

def reducer(x,y):
  if not isinstance(x, (list,)):
    x = [x]
  for i in x:
    if i['answer']['event'] == y['answer']['event']:
      return x
  x.append(y)
  return x

def build_email_body(messages,record, patient ):
    ret = "On %s Patient %s received the following message(s):\n\n" % (record.uploaded.ctime(), patient.id)
    for i in messages:
        ret = ret + i + "\n\n"
    return ret

def send_emails(record, patient):
    email_to = {}
    all_messages = functools.reduce(reducer, record.data['result_set'])

    if isinstance(all_messages, dict):
        all_messages = [all_messages]

    print (all_messages)
    for item in all_messages:
        # For now we don't send this
        # TODO for production we need to uncomment this
        # for email in item['response']['email_to']:
        #     if email in email_to:
        #         email_to[email].append(item['response']['text'])
        #     else:
        #         email_to[email] = [item['response']['text']]

        cm = record.data['user']['clinic_email']
        if cm in email_to:
            email_to[cm].append(item['response']['text'])
        else:
            print(cm)
            print(email_to)
            print(item)
            print(item['response'])
            print(item['response']['text'])
            email_to[cm] = [item['response']['text']]

    for email in email_to:
        send_mail(
            'MyPath message for patient %s' % patient.pk,
            build_email_body(email_to[email], record, patient),
            'mypath@%s' % settings.MAIL_DOMAIN,
            [email],
            fail_silently=False,
        )

    print( )

@require_POST
@csrf_exempt
def save(request):
    for record in json.loads(request.body):
        if 'user' in record and 'result_set' in record:
            patient, created = Patient.objects.get_or_create(pseudonym=record['user']['pseudonym'], phone_number=record['user']['phone_number'])
            r = Record()
            r.patient = patient
            r.data = record
            r.save()
            send_emails(r, patient)
        else:
            print(record)
            return JsonResponse({'status':'error'}, status=400)

    return JsonResponse({'status':'saved'})


@require_GET
def clinics(request):
    return JsonResponse([
        {'name':'Springfield', 'email':'mypath@rebelproject.org'},
        {'name':'Quahog', 'email':'mch266@uky.edu'},
        {'name':'South Park', 'email':'earonoffspencer@health.ucsd.edu'},
        {'name':'Citadel of Ricks', 'email':'ahubenko@ucsd.edu'}
        ], safe=False)
