import math
import logging
from collections import defaultdict
from django.db import transaction
from core.models import Surat, Kriteria, Disposisi
from topsis.models import Nilai, Hasil

logger = logging.getLogger(__name__)

def hitung_nilai_otomatis(surat, kriteria):
    if kriteria.nama == "Kepentingan":
        mapping = {
            "Undangan Rapat": 70,
            "Permintaan Data": 80,
            "Permohonan Penerimaan": 75,
            "Penyampaian Laporan": 50,
            "Penugasan Instansi": 90,
        }
        return mapping.get(getattr(surat.perihal, 'hal', None), 50)

    elif kriteria.nama == "Sumber Surat":
        return 100 if getattr(surat, "pengirim", None) else 50

    elif kriteria.nama == "Jenis Surat":
        mapping = {
            "Sangat Segera": 100,
            "Segera": 85,
            "Rahasia": 70,
            "Biasa": 40,
        }
        return mapping.get(getattr(surat.sifat, 'nama', None), 50)

    elif kriteria.nama == "Deadline":
        return 100 if getattr(surat, "deadline_hari", None) and surat.deadline_hari <= 3 else 50

    else:
        return 50

def generate_nilai_otomatis():
    for surat in Surat.objects.all():
        for kriteria in Kriteria.objects.all():
            nilai = hitung_nilai_otomatis(surat, kriteria)
            Nilai.objects.update_or_create(
                surat=surat,
                kriteria=kriteria,
                defaults={'nilai': nilai}
            )

def hitung_topsis(dry_run=False):
    generate_nilai_otomatis()

    surat_list = list(Surat.objects.all())
    kriteria_list = list(Kriteria.objects.all())
    if not surat_list or not kriteria_list:
        logger.info("TOPSIS: tidak ada surat atau kriteria untuk diproses.")
        return

    # 🔹 Matriks keputusan
    X = defaultdict(dict)
    for s in surat_list:
        for k in kriteria_list:
            X[s.id][k.id] = 0
    for n in Nilai.objects.all():
        X[n.surat_id][n.kriteria_id] = n.nilai

    # 🔹 Normalisasi
    pembagi = {}
    for k in kriteria_list:
        jumlah = sum((X[s.id][k.id] ** 2 for s in surat_list))
        pembagi[k.id] = math.sqrt(jumlah) if jumlah != 0 else 1

    R = defaultdict(dict)
    for s in surat_list:
        for k in kriteria_list:
            R[s.id][k.id] = X[s.id][k.id] / pembagi[k.id]

    # 🔹 Normalisasi terbobot
    V = defaultdict(dict)
    for s in surat_list:
        for k in kriteria_list:
            V[s.id][k.id] = R[s.id][k.id] * k.bobot

    # 🔹 Solusi ideal
    A_plus, A_min = {}, {}
    for k in kriteria_list:
        nilai_k = [V[s.id][k.id] for s in surat_list]

        # cek jenis kriteria: benefit atau cost
        if k.nama == "Deadline":  # contoh cost criteria
            # untuk cost: ideal positif = min, ideal negatif = max
            A_plus[k.id] = min(nilai_k)
            A_min[k.id] = max(nilai_k)
        else:  # default benefit criteria
            # untuk benefit: ideal positif = max, ideal negatif = min
            A_plus[k.id] = max(nilai_k)
            A_min[k.id] = min(nilai_k)

    # 🔹 Jarak
    D_plus, D_min = {}, {}
    for s in surat_list:
        D_plus[s.id] = math.sqrt(sum((V[s.id][k.id] - A_plus[k.id]) ** 2 for k in kriteria_list))
        D_min[s.id] = math.sqrt(sum((V[s.id][k.id] - A_min[k.id]) ** 2 for k in kriteria_list))

    # 🔹 Preferensi
    preferensi = {}
    for s in surat_list:
        pembagi_pref = (D_plus[s.id] + D_min[s.id])
        preferensi[s.id] = 0 if pembagi_pref == 0 else D_min[s.id] / pembagi_pref
        print("Surat:", s.no_surat)
        print("D+:", D_plus[s.id], "D-:", D_min[s.id], "Preferensi:", preferensi[s.id])

    # 🔹 Ranking
    urut = sorted(preferensi.items(), key=lambda x: x[1], reverse=True)
    Hasil.objects.all().delete()
    for rank, (sid, pref) in enumerate(urut, start=1):
        Hasil.objects.create(
            surat_id=sid,
            preferensi=round(pref, 5),
            ranking=rank
        )

    # 🔹 Disposisi tidak diisi otomatis
    if dry_run:
        logger.info("TOPSIS: dry_run aktif — tidak mengubah disposisi.")
        for hasil in Hasil.objects.select_related('surat').all():
            logger.info("Rekomendasi: surat=%s ranking=%s",
                        hasil.surat.no_surat, hasil.ranking)
        return

    with transaction.atomic():
        for hasil in Hasil.objects.select_for_update().select_related('surat'):
            disposisi_obj, created = Disposisi.objects.get_or_create(surat=hasil.surat)
            if not disposisi_obj.tujuan:
                # 🔹 Biarkan kosong, jangan isi otomatis
                logger.info("TOPSIS: surat=%s disposisi dibiarkan kosong (ranking %s)",
                            hasil.surat.no_surat, hasil.ranking)
                disposisi_obj.save()
            else:
                # 🔹 Kalau sudah ada disposisi manual, tetap dipertahankan
                logger.info("TOPSIS: surat=%s disposisi lama=%s (ranking %s)",
                            hasil.surat.no_surat, disposisi_obj.tujuan, hasil.ranking)
