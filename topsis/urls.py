from django.urls import path
from . import views

urlpatterns = [
    path('nilai/', views.nilai_index, name='nilai_index'),
    path('nilai/tambah/', views.nilai_tambah, name='nilai_tambah'),
    path('nilai/edit/<int:pk>/', views.nilai_edit, name='nilai_edit'),
    path('nilai/hapus/<int:pk>/', views.nilai_hapus, name='nilai_hapus'),
    path('proses/', views.proses_topsis_view, name='proses_topsis'),
    path('hasil/', views.hasil, name='hasil'),
    path('grafik/', views.grafik, name='grafik'),

    path('disposisi/beri/', views.disposisi_beri, name='disposisi_beri'),
    path('disposisi/', views.disposisi_index, name='disposisi_index'),
    path('surat/<int:surat_id>/disposisi/', views.disposisi_manage, name='disposisi_manage'),
    path('exportdisposisi_pdf/', views.exportdisposisi_pdf, name='exportdisposisi_pdf'),
    path('disposisi/<int:pk>/pdf/', views.export_disposisi_pdf, name='export_disposisi_pdf'),
]
