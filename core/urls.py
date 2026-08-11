from django.urls import path
from . import views

urlpatterns = [
    #Surat
    path('surat_list', views.surat_list, name='surat_list'),
    path('surat/detail/<int:pk>/', views.surat_detail, name='surat_detail'),
    path('surat/tambah/', views.surat_tambah, name='surat_tambah'),
    path('surat/edit/<int:pk>/', views.surat_edit, name='surat_edit'),
    path('surat/hapus/<int:pk>/', views.surat_hapus, name='surat_hapus'),

    path('export_pdf/', views.export_pdf, name='export_pdf'),

    #Perihal
    path('perihal/', views.perihal_index, name='perihal_index'),
    path('perihal/tambah/', views.perihal_tambah, name='perihal_tambah'),
    path('perihal/edit/<int:pk>/', views.perihal_edit, name='perihal_edit'),
    path('perihal/hapus/<int:pk>/', views.perihal_hapus, name='perihal_hapus'),

    #Status
    path('status/', views.status_index, name='status_index'),
    path('status/tambah/', views.status_tambah, name='status_tambah'),
    path('status/edit/<int:pk>/', views.status_edit, name='status_edit'),
    path('status/hapus/<int:pk>/', views.status_hapus, name='status_hapus'),

    #Kriteria
    path('kriteria_index/', views.kriteria_index, name='kriteria_index'),
    path('kriteria/tambah/', views.kriteria_tambah, name='kriteria_tambah'),
    path('kriteria/edit/<int:pk>/', views.kriteria_edit, name='kriteria_edit'),
    path('kriteria/hapus/<int:pk>/', views.kriteria_hapus, name='kriteria_hapus'),

    #Sifat
    path('sifat_index/', views.sifat_index, name='sifat_index'),
    path('sifat/tambah/', views.sifat_tambah, name='sifat_tambah'),
    path('sifat/edit/<int:pk>/', views.sifat_edit, name='sifat_edit'),
    path('sifat/hapus/<int:pk>/', views.sifat_hapus, name='sifat_hapus'),

    #Sumber Surat
    path('sumbersurat_index/', views.sumbersurat_index, name='sumbersurat_index'),
    path('sumbersurat/tambah/', views.sumbersurat_tambah, name='sumbersurat_tambah'),
    path('sumbersurat/edit/<int:pk>/', views.sumbersurat_edit, name='sumbersurat_edit'),
    path('sumbersurat/hapus/<int:pk>/', views.sumbersurat_hapus, name='sumbersurat_hapus'),

    #Pengirim
    path('pengirim_index/', views.pengirim_index, name='pengirim_index'),
    path('pengirim/tambah/', views.pengirim_tambah, name='pengirim_tambah'),
    path('pengirim/edit/<int:pk>/', views.pengirim_edit, name='pengirim_edit'),
    path('pengirim/hapus/<int:pk>/', views.pengirim_hapus, name='pengirim_hapus'),
]