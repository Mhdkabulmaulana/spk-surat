import calendar
from django.http import HttpResponse
from datetime import date
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.db.models.functions import ExtractWeekDay
from core.models import Surat, Disposisi
from topsis.models import Hasil
from django.utils import timezone

def in_groups(user, group_names):
    return user.groups.filter(name__in=group_names).exists()

def get_week_of_month(dt: date) -> int:
    """Hitung minggu ke berapa dalam bulan, sesuai kalender"""
    first_day = dt.replace(day=1)
    dom = dt.day
    adjusted_dom = dom + first_day.weekday()  # weekday: Sen=0
    return int((adjusted_dom - 1) / 7) + 1

@login_required
def index(request): 
    # Ringkasan
    total_surat = Surat.objects.count()
    sudah_dinilai = Surat.objects.filter(nilai__isnull=False).distinct().count()
    belum_dinilai = total_surat - sudah_dinilai

    sudah_disposisi = Disposisi.objects.filter(tujuan__isnull=False).exclude(tujuan="").count()
    belum_disposisi = total_surat - sudah_disposisi

    surat_selesai = Surat.objects.filter(status__nama="Selesai").count()
    surat_proses = Surat.objects.filter(status__nama="Proses").count()

    surat_terbaru = Surat.objects.order_by("-tanggal")[:1]
    today = timezone.localdate()
    disposisi_today = Disposisi.objects.filter(tanggal__date=today).select_related("surat","surat__status")

    # Hitung jumlah minggu sesuai bulan berjalan
    year, month = today.year, today.month
    days_in_month = calendar.monthrange(year, month)[1]
    jumlah_minggu = (days_in_month + 6) // 7

    urgent_terbaru = Hasil.objects.select_related("surat").order_by("ranking")[:3]
    
    # Mingguan
    data_surat_minggu = [0]*jumlah_minggu
    for surat in Surat.objects.all():
        week_idx = get_week_of_month(surat.tanggal) - 1
        data_surat_minggu[week_idx] += 1

    data_selesai_minggu = [0]*jumlah_minggu
    for surat in Surat.objects.filter(status__nama="Selesai"):
        week_idx = get_week_of_month(surat.tanggal) - 1
        data_selesai_minggu[week_idx] += 1

    data_proses_minggu = [0]*jumlah_minggu
    for surat in Surat.objects.filter(status__nama="Proses"):
        week_idx = get_week_of_month(surat.tanggal) - 1
        data_proses_minggu[week_idx] += 1

    data_sudah_disposisi_minggu = [0]*jumlah_minggu
    for disp in Disposisi.objects.filter(tujuan__isnull=False).exclude(tujuan=""):
        week_idx = get_week_of_month(disp.tanggal) - 1
        data_sudah_disposisi_minggu[week_idx] += 1

    data_belum_disposisi_minggu = [0]*jumlah_minggu
    for disp in Disposisi.objects.filter(Q(tujuan__isnull=True)|Q(tujuan="")):
        week_idx = get_week_of_month(disp.tanggal) - 1
        data_belum_disposisi_minggu[week_idx] += 1

    # Harian (Sen–Min)
    data_surat_hari = [0]*7
    for row in Surat.objects.annotate(hari=ExtractWeekDay("tanggal")).values("hari").annotate(jml=Count("id")):
        data_surat_hari[row["hari"]-1] = row["jml"]

    data_selesai_hari = [0]*7
    for row in Surat.objects.filter(status__nama="Selesai").annotate(hari=ExtractWeekDay("tanggal")).values("hari").annotate(jml=Count("id")):
        data_selesai_hari[row["hari"]-1] = row["jml"]

    data_proses_hari = [0]*7
    for row in Surat.objects.filter(status__nama="Proses").annotate(hari=ExtractWeekDay("tanggal")).values("hari").annotate(jml=Count("id")):
        data_proses_hari[row["hari"]-1] = row["jml"]

    context = {
        "total_surat": total_surat,
        "sudah_dinilai": sudah_dinilai,
        "belum_dinilai": belum_dinilai,
        "sudah_disposisi": sudah_disposisi,
        "belum_disposisi": belum_disposisi,
        "surat_selesai": surat_selesai,
        "surat_proses": surat_proses,
        "surat_terbaru": surat_terbaru,
        "disposisi_today": disposisi_today,
        "urgent_terbaru": urgent_terbaru,
        # Mingguan
        "data_surat_minggu": data_surat_minggu,
        "data_proses_minggu": data_proses_minggu,
        "data_selesai_minggu": data_selesai_minggu,
        "data_sudah_disposisi_minggu": data_sudah_disposisi_minggu,
        "data_belum_disposisi_minggu": data_belum_disposisi_minggu,
        # Harian
        "data_surat_hari": data_surat_hari,
        "data_proses_hari": data_proses_hari,
        "data_selesai_hari": data_selesai_hari,
    }
    return render(request, "beranda.html", context)
