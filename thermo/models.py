from django.db import models
from django.contrib.postgres.fields import JSONField

class Patient(models.Model):
    data = JSONField()
    created = models.DateTimeField(auto_now=True)

    def first_name(self):
        try:
            return self.data['user']['fname']
        except KeyError:
            return ""

    def last_name(self):
        try:
            return self.data['user']['lname']
        except KeyError:
            return ""

    def therno_value(self):
        try:
            return self.data['thermo']
        except KeyError:
            return ""

    def issues(self):
        try:
            return self.data['answers']
        except KeyError:
            return ""

    def other_issues(self):
        try:
            return self.data['other']
        except KeyError:
            return ""
