from django.db import models
from django.contrib.postgres.fields import JSONField

class Patient(models.Model):
    data = JSONField()
    created = models.DateTimeField(auto_now=True)

    def first_name(self):
        return self.data['user']['fname']

    def last_name(self):
        return self.data['user']['lname']

    def therno_value(self):
        return self.data['thermo']

    def issues(self):
        return self.data['answers']

    def other_issues(self):
        return self.data['other']