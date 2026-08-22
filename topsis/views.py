# topsis/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from .models import Nilai, Hasil
from core.models import Disposisi, Surat
from .forms import NilaiForm, DisposisiForm
from .utils import generate_nilai_otomatis, hitung_topsis
import logging
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.utils import timezone
from core.decorators import group_required
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4, landscape
from django.template.loader import get_template
from django.templatetags.static import static

logger = logging.getLogger(__name__)

def is_superadmin(user):
    return user.groups.filter(name="Superadmin").exists()
def is_admin(user):
    return user.groups.filter(name="Admin").exists()
def is_kabid(user):
    return user.groups.filter(name="Kabid").exists()

@login_required
def nilai_index(request):
    data = Nilai.objects.select_related('surat','kriteria').order_by('surat__no_surat')
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'topsis/nilai_index.html', {'page_obj': page_obj})

@login_required
def nilai_tambah(request):
    if request.method == 'POST':
        form = NilaiForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Nilai berhasil ditambahkan.")
            return redirect('nilai_index')
    else:
        form = NilaiForm()
    return render(request, 'topsis/nilai_form.html', {'form': form})

@login_required
def nilai_edit(request, pk):
    nilai = get_object_or_404(Nilai, pk=pk)
    if request.method == 'POST':
        form = NilaiForm(request.POST, instance=nilai)
        if form.is_valid():
            form.save()
            messages.success(request, "Nilai berhasil diperbarui.")
            return redirect('nilai_index')
    else:
        form = NilaiForm(instance=nilai)
    return render(request, 'topsis/nilai_form.html', {'form': form})

@login_required
def nilai_hapus(request, pk):
    nilai = get_object_or_404(Nilai, pk=pk)
    nilai.delete()
    messages.success(request, "Nilai berhasil dihapus.")
    return redirect('nilai_index')

@login_required
def hasil(request):
    # ambil data hasil ranking
    data = Hasil.objects.select_related('surat').order_by('ranking')

    # siapkan data preferensi untuk chart
    preferensi_data = list(data.values('surat__no_surat', 'preferensi'))

    # pagination untuk tabel
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'topsis/hasil.html', {
        'page_obj': page_obj,
        'preferensi_data': preferensi_data,  # kirim ke template
    })

@login_required
def grafik(request):

    data_ranking = Hasil.objects.select_related('surat').order_by('ranking')
    ranking_data = []
    ranking_labels = []
    ranking_values = []
        
    for h in data_ranking:
        ranking_data.append({
            'no_surat': h.surat.no_surat,
            'ranking': h.ranking,
            'preferensi': float(h.preferensi)
        })
    ranking_labels.append(f"Rank {h.ranking}")
    ranking_values.append(float(h.preferensi))
        
    preferensi_labels = [h.surat.no_surat for h in data_ranking]
    preferensi_data = [float(h.preferensi) for h in data_ranking]
        
    return render(request, 'topsis/grafik.html', {
        'ranking_labels': ranking_labels,  
        'ranking_values': ranking_values,  
        'ranking_info': ranking_data,  
            
        'preferensi_labels': preferensi_labels,
        'preferensi_data': preferensi_data,
    })

@login_required
def proses_topsis_view(request):
    """
    Trigger proses TOPSIS.
    Tambahkan ?dry_run=1 untuk menjalankan tanpa mengubah disposisi.
    """
    dry_run = request.GET.get('dry_run') in ['1', 'true', 'True']
    generate_nilai_otomatis()
    hitung_topsis(dry_run=dry_run)
    if dry_run:
        messages.info(request, "TOPSIS selesai (dry run). Disposisi tidak diubah.")
    else:
        messages.success(request, "TOPSIS selesai. Disposisi telah diproses sesuai aturan.")
    return redirect('hasil')

def disposisi_index(request):
    query = request.GET.get('q') or ""
    tujuan_filter = request.GET.get('tujuan')
    tanggal_filter = request.GET.get('tanggal')

    data = Disposisi.objects.select_related('surat').order_by('-tanggal')

    if query:
        data = data.filter(surat__no_surat__icontains=query)

    if tujuan_filter and tujuan_filter != "":
        data = data.filter(tujuan__icontains=tujuan_filter)

    if tanggal_filter and tanggal_filter != "":
        data = data.filter(tanggal__date=tanggal_filter)  # filter by date (YYYY-MM-DD)

    paginator = Paginator(data, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    tujuan_list = Disposisi.objects.values_list('tujuan', flat=True).distinct()
    tanggal_list = Disposisi.objects.dates('tanggal', 'day').distinct()

    return render(request, 'disposisi/disposisi_index.html', {
        'page_obj': page_obj,
        'query': query,
        'tujuan_filter': tujuan_filter,
        'tanggal_filter': tanggal_filter,
        'tujuan_list': tujuan_list,
        'tanggal_list': tanggal_list,
    })

@login_required
def exportdisposisi_pdf(request):
    try:
        dispo = Disposisi.objects.all().order_by('-id')

        now = timezone.localtime(timezone.now())

        hari = {
            "Monday": "Senin",
            "Tuesday": "Selasa",
            "Wednesday": "Rabu",
            "Thursday": "Kamis",
            "Friday": "Jumat",
            "Saturday": "Sabtu",
            "Sunday": "Minggu",
        }

        bulan = {
            "January": "Januari",
            "February": "Februari",
            "March": "Maret",
            "April": "April",
            "May": "Mei",
            "June": "Juni",
            "July": "Juli",
            "August": "Agustus",
            "September": "September",
            "October": "Oktober",
            "November": "November",
            "December": "Desember",
        }

        dicetak = (
            f"{hari[now.strftime('%A')]}, "
            f"{now.strftime('%d')} "
            f"{bulan[now.strftime('%B')]} "
            f"{now.strftime('%Y')} "
            f"pukul {now.strftime('%H:%M')} WIB"
        )

        context = {
            "dispo": dispo,
            "dicetak": dicetak,
        }

        template = get_template('topsis/export_pdf.html')
        html = template.render(context)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="rekap-disposisi-surat.pdf"'
        )

        pisa_status = pisa.CreatePDF(
            html,
            dest=response,
            default_page_size=landscape(A4)
        )

        if pisa_status.err:
            return HttpResponse(
                "ERROR PDF:<br><pre>" + html + "</pre>",
                status=500
            )

        return response

    except Exception as e:
        import traceback
        traceback.print_exc()

        return HttpResponse(
            f"<h3>Error export PDF:</h3><pre>{traceback.format_exc()}</pre>",
            status=500
        )

@group_required("Kabid")
def tambah_disposisi(request, surat_id):
    surat = get_object_or_404(Surat, id=surat_id)
    if request.method == "POST":
        form = DisposisiForm(request.POST)
        if form.is_valid():
            disposisi = form.save(commit=False)
            disposisi.surat = surat
            disposisi.save()
            messages.success(request, "Disposisi berhasil ditambahkan.")
            return redirect("surat_list")
        else:
            messages.error(request, "Disposisi gagal ditambahkan. Periksa input.")
    else:
        form = DisposisiForm()
    return render(request, "disposisi/disposisi_form.html", {"form": form, "surat": surat})

@group_required("Kabid")
def disposisi_manage(request, surat_id):
    surat = get_object_or_404(Surat, id=surat_id)
    try:
        disposisi = Disposisi.objects.get(surat=surat)
    except Disposisi.DoesNotExist:
        disposisi = None

    if request.method == "POST":
        form = DisposisiForm(request.POST, instance=disposisi)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.surat = surat
            obj.save()
            messages.success(request, "Disposisi berhasil disimpan.")
            return redirect("disposisi_index")
        else:
            messages.error(request, "Disposisi gagal disimpan. Periksa kembali data yang diisi.")
    else:
        form = DisposisiForm(instance=disposisi)

    return render(request, "disposisi/disposisi_form.html", {
        "form": form,
        "surat": surat
    })

@group_required("Kabid")
def disposisi_beri(request):
    if not request.user.groups.filter(name="Kabid").exists():
        return redirect("surat_list")

    query = request.GET.get("q", "").strip()

    surat_dengan_ranking = Hasil.objects.values_list(
        "surat_id",
        flat=True
    )

    surat_list = Surat.objects.filter(
        id__in=surat_dengan_ranking
    ).filter(
        Q(disposisi__isnull=True) |
        Q(disposisi__tujuan__isnull=True) |
        Q(disposisi__tujuan="")
    ).distinct().order_by("-id")

    if query:
        surat_list = surat_list.filter(
            Q(no_surat__icontains=query)
        )

    paginator = Paginator(surat_list, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "disposisi/disposisi_beri.html", {
        "page_obj": page_obj,
        "query": query,
    })

def export_disposisi_pdf(request, pk):
    disposisi = get_object_or_404(Disposisi, pk=pk)
    surat = disposisi.surat
    logo_url = request.build_absolute_uri(static('img/pemprovsu.png'))

    template_path = 'disposisi/disposisi_unduh.html'
    context = {
        'logo_url': logo_url,
        'disposisi': disposisi,
        'surat': surat,
    }
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="disposisi-{surat.no_surat}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error saat membuat PDF <pre>' + html + '</pre>')
    return response