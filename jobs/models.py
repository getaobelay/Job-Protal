from django.db import models

# Create your models here.
class Skill(models.Model):
    description = models.TextField(max_length=30)

    
class Job(models.Model):
    
    title = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField(max_length=100)
    url = models.CharField(max_length=100,default='', null=True, blank=True)
    date_posted = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now=True)
    skills = models.ManyToManyField(Skill)



class JobApplication(models.Model):  
    job = models.ForeignKey(Job, on_delete=models.CASCADE)  
    date_created = models.DateTimeField(auto_now=True)
    date_modified = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    cv = models.FileField(upload_to='documents/%Y/%m/%d', blank=True)


