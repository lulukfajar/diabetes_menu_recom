from django.db import connections
from django.db import models

# Create your models here.

class Makanan(models.Model):   
    id          = models.BigIntegerField(primary_key=True)
    nama        = models.CharField(max_length=255)
    kategori    = models.CharField(max_length=255)
    kalori      = models.FloatField()
    protein     = models.FloatField()
    lemak       = models.FloatField()
    karbohidrat = models.FloatField()
    asam_amino  = models.CharField(max_length=10)
    kolesterol  = models.FloatField()
    asam_folat  = models.CharField(max_length=10)
    benam_bduabelas = models.CharField(max_length=10)
    harga           = models.CharField(max_length=10)
    class Meta:
        db_table = "makanan"
