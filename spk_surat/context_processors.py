from core.models import Surat, Disposisi
from topsis.models import Hasil
from django.db.models import Q

def disposisi_notification(request):
    pending_disposisi_count = 0
    is_kabid = False
    
    if request.user.is_authenticated:
        is_kabid = request.user.groups.filter(name='Kabid').exists()
        
        surat_dengan_ranking = Hasil.objects.values_list('surat_id', flat=True)
        
        # ✅ CARA 1: Pisahkan filter - PALING SIMPLE & CLEAN
        pending_disposisi_count = Surat.objects.filter(
            id__in=surat_dengan_ranking
        ).filter(
            Q(disposisi__isnull=True) |
            Q(disposisi__tujuan__isnull=True) |
            Q(disposisi__tujuan='')
        ).distinct().count()
    
    return {
        'pending_disposisi_count': pending_disposisi_count,
        'is_user_kabid': is_kabid,
    }