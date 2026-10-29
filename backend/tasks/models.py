from django.db import models
from django.conf import settings
class Task(models.Model):
 class Status(models.TextChoices):
  PENDING='pending','Pending'
  IN_PROGRESS='in_progress','In Progress'
  COMPLETED='completed','Completed'
 owner=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='workflow_tasks')
 title=models.CharField(max_length=200)
 description=models.TextField(blank=True)
 status=models.CharField(max_length=20,choices=Status.choices,default=Status.PENDING)
 created_at=models.DateTimeField(auto_now_add=True)
 def __str__(self): return self.title
