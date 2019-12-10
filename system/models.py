from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

from django.contrib.auth.models import User
#扩展用户模型
class MyUser(AbstractUser):
    #管理员类型
    root=models.BooleanField(default=False)

class Project(models.Model):

    name=models.CharField(max_length=2048)
    create_time=models.DateField()
    pushilder=models.IntegerField()

class Job(models.Model):
	content=models.TextField()
	projectId=models.IntegerField()
	userId=models.IntegerField()
	status=models.IntegerField(default=0)
	grade=models.IntegerField(null=True)
	meaching_grade=models.IntegerField(null=True)
	create_time=models.DateField(null=True)




