from django.db import models
from django.utils import timezone
from rest_framework import serializers


class CustomUserModel(models.Model):
    email = models.EmailField(unique=True, null=False, blank=False)
    password= models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return self.email
    

class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class Task(models.Model):
    StatusTypes=(("OPEN","open"),("WORKING","working"),("DONE","done"),("OVERDUE","overdue"),)
    author = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=100,null=False, blank=False)
    description = models.TextField(max_length=1000,null=False, blank=False)
    due_date= models.DateField(null=True, blank=True)
    tags = models.ManyToManyField(Tag)
    status = models.CharField(max_length=30, choices=StatusTypes, default= "OPEN",null=False, blank=False)
    def __str__(self):
       return self.title

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'