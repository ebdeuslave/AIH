from django.db import models
from django.forms import IntegerField
from datetime import date
from django.urls import reverse


class Status(models.Model):
    name = models.CharField(max_length=1000, null=True)

    def __str__(self):
        return f'{self.id}  - { self.name}'
    
    class Meta:
        verbose_name_plural = 'Status'


class Livraison(models.Model):
    cab = models.AutoField(primary_key=True, unique=True, editable=False)
    site = models.CharField(max_length=100, default='Parapharma')
    name = models.CharField(max_length=100,blank=True)
    address = models.CharField(max_length=10000,blank=True)
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=50)
    price = models.IntegerField()
    status = models.ForeignKey(Status, null=True, on_delete=models.SET_NULL, default=1)
    created = models.CharField(max_length=100,default=date.today())
    updated = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return f'{self.cab} - {self.created} - {self.updated} - {self.city} - {self.price} - {self.status}'

    def get_absolute_url(self):
        return reverse("amanaApp:livraison", kwargs={"id":self.pk})

