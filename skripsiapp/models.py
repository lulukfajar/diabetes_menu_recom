from django.db import connections
from django.db import models

# Create your models here.

class Makanan(models.Model):   
    # id          = models.BigIntegerField(primary_key=True)
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

class JenisDiet(models.Model):   
    id            = models.BigIntegerField(primary_key=True)
    kode_diet     = models.CharField(max_length=3)
    kode_penyakit = models.CharField(max_length=3)
    kode_imt      = models.CharField(max_length=3)
    kelompok_diet = models.CharField(max_length=3)
    nama_diet     = models.CharField(max_length=70)
    deskripsi_diet = models.CharField(max_length=1000)
    class Meta:
        db_table = "jenis_diet"

class TingkatAktivitas(models.Model):   
    id            = models.BigIntegerField(primary_key=True)
    nama_kegiatan = models.CharField(max_length=15)
    kategori      = models.CharField(max_length=100)
    class Meta:
        db_table = "tingkat_aktivitas"
