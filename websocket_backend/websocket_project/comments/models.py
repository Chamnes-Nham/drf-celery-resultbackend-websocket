from django.db import models

# Create your models here.
class Comments(models.Model):
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:50]