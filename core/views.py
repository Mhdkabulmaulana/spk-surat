from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from xhtml2pdf import pisa
from django.utils import timezone
import locale
from core.decorators import group_required
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4, landscape
from django.template.loader import get_template
from .models import Surat, Perihal, Status, Kriteria, Sifat, Disposisi, Sumbersurat, Pengirim
from .forms import SuratForm, PerihalForm, StatusForm, KriteriaForm, SifatForm, SumbersuratForm, PengirimForm

def in_groups(user, group_names):
    return user.groups.filter(name__in=group_names).exists()

@login_required
def surat_list(request):
    query = request.GET.get('q')
    status_filter = request.GET.get('status')
    perihal_filter = request.GET.get('perihal')
    sifat_filter = request.GET.get('sifat')
    pengirim_filter = request.GET.get('pengirim')
    sumber_surat_filter = request.GET.get('sumber_surat')
    disposisi_filter = request.GET.get('disposisi')

    surat_qs = Surat.objects.all().order_by('-id')

    if query:
        surat_qs = surat_qs.filter(
            Q(no_surat__icontains=query) |
            Q(perihal__hal__icontains=query) |
            Q(pengirim__nama__icontains=query) |
            Q(sumber_surat__nama__icontains=query)
        )

    if status_filter:
        surat_qs = surat_qs.filter(status__id=status_filter)

    if perihal_filter:
        surat_qs = surat_qs.filter(perihal__id=perihal_filter)

    if sifat_filter:
        surat_qs = surat_qs.filter(sifat__id=sifat_filter)
    
    if pengirim_filter:
        surat_qs = surat_qs.filter(pengirim__id=pengirim_filter)
    
    if sumber_surat_filter:
        surat_qs = surat_qs.filter(sumber_surat__id=sumber_surat_filter)

    if disposisi_filter:
        surat_qs = surat_qs.filter(disposisi__tujuan__icontains=disposisi_filter)

    paginator = Paginator(surat_qs, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    status_list = Status.objects.all()
    perihal_list = Perihal.objects.all()
    sifat_list = Sifat.objects.all()
    pengirim_list = Pengirim.objects.all()
    sumbersurat_list = Sumbersurat.objects.all()
    disposisi_list = Disposisi.objects.values_list('tujuan', flat=True).distinct()

    return render(request, 'surat/surat_list.html', {
        'page_obj': page_obj,
        'status_list': status_list,
        'perihal_list': perihal_list,
        'sifat_list': sifat_list,
        'pengirim_list': pengirim_list,
        'sumbersurat_list': sumbersurat_list,
        'disposisi_list': disposisi_list,
        'query': query,
        'status_filter': status_filter,
        'perihal_filter': perihal_filter,
        'sifat_filter': sifat_filter,
        'pengirim_filter': pengirim_filter,
        'sumber_surat_filter': sumber_surat_filter,
        'disposisi_filter': disposisi_filter,
    })

@login_required
def surat_detail(request, pk):
    surat = get_object_or_404(Surat, pk=pk)
    return render(request, 'surat/surat_detail.html', {'surat': surat})

@login_required
def export_pdf(request):
    surat_qs = Surat.objects.all().order_by('-id')
    template_path = 'surat/export_pdf.html'

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
        "surat_qs": surat_qs,
        "dicetak": dicetak,
    }

    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="rekapan-surat.pdf"'

    pisa_status = pisa.CreatePDF(
        html,
        dest=response,
        default_page_size=landscape(A4)
    )

    if pisa_status.err:
        return HttpResponse('Error saat membuat PDF <pre>' + html + '</pre>')
    return response

@group_required("Superadmin", "Admin")
def surat_tambah(request):
    form = SuratForm(request.POST or None, request.FILES or None)

    perihal_list = Perihal.objects.all()
    status_list = Status.objects.all()
    sifat_list = Sifat.objects.all()
    pengirim_list = Pengirim.objects.all()
    sumbersurat_list = Sumbersurat.objects.all()

    if request.method == "POST":
        if form.is_valid():
            surat = form.save(commit=False)
            if not surat.status:
                surat.status = Status.objects.get(nama="Proses")
            surat.save()
            messages.success(request, "Surat berhasil ditambahkan!") 
            return redirect('surat_list')
        else:
            messages.error(request, "Gagal menambahkan surat, periksa input!")  

    return render(request, 'surat/surat_tambah.html', {
        'form': form,
        'perihal_list': perihal_list,
        'status_list': status_list,
        'sifat_list': sifat_list,
        'pengirim_list': pengirim_list,
        'sumbersurat_list': sumbersurat_list,
    })

@login_required
def surat_edit(request, pk):
    surat = get_object_or_404(Surat, pk=pk)
    form = SuratForm(request.POST or None, request.FILES or None, instance=surat)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Data berhasil diperbarui!")
            return redirect('surat_edit', pk=pk)
        else:
            messages.error(request, "Data gagal diperbarui. Periksa kembali input Anda.")

    return render(request, 'surat/surat_edit.html', {
        'form': form,
        'surat': surat
    })

@login_required
def surat_hapus(request, pk):
    surat = get_object_or_404(Surat, pk=pk)
    surat.delete()
    messages.success(request, "Data berhasil dihapus!")  
    return redirect("surat_list")

# PERIHAL #
@login_required
def perihal_index(request):
    perihals = Perihal.objects.all().order_by('-id')

    paginator = Paginator(perihals, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'perihal/index.html', {'page_obj': page_obj})

def perihal_tambah(request):
    form = PerihalForm(request.POST or None, request.FILES or None)
    perihal_list = Perihal.objects.all()

    if form.is_valid():
        form.save()
        return redirect('perihal_index')

    return render(request, 'perihal/perihal_tambah.html', {
        'form': form,
        'perihal_list': perihal_list
    })

def perihal_edit(request, pk):
    perihal = get_object_or_404(Perihal, pk=pk)
    form = PerihalForm(request.POST or None, request.FILES or None, instance=perihal)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Data berhasil diperbarui!")
            return redirect('perihal_edit', pk=pk)
        else:
            messages.error(request, "Data gagal diperbarui. Periksa kembali input Anda.")

    return render(request, 'perihal/perihal_edit.html', {
        'form': form,
        'perihal': perihal
    })

def perihal_hapus(request, pk):
    perihal = get_object_or_404(Perihal, pk=pk)
    perihal.delete()
    messages.success(request, "Data berhasil dihapus!")  
    return redirect('perihal_index')

# Status #
@login_required
def status_index(request):
    statuses = Status.objects.all().order_by('-id')

    paginator = Paginator(statuses, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'status/index.html', {'page_obj': page_obj})

def status_tambah(request):
    form = StatusForm(request.POST or None, request.FILES or None)
    status_list = Status.objects.all()

    if form.is_valid():
        form.save()
        return redirect('status_index')

    return render(request, 'status/status_tambah.html', {
        'form': form,
        'status_list': status_list
    })

def status_edit(request, pk):
    status = get_object_or_404(Status, pk=pk)
    pesan = None

    if request.method == 'POST':
        nama_baru = request.POST.get('nama')
        if nama_baru:
            status.nama = nama_baru
            status.save()
            pesan = "Data berhasil diperbarui!"  

    return render(request, 'status/status_edit.html', {
        'statuses': status,
        'pesan': pesan
    })

def status_hapus(request, pk):
    status = get_object_or_404(Status, pk=pk)
    status.delete()
    return redirect('status_index')

# Kriteria #
@login_required
def kriteria_index(request):
    data = Kriteria.objects.all().order_by('-id')

    paginator = Paginator(data, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'kriteria/kriteria_index.html', {'page_obj': page_obj})

def kriteria_tambah(request):
    form = KriteriaForm(request.POST or None)
    data = Kriteria.objects.all()

    if form.is_valid():
        obj = form.save()
        print("Data tersimpan:", obj.nama, obj.bobot)
        return redirect('kriteria_index')
    else:
        print("Form error:", form.errors)

    return render(request, 'kriteria/kriteria_tambah.html', {
        'form': form,
        'data': data
    })

def kriteria_edit(request, pk):
    kriteria = get_object_or_404(Kriteria, pk=pk)
    form = KriteriaForm(request.POST or None, request.FILES or None, instance=kriteria)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Data berhasil diperbarui!")
            return redirect('kriteria_edit', pk=pk)
        else:
            messages.error(request, "Data gagal diperbarui. Periksa kembali input Anda.")

    return render(request, 'kriteria/kriteria_edit.html', {
        'form': form,
        'kriteria': kriteria
    })

def kriteria_hapus(request, pk):
    kriteria = get_object_or_404(Kriteria, pk=pk)
    kriteria.delete()
    return redirect('kriteria_index')

# Sifat #
@login_required
def sifat_index(request):
    data = Sifat.objects.all().order_by('-id')

    paginator = Paginator(data, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'sifat/sifat_index.html', {'page_obj': page_obj})

def sifat_tambah(request):
    form = SifatForm(request.POST or None)
    data = Sifat.objects.all()

    if form.is_valid():
        obj = form.save()
        print("Data tersimpan:", obj.nama)
        return redirect('sifat_index')
    else:
        print("Form error:", form.errors)

    return render(request, 'sifat/sifat_tambah.html', {
        'form': form,
        'data': data
    })

def sifat_edit(request, pk):
    sifat = get_object_or_404(Sifat, pk=pk)
    form = SifatForm(request.POST or None, request.FILES or None, instance=sifat)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Data berhasil diperbarui!")
            return redirect('sifat_edit', pk=pk)
        else:
            messages.error(request, "Data gagal diperbarui. Periksa kembali input Anda.")

    return render(request, 'sifat/sifat_edit.html', {
        'form': form,
        'sifat': sifat
    })

def sifat_hapus(request, pk):
    sifat = get_object_or_404(Sifat, pk=pk)
    sifat.delete()
    return redirect('sifat_index')

# Sumber Surat #
@login_required
def sumbersurat_index(request):

    data = Sumbersurat.objects.all().order_by('-id')

    paginator = Paginator(data, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'sumbersurat/sumbersurat_index.html', {
        'page_obj': page_obj})

def sumbersurat_tambah(request):
    form = SumbersuratForm(request.POST or None)
    data = Sumbersurat.objects.all()

    if form.is_valid():
        obj = form.save()
        print("Data tersimpan:", obj.nama)
        return redirect('sumbersurat_index')
    else:
        print("Form error:", form.errors)

    return render(request, 'sumbersurat/sumbersurat_tambah.html', {
        'form': form,
        'data': data
    })

def sumbersurat_edit(request, pk):
    sumbersurat = get_object_or_404(Sumbersurat, pk=pk)
    form = SumbersuratForm(request.POST or None, request.FILES or None, instance=sumbersurat)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Data berhasil diperbarui!")
            return redirect('sumbersurat_edit', pk=pk)
        else:
            messages.error(request, "Data gagal diperbarui. Periksa kembali input Anda.")

    return render(request, 'sumbersurat/sumbersurat_edit.html', {
        'form': form,
        'sumbersurat': sumbersurat
    })

def sumbersurat_hapus(request, pk):
    sumbersurat = get_object_or_404(Sumbersurat, pk=pk)
    sumbersurat.delete()
    return redirect('sumbersurat_index')

# Pengirim 
@login_required
def pengirim_index(request):

    data = Pengirim.objects.all().order_by('-id')

    paginator = Paginator(data, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'pengirim/pengirim_index.html', {
        'page_obj': page_obj})

def pengirim_tambah(request):
    form = PengirimForm(request.POST or None)
    data = Pengirim.objects.all()

    if form.is_valid():
        obj = form.save()
        print("Data tersimpan:", obj.nama)
        return redirect('pengirim_index')
    else:
        print("Form error:", form.errors)

    return render(request, 'pengirim/pengirim_tambah.html', {
        'form': form,
        'data': data
    })

def pengirim_edit(request, pk):
    pengirim = get_object_or_404(Pengirim, pk=pk)
    form = PengirimForm(request.POST or None, request.FILES or None, instance=pengirim)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Data berhasil diperbarui!")
            return redirect('pengirim_edit', pk=pk)
        else:
            messages.error(request, "Data gagal diperbarui. Periksa kembali input Anda.")

    return render(request, 'pengirim/pengirim_edit.html', {
        'form': form,
        'pengirim': pengirim
    })

def pengirim_hapus(request, pk):
    pengirim = get_object_or_404(Pengirim, pk=pk)
    pengirim.delete()
    return redirect('pengirim_index')