from django import template
from django.db.models import Q
from core.models import Surat, Disposisi

register = template.Library()

@register.filter
def count_pending_disposisi():
    """
    Menghitung jumlah surat yang belum memiliki disposisi
    """
    # Surat yang belum memiliki disposisi
    pending_count = Surat.objects.exclude(disposisi__isnull=False).count()
    return pending_count

@register.filter
def get_pending_disposisi_count():
    """
    Alternative version dengan nama yang lebih deskriptif
    """
    pending_count = Surat.objects.filter(disposisi__isnull=True).count()
    return pending_count

@register.simple_tag
def pending_disposisi_count():
    """
    Simple tag untuk menghitung jumlah surat belum disposisi
    """
    pending_count = Surat.objects.filter(disposisi__isnull=True).count()
    return pending_count

@register.simple_tag
def pending_disposisi_for_kabid():
    """
    Simple tag untuk menghitung surat belum disposisi khusus untuk Kabid
    """
    pending_count = Surat.objects.filter(disposisi__isnull=True).count()
    return pending_count
