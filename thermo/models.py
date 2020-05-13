from datetime import datetime, timezone

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.safestring import mark_safe

def return_builder(colour):
    return mark_safe('<i class="circle '+ colour +' icon"></i>')

def group_value(data, g1, g2):
    value_sum = 0
    for i in data:
        if i['answer']['heading'] == g1 and i['answer']['subheading'] == g2 :
            value_sum += i['answer']['value']

    return value_sum

def get_value_question(data, question):
    for i in data:
        if i['answer']['question'] == question:
            return i['answer']['value']

    return 0

class Patient(models.Model):
    pseudonym = models.TextField()
    phone_number = models.TextField()

    def last_upload(self):
        last_upload = (Record.objects.filter(patient=self).last().uploaded)
        now = datetime.now(timezone.utc)
        days = (now-last_upload).days
        ret_string = "%i days ago" % days
        if days > 7:
            return mark_safe('<i class="red exclamation triangle icon"></i> %s days' % ret_string)
        return ret_string


class Record(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT)
    data = JSONField()
    uploaded = models.DateTimeField(auto_now=True)

    order_by = '-uploaded'

    def pseudonym(self):
        try:
            return self.data['user']['pseudonym']
        except KeyError:
            return ""

    def phone_number(self):
        try:
            return self.data['user']['phone_number']
        except KeyError:
            return ""

    def provider_phone_number(self):
        try:
            return self.data['user']['provider_phone_number']
        except KeyError:
            return ""

    def diagnosis(self):
        try:
            return self.data['user']['diagnosis']
        except KeyError:
            return ""

    def clinic_email(self):
        try:
            return self.data['user']['clinic_email']
        except KeyError:
            return ""

    def patient_link(self):
        return mark_safe("<a href='/thermo/patient/%i/change/'>All Patient Records</a>" % self.patient_id)


    def quality_of_life(self):
        try:
            for i in self.data['result_set']:
                if i['answer']['question'] == 'quality of life':
                    if i['answer']['answer'] <= 3:
                        return return_builder('red')

            return return_builder('purple')
        except KeyError:
            return mark_safe('<i class="exclamation circle icon"></i> Please contact an admin')

    def body(self):
        try:
            if group_value(self.data['result_set'], 'Body', 'Whole Body') > 11:
                return return_builder('red')

            if group_value(self.data['result_set'], 'Body', 'Head, Face, Neck') > 4:
                return return_builder('red')

            if group_value(self.data['result_set'], 'Body', 'Respiration and Heart') > 1:
                return return_builder('red')

            if group_value(self.data['result_set'], 'Body', 'Stomach and Gut') > 5:
                return return_builder('red')

            if group_value(self.data['result_set'], 'Body', 'Other') > 2:
                return return_builder('red')

            return return_builder('purple')

        except KeyError:
            return mark_safe('<i class="exclamation circle icon"></i> Please contact an admin')

    def mind(self):
        try:
            if get_value_question(self.data['result_set'], 'Feeling nervous, anxious or on edge') + \
                 get_value_question(self.data['result_set'], 'Not being able to stop or control worrying') > 3:
                return return_builder('red')

            if get_value_question(self.data['result_set'], 'Feeling down, depressed or hopeless') + \
                 get_value_question(self.data['result_set'], 'Little interest or pleasure in doing things') > 3:
                return return_builder('red')

            if get_value_question(self.data['result_set'], 'Felt that you lack companionship') + \
                 get_value_question(self.data['result_set'], 'Felt left out') + \
                 get_value_question(self.data['result_set'], 'Felt isolated from others')  > 5:
                return return_builder('red')

            if get_value_question(self.data['result_set'], 'Feeling guilty about being a burden on others') > 2 or \
                 get_value_question(self.data['result_set'], 'Feeling uncertain about the future') > 2 or \
                 get_value_question(self.data['result_set'], 'Feeling irritable')  > 2:
                return return_builder('red')

            return return_builder('purple')

        except KeyError:
            return mark_safe('<i class="exclamation circle icon"></i> Please contact an admin')

    def living(self):
        try:
            if group_value(self.data['result_set'], 'Living', 'Household') > 3:
                return return_builder('red')

            if group_value(self.data['result_set'], 'Living', 'Finances') > 4:
                return return_builder('red')

            if group_value(self.data['result_set'], 'Living', 'Relationships') > 2:
                return return_builder('red')

            if group_value(self.data['result_set'], 'Living', 'Medications and drugs') > 2:
                return return_builder('red')

            return return_builder('purple')

        except KeyError:
            return mark_safe('<i class="exclamation circle icon"></i> Please contact an admin')


    def detail_response(self):
        return_string = ""
        for i in self.data['result_set']:
            return_string += """
            <table class="ui collapsing celled table">

                <tbody>
                    <tr><td>Heading</td><td>%s</td></tr>
                    <tr><td>Sub-Heading</td><td>%s</td></tr>
                    <tr><td>Question</td><td>%s</td></tr>
                    <tr><td>Answer</td><td>%s</td></tr>
                    <tr><td>Event fired</td><td>%s</td></tr>
                    <tr><td>Email to</td><td>%s</td></tr>
                </tbody>
            </table>
            """ %(
                i['answer']['heading'],
                i['answer'].get('subheading', ''),
                i['answer']['question'],
                i['answer']['answer'],
                i['answer']['event'],
                i['response']['email_to']
            )

        if return_string is "":
            return_string = "The user hasn't selected anything that triggered an event."
        return mark_safe(return_string)

