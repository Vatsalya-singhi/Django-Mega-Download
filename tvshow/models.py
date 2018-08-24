from django.db import models
from datetime import datetime
# Create your models here.
class show (models.Model):
    name = models.CharField(max_length=40)
    links = models.CharField(max_length=600)
    ratingdetails = models.CharField(max_length=600)
    created_at = models.DateTimeField(default = datetime.now,blank = True)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'shows' 


class movie (models.Model):
    name = models.CharField(max_length=40)
    links = models.CharField(max_length=600)
    ratingdetails = models.CharField(max_length=600)
    created_at = models.DateTimeField(default = datetime.now,blank = True)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'movies' 
