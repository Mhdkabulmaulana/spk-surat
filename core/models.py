from django.db import models

class Surat(models.Model):
    no_surat = models.CharField(max_length=100, unique=True)
    perihal = models.ForeignKey('Perihal', on_delete=models.CASCADE)
    file = models.FileField(upload_to='surat/', null=True, blank=True)
    tanggal = models.DateField(auto_now_add=True) 
    tanggal_surat = models.DateField(null=False, blank=False)  
    pengirim = models.ForeignKey('Pengirim', on_delete=models.SET_NULL, null=True, blank=True)
    sumber_surat = models.ForeignKey('Sumbersurat', on_delete=models.SET_NULL, null=True, blank=True)
    keterangan = models.TextField(null=True, blank=True)
    status = models.ForeignKey('Status', on_delete=models.SET_NULL, null=True, blank=True)
    sifat = models.ForeignKey('Sifat', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.no_surat

class Kriteria(models.Model):
    nama = models.CharField(max_length=100)
    bobot = models.FloatField()

    def __str__(self):
        return self.nama

class Perihal(models.Model):
    hal = models.CharField(max_length=100)

    def __str__(self):
        return self.hal

class Sumbersurat(models.Model):
    nama = models.CharField(max_length=100)

    def __str__(self):
        return self.nama

class Pengirim(models.Model):
    nama = models.CharField(max_length=100)

    def __str__(self):
        return self.nama
    
class Status(models.Model):
    nama = models.CharField(max_length=100)   # contoh: Proses, Selesai, Ditolak, Arsip

    def __str__(self):
        return self.nama
    
class Sifat(models.Model):
    nama = models.CharField(max_length=100)  

    def __str__(self):
        return self.nama

class Disposisi(models.Model):
    TUJUAN_CHOICES = [
        ("Staf", "Staf"),
        ("Kasubbid 1", "Kasubbid 1"),
        ("Kasubbid 2", "Kasubbid 2"),
        ("Kasubbid 3", "Kasubbid 3 / Jafung"),
        ("Kabid", "Kabid"),
        ("Arsip", "Arsip"),
    ]

    surat = models.OneToOneField(Surat, on_delete=models.CASCADE, related_name="disposisi")
    catatan = models.TextField(default="", blank=True)
    tujuan = models.CharField(max_length=100, choices=TUJUAN_CHOICES, blank=True, null=True)
    tanggal = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Disposisi {self.surat.no_surat} → {self.tujuan}"
