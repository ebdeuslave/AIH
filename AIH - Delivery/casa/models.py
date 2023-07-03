from django.db import models
from django.core.validators import RegexValidator
from django.core.validators import MinLengthValidator
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, date
from io import BytesIO


class Livreur(models.Model):
    nom = models.CharField(null=False, blank=False, max_length=100)
    phone = models.CharField(blank=True, max_length=10, validators=[RegexValidator(r'^0\d*$', 'Invalid Phone Format, Use : 0#########'), MinLengthValidator(10, 'Phone Should be 10 numbers')])


    def __str__(self):
        return self.nom


class Zone(models.Model):
    nom = models.CharField(null=False, blank=False, max_length=1000)
    livreur = models.ForeignKey(Livreur, null=True, blank=False, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.nom} | {self.livreur}'  
        

class Status(models.Model):
    nom = models.CharField(null=False, blank=False, max_length=1000)

    
    class Meta:
        verbose_name_plural = 'Status'
        
        
        
    def __str__(self):
        return f'{self.pk} - {self.nom}'


class Livraison(models.Model):
    site = models.CharField(null=False,max_length=100, blank=False,default='Parapharma')
    zone = models.ForeignKey(Zone, null=True, blank=False, on_delete=models.SET_NULL)
    phone = models.CharField(null=False, blank=False, max_length=20, validators=[MinLengthValidator(10, 'Phone Should be minimum 10 numbers')])
    montant_DH = models.IntegerField(blank=False,null=False)
    n_commande = models.IntegerField(blank=False,default=0)
    commentaire = models.CharField(blank=True, max_length=1000)
    created = models.CharField(max_length=100, null=True,blank=True, default=date.today())
    status = models.ForeignKey(Status, null=True,blank=True, on_delete=models.DO_NOTHING,default=1)
  
    

    def get_absolute_url(self):
        return reverse("livraison:livraison", kwargs={"id":self.pk})

  












