from django.db import models
from core.models import Surat, Kriteria

class Nilai(models.Model):
    surat = models.ForeignKey(Surat, on_delete=models.CASCADE)
    kriteria = models.ForeignKey(Kriteria, on_delete=models.CASCADE)
    nilai = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.surat.no_surat} - {self.kriteria.nama} ({self.nilai})"


class Hasil(models.Model):
    surat = models.ForeignKey(Surat, on_delete=models.CASCADE)
    preferensi = models.FloatField()
    ranking = models.IntegerField()

    def __str__(self):
        return f"{self.surat.no_surat} - Rank {self.ranking}"
