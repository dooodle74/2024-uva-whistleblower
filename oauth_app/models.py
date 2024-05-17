from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime
from django.contrib.auth import get_user_model
from django.conf import settings

class UploadedFile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(null=True, blank=True)
    upload_time = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='New')
    public = models.BooleanField(default=False)
    # form
    INCIDENT_CHOICES = [
        ('option1', 'Hazing'),
        ('option2', 'Sexual Misconduct'),
        ('option3', 'Verbal Abuse'),
        ('option4', 'Physical Abuse'),
        ('option5', 'Substance Abuse'),
        ('option6', 'Discrimination'),
        ('other', 'Other'),
    ]
    ORGANIZATION_CHOICES = [
        ('', '---------'),
        ('option1', 'None'),
        ('option2', 'Fraternity'),
        ('option3', 'Sorority'),
        ('option4', 'Academic Club'),
        ('option5', 'Non-Academic Club'),
        ('option6', 'Sports'),
        ('option7', 'Societies'),
        ('other', 'Other'),
    ]
    incident_type = models.CharField(max_length=200, blank=True)

    def get_readable_incident_type(self):
        return [dict(self.INCIDENT_CHOICES).get(option, option) for option in
                self.incident_type.strip("[]").replace("'", "").split(", ") if option]
    
    def get_string_incident_type(self):
        incidents = self.get_readable_incident_type
        

    organizations_involved = models.CharField(max_length=200, choices=ORGANIZATION_CHOICES, blank=True)
    who_was_involved = models.CharField(max_length=200, blank=True)
    injuries = models.CharField(max_length=200, blank=True)
    date_and_time = models.DateTimeField(null=True, blank=True)
    additional_info = models.TextField(blank=True)

    #models.ManyToManyField