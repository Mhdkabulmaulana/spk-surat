from django.contrib import admin
from .models import Nilai, Hasil
from .utils import hitung_topsis


@admin.action(description="Proses TOPSIS")
def proses_topsis(modeladmin, request, queryset):
    hitung_topsis()
    modeladmin.message_user(request, "Perhitungan TOPSIS berhasil!")


@admin.register(Nilai)
class NilaiAdmin(admin.ModelAdmin):
    list_display = ('surat', 'kriteria', 'nilai')
    actions = [proses_topsis]


@admin.register(Hasil)
class HasilAdmin(admin.ModelAdmin):
    list_display = ('surat', 'preferensi', 'ranking')
    ordering = ('ranking',)