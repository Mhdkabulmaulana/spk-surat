from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import Surat, Disposisi, Status
from topsis.utils import generate_nilai_otomatis, hitung_topsis
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Surat)
def set_status_proses(sender, instance, created, **kwargs):
    """
    Kalau surat baru ditambahkan, otomatis status = Proses
    """
    if created:
        status_proses, _ = Status.objects.get_or_create(nama="Proses")
        instance.status = status_proses
        instance.save()

@receiver(post_save, sender=Surat)
def auto_run_topsis_on_surat_save(sender, instance, created, **kwargs):
    """
    - Generate nilai otomatis dari utils.py
    - Hitung ranking & preferensi
    - Surat langsung muncul di halaman Tingkat Urgensi
    """
    if created:  # Hanya untuk surat BARU
        try:
            logger.info(f"[TOPSIS AUTO] Memproses surat: {instance.no_surat}")
            
            # ✅ Step 1: Generate nilai otomatis untuk surat baru
            generate_nilai_otomatis()
            logger.info(f"[TOPSIS AUTO] Nilai generated untuk surat: {instance.no_surat}")
            
            # ✅ Step 2: Hitung TOPSIS (ranking & preferensi)
            hitung_topsis(dry_run=False)
            logger.info(f"[TOPSIS AUTO] TOPSIS selesai untuk surat: {instance.no_surat}")
            
        except Exception as e:
            logger.error(f"[TOPSIS AUTO] Error saat proses TOPSIS untuk {instance.no_surat}: {str(e)}")

@receiver(post_save, sender=Disposisi)
def update_status_surat(sender, instance, created, **kwargs):
    """
    Kalau disposisi dibuat/diupdate, otomatis status surat = Selesai
    """
    if kwargs.get("raw", False):
        return
    
    surat = instance.surat
    status_selesai, _ = Status.objects.get_or_create(nama="Selesai")
    surat.status = status_selesai
    surat.save()
