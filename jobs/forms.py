from enum import Enum
from django import forms

from jobs.models import Job

class ApplicationStatus(Enum):   
    Application = "Application"
    Phone = "Phone"
    InPerson = "In Person"
    Skills = "Skills"
    ContractOffer = "Contract Offer"

 

class ApplicationForm(forms.Form):
    status = forms.ChoiceField(choices=[(status, status.value) for status in ApplicationStatus])

  

class CreateJobForm(forms.Form):
    title = forms.CharField(max_length=100)
    company = forms.CharField(max_length=100)
    location = forms.CharField(max_length=100)
    description = forms.TextInput()
    url = forms.CharField(max_length=100)
    date_posted = forms.DateField()
    date_created = forms.DateTimeField()
    
    class Meta:
        model = Job
        fields = "__all__"