import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings

from .models import Record, Patient
import functools
import anymail

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
        ret += i + "\n\n"

    ret += "\n\n"

    ret += "Patient Details:\n Pseudonym: %s\n Phone Number: %s\n\n" % (patient.pseudonym, patient.phone_number)

    ret += "Patient selected the following:\n"

    for i in record.data['result_set']:
        ret += " %s: %s\n" %(i['answer']['question'], i['answer']['answer'])

    return ret


def send_emails(record, patient):

    if len(record.data['result_set']) == 0:
        return

    email_to = {}
    messages_by_event = functools.reduce(reducer, record.data['result_set'])

    if isinstance(messages_by_event, dict):
        messages_by_event = [messages_by_event]

    #print (messages_by_event)
    for item in messages_by_event:
        # For now we don't send this
        # TODO for production we need to uncomment this
        for email in item['response']['email_to']:
            if email in email_to:
                email_to[email].append(item['response']['text'])
            else:
                email_to[email] = [item['response']['text']]

        cm = record.data['user']['clinic_email']
        if cm in email_to:
            email_to[cm].append(item['response']['text'])
        else:
            email_to[cm] = [item['response']['text']]

    for email in email_to:
        try:
            send_mail(
                'MyPath message for patient %s' % patient.pk,
                build_email_body(email_to[email], record, patient),
                'mypath@%s' % settings.MAIL_DOMAIN,
                [email],
                fail_silently=False,
            )
        except anymail.exceptions.AnymailRequestsAPIError:
            send_mail(
                'MyPath message for patient %s' % patient.pk,
                build_email_body(email_to[email], record, patient),
                'mypath@%s' % settings.MAIL_DOMAIN,
                ['mypath@rebelproject.org'],
                fail_silently=False,
            )


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
        {'name':'CT Surgery', 'email':'lesley.hubbard@uky.edu'},
        ], safe=False)
