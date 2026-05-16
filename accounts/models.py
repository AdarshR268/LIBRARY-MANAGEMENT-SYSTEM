from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.



class CustomUser(AbstractUser):
    status=models.IntegerField(default=0)
    Age=models.IntegerField()
    Phone_number=models.CharField(max_length=255)
    image=models.FileField(upload_to='image/',null=True)
    address=models.CharField(max_length=255)

