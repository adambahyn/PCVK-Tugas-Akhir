# Laporan Pipeline Deteksi Lokasi dan Klasifikasi Impacted/Erupted Molar III Bawah (ExAn-MTM)

**Mata kuliah:** PCVK (Praktikum Pemrosesan Citra dan Visi Komputer)
**Tanggal verifikasi hasil:** 25 November 2026
**Artefak utama:** `Pipeline/PCVK_Pipeline_Deteksi_Klasifikasi_Impaksi.ipynb` (sudah dieksekusi, outputs tersimpan di dalam notebook)
**Sumber angka tunggal:** `Pipeline/outputs/metrics.json`

---

## 1. Pendahuluan

### 1.1 Latar belakang
Molar ketiga bawah (mandibular third molar, M3B) yang impacted sering ditemukan pada radiografi panoramik.
Klasifikasi impacted/erupted adalah langkah awal clinicians sebelum menentukan tindakan; pada pipeline
riset, tahap ini dipakai sebagai *gate* menuju klasifikasi yang lebih rinci seperti angulasi
(Winter) dan kedalaman (klasifikasi deepest point by Adams–Lunt). Paper baseline yang dipakai:
Khurshid et al. (2026) membangun framework ganda (deteksi + klasifikasi) untuk impaksi M3B,
sementara Kayadibi et al. (2025) merilis dataset ExAn-MTM sekaligus model deteksi YOLO explainable.

### 1.2 Tujuan
Membangun pipeline reproducible yang:
1. mendeteksi **lokasi** M3B pada citra panoramik (bounding box);
2. mengklasifikasikan tiap kandidat sebagai **impacted (i-MTM)** atau **erupted (e-MTM)**;
3. menyiapkan titik sambung (hook) agar klasifikasi lanjutan 6 angulasi (Winter) bisa disambungkan
   tanpa menulis ulang pipeline.

### 1.3 Ruang lingkup
Eksperimen ini memakai dataset publik ExAn-MTM (973 citra OPG, lisensi CC BY-NC-ND 4.0),
komputasi **CPU-only**, dan **belum** menjalankan klasifikasi angulasi (alasan di Bagian 8).

---

## 2. Tinjauan pustaka

| No | Sumber | Peran dalam pekerjaan ini | Metrik yang dilaporkan paper |
|---|---|---|---|
| 1 | Kayadibi, İ., Köse, U., Güraksın, G. E., & Çetin, B. (2025). E-MTMYOLO: an explainable YOLOv5-based architecture for accurate detection of mandibular third molar using a novel expert-annotated dataset. *The Journal of Supercomputing*, 81(13), 1286. https://doi.org/10.1007/s11227-025-07775-w | Sumber dataset ExAn-MTM; acuan arsitektur deteksi YOLO multi-kelas | Tidak dijelaskan — angka paper tidak diambil pada tahap ini |
| 2 | Khurshid, Z., Alsleem, M. H., Aljubairah, F. A., Alghafli, H. A., Alasafirah, A. O., Alibrahim, B. A., Alshamrani, A. A., & Alsuhaymi, A. N. (2026). Dual framework for classification and detection of third molar impaction in panoramic radiographs. *International Dental Journal*, 76(2), 109430. https://doi.org/10.1016/j.identj.2026.109430 | Acuan pipeline dua tahap (deteksi + klasifikasi) | 5.796 OPG; ResNet50+Fine KNN 97,56% (test); YOLOv11n mAP@0.5:0.95 85,7%; κ = 0,92; split 1.796/2.000/2.000 |
| 3 | Kayadibi, İ., Köse, U., Güraksın, G. E., & Çetin, B. (2025). An AI-assisted explainable mTMCNN architecture for detection of mandibular third molar presence from panoramic radiography. *International Journal of Medical Informatics*, 195, 105724. https://doi.org/10.1016/j.ijmedinf.2024.105724 | Acuan deteksi keberadaan M3B | Tidak dijelaskan — angka paper tidak diambil pada tahap ini |

**Catatan kuartil jurnal (Q1/Q2):** belum diverifikasi terhadap Scimago/Scopus pada penyusunan laporan ini — ditulis **Tidak dijelaskan**.

**Dataset.**
Kayadibi, İ., Köse, U., Güraksın, G. E., & Çetin, B. (2025). *Expert Annotated Mandibular Third Molar
(ExAn-MTM) Dataset* [Data set]. Mendeley Data. https://doi.org/10.17632/t8k59p35p6.1
Lisensi: CC BY-NC-ND 4.0. Konsekuensi: training lokal, **tidak boleh** mengunggah ulang citra ke repo publik.

---

## 3. Data

### 3.1 Ringkasan dataset (hasil audit file lokal, bukan kutipan paper)

| Split | Citra | Objek (bounding box) | e-MTM (erupted) | i-MTM (impacted) | Rata-rata box/citra |
|---|---|---|---|---|---|
| train | 875 | 1604 | 624 | 980 | 1.833 |
| valid | 98 | 180 | 63 | 117 | 1.837 |
| **Total** | **973** | **1784** | **687** | **1097** | 1.834 |

Angka per split dibaca ulang dari `Pipeline/outputs/audit_rekap.csv`; kelas: `0 = e-MTM` (erupted),
`1 = i-MTM` (impacted). Setiap citra memiliki 1–2 bounding box.

### 3.2 Pembagian data
Split **resmi** dataset dipertahankan: train 875 citra / valid 98 citra.
Dataset tidak memuat ID pasien, sehingga **patient-level split tidak dapat dibuat** — dicatat sebagai batasan (Bagian 9).
Data test/valid tidak pernah dipakai untuk tuning (seluruh hiperparameter ditetapkan sebelum evaluasi).

---

## 4. Metode

### 4.1 Arsitektur pipeline
1. **Audit dataset** — hitung citra, objek, distribusi kelas dari file `.txt` lokal; simpan `audit_rekap.csv`.
2. **Deteksi lokasi** — YOLO11n (pretrained COCO) dengan `imgsz=448`, `batch=8`, `epochs=20`, seed 42, device CPU. Kelas: `e-MTM`, `i-MTM`. Bobot terbaik dipakai untuk evaluasi.
3. **Klasifikasi crop** — bounding box di-crop (margin 8%), resize 96×96px:
   - (a) feature ResNet-18 pretrained (ImageNet, frozen) → Logistic Regression & KNN;
   - (b) CNN kecil dilatih dari nol, 3 seed (42/1337/2024) untuk mengukur **variansi antar-run**.
4. **Demo end-to-end** — citra valid → deteksi → crop → klasifikasi → citra berannotasi.
5. **Ringkasan angka** — seluruh metrik digabung di `Pipeline/outputs/metrics.json` (sumber angka tunggal laporan).

### 4.2 Metrik
Deteksi: precision, recall, mAP@0.5, mAP@0.5:0.95 (overall & per kelas), confusion matrix biner.
Klasifikasi: accuracy, precision/recall/F1 per kelas, macro-F1, ROC-AUC, bootstrap 95% CI untuk akurasi.
Variansi: mean ± std lintas 3 seed.

---

## 5. Hasil

### 5.1 Deteksi lokasi (YOLO11n, split valid resmi)

| Metrik | Nilai |
|---|---|
| Precision (overall) | 0.9458 |
| Recall (overall) | 0.9611 |
| mAP@0.5 | 0.9847 |
| mAP@0.5:0.95 | 0.6020 |
| Epoch terbaik (mAP50-95 maksimum) | 20 dari 20 |
| Waktu training | 98.8 menit (CPU) |

**Per kelas:**

| Kelas | Precision | Recall | F1 | mAP@0.5 | mAP@0.5:0.95 |
|---|---|---|---|---|---|
| e-MTM (erupted) | 0.8951 | 0.9479 | 0.9207 | 0.9745 | 0.5666 |
| i-MTM (impacted) | 0.9964 | 0.9744 | 0.9853 | 0.9948 | 0.6373 |

**Confusion matrix deteksi** (baris = ground truth, kolom = prediksi; urutan: e-MTM, i-MTM, background):

```
  61    0    2
   3  114    0
   8    2    0
```

dihitung ulang oleh `scripts/make_cm.py` (conf=0.25, IoU=0.5, pencocokan greedy class-agnostic; matriks bawaan ultralytics 8.4.218 tidak konsisten dengan jumlah GT); jumlah baris = jumlah GT per kelas (61 e-MTM, 117 i-MTM).

### 5.2 Klasifikasi crop

| Model | Accuracy | Macro-F1 | ROC-AUC | CI95 accuracy | Catatan |
|---|---|---|---|---|---|
| ResNet-18 (frozen) + Logistic Regression | 0.9389 | 0.9326 | 0.9742 | [0.9000, 0.9722] | 1 run |
| ResNet-18 (frozen) + KNN (k=5) | 0.8667 | 0.8460 | 0.9267 | [0.8167, 0.9111] | 1 run |
| CNN kecil (96×96) | 0.8648 ± 0.0189 | 0.8543 ± 0.0149 | 0.9634 | seed terbaik 1337 [0.8389, 0.9278] | 3 seed [42, 1337, 2024] |

Rentang akurasi CNN lintas seed: **0.8389 – 0.8833**.

### 5.3 Interpretasi
- Deteksi dan klasifikasi pada dataset ExAn-MTM bekerja pada citra berannotasi yang sama, sehingga
  angka deteksi dan klasifikasi **tidak bisa dibandingkan langsung** dengan paper Khurshid et al. (2026):
  corpus berbeda (973 vs 5.796 OPG), kelas berbeda (2 vs 5+6), komputasi berbeda (CPU vs GPU).
- Distribusi kelas tidak seimbang (687 e-MTM vs 1097 i-MTM); metrik per kelas
  lebih informatif daripada accuracy alone.
- CI95 bootstrap pada split valid (98 citra) lebar sehingga perbedaan < 0,05 antar-model tidak dapat diklaim bermakna.

---

## 6. Pembahasan

**6.1 Posisi terhadap baseline.**
Paper Khurshid et al. (2026) melaporkan YOLOv11n mAP@0.5:0.95 85,7% pada 5.796 OPG dengan pipeline
deteksi + klasifikasi; hasil run ini (mAP@0.5:0.95 0.6020 pada 973 OPG, CPU,
20 epoch) berada pada orde yang lebih rendah. Faktor yang paling mungkin: ukuran corpus,
keterbatasan epoch/CPU, serta perbedaan definisi kelas. **Bukan** disimpulkan sebagaiinferiorkomparatif
karena setup berbeda.

**6.2 Dampak ke tahap angulasi (Winter).**
Pipeline ini dirancang agar tahap 6 angulasi cukup disambungkan:
- `Pipeline/outputs/crops/manifest.csv` sudah memetakan citra → bounding box → crop;
- label angulasi (kelas 0–5 pada `data.yaml` paket Multi-Label) tinggal disatukan ke kolom `cls` manifest;
- kepala klasifikasi tinggal diganti `n_classes=6` dan metrik berpindah dari accuracy ke macro-F1 per kelas;
- citra sumber 6 angulasi **belum** publik di Mendeley Data (`10.17632/xn5bz6fdm6.1` hanya memuat paket
  label + kode), sehingga tahap ini ditunda — bukan dikerjakan dengan data tidak terverifikasi.

**6.3 Replikasi.**
Notebook dijalankan end-to-end di CPU (torch 2.15.0+cpu, ultralytics 8.4.218);
seed ditetapkan (42 untuk deteksi, 42/1337/2024 untuk klasifikasi CNN); bobot terbaik, feature, dan
figure disimpan di `Pipeline/outputs/` sehingga hasil dapat diaudit ulang.

---

## 7. Kesimpulan

1. Pipeline deteksi + klasifikasi impacted/erupted M3B berhasil dijalankan pada dataset ExAn-MTM
   (973 OPG): YOLO11n mencapai mAP@0.5 0.9847 / mAP@0.5:0.95 0.6020
   pada split valid resmi, dan klasifikasi crop mencapai akurasi 0.8648 ± 0.0189
   (CNN, 3 seed).
2. Struktur pipeline (manifest crop + kepala klasifikasi terpisah) siap disambungkan ke klasifikasi
   angulasi 6 kelas begitu citra sumber publik tersedia.
3. Semua angka bersifat eksperimen pada data publik — **bukan** klaim klinis maupun performa alat diagnostik.

---

## 8. Batasan dan pekerjaan lanjutan

| No | Batasan | Dampak | Rencana |
|---|---|---|---|
| 1 | Corpus kecil (973 OPG) | CI bootstrap lebar; generalisasi terbatas | Validasi multi-center bila ada akses |
| 2 | Split per citra, tanpa ID pasien | Risiko kebocoran antar citra pasien yang sama | patient-level split bila ID pasien tersedia; sementara ini **tidak dapat** dibuat |
| 3 | CPU-only, 20 epoch | Model mungkin belum konvergen | Tambah epoch bila compute tersedia |
| 4 | Deteksi dilatih 1 seed | Variansi mAP antar-run belum diukur | ulangi 3 seed bila compute tersedia |
| 5 | Klasifikasi dievaluasi pada crop GT | Domain-shift dari prediksi detektor belum terukur | evaluasi ulang memakai crop dari prediksi |
| 6 | Citra 6 angulasi belum publik | Tahap Winter belum bisa dijalankan | ambil dari sumber publik + buat fetch script + catatan lisensi |
| 7 | Lisensi data NC-ND | Tidak boleh mengunggah ulang citra | training lokal; repo hanya berisi kode, config, dan metrik |

**Pekerjaan lanjutan yang sudah disiapkan kodenya (Bagian 4.1 dan 6.2):** penyambungan dataset angulasi,
perluasan kepala klasifikasi multi-kelas, evaluasi multi-label, dan pembaruan tabel metrik.

---

## 9. Daftar pustaka

Kayadibi, İ., Köse, U., Güraksın, G. E., & Çetin, B. (2025). *Expert Annotated Mandibular Third Molar
(ExAn-MTM) Dataset* [Data set]. Mendeley Data. https://doi.org/10.17632/t8k59p35p6.1

Kayadibi, İ., Köse, U., Güraksın, G. E., & Çetin, B. (2025). An AI-assisted explainable mTMCNN architecture
for detection of mandibular third molar presence from panoramic radiography. *International Journal of
Medical Informatics*, 195, 105724. https://doi.org/10.1016/j.ijmedinf.2024.105724

Kayadibi, İ., Köse, U., Güraksın, G. E., & Çetin, B. (2025). E-MTMYOLO: an explainable YOLOv5-based
architecture for accurate detection of mandibular third molar using a novel expert-annotated dataset.
*The Journal of Supercomputing*, 81(13), 1286. https://doi.org/10.1007/s11227-025-07775-w

Khurshid, Z., Alsleem, M. H., Aljubairah, F. A., Alghafli, H. A., Alasafirah, A. O., Alibrahim, B. A.,
Alshamrani, A. A., & Alsuhaymi, A. N. (2026). Dual framework for classification and detection of third
molar impaction in panoramic radiographs. *International Dental Journal*, 76(2), 109430.
https://doi.org/10.1016/j.identj.2026.109430

---

## 10. Lampiran

### 10.1 Struktur keluaran
```
Pipeline/
  PCVK_Pipeline_Deteksi_Klasifikasi_Impaksi.ipynb   # notebook (sudah dieksekusi)
  data.yaml                                          # konfigurasi YOLO (dihasilkan notebook)
  scripts/build_notebook.py, build_laporan.py         # pembangun artefak
  outputs/
    metrics.json                # sumber angka tunggal
    audit_rekap.csv, audit_dataset.csv, dataset_integrity.json
    metrics_deteksi.json, metrics_klasifikasi_feature.json, metrics_klasifikasi_cnn.json
    figures/                    # figure untuk laporan & PPT
    crops/manifest.csv          # peta citra -> bounding box -> crop (hook angulasi)
    runs/yolo11n_exanmtm/       # bobot YOLO + results.csv
    annotated/                  # keluaran demo end-to-end
```

### 10.2 Perintah replikasi
```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe torch torchvision --index-url https://download.pytorch.org/whl/cpu
uv pip install --python .venv/Scripts/python.exe ultralytics jupyter nbconvert ipykernel matplotlib pandas scikit-learn opencv-python seaborn pillow python-docx
.venv/Scripts/python.exe -m jupyter nbconvert --to notebook --execute --inplace Pipeline/PCVK_Pipeline_Deteksi_Klasifikasi_Impaksi.ipynb
.venv/Scripts/python.exe Pipeline/scripts/build_laporan.py
```

### 10.3 Checklist pelacakan klaim
| Klaim | Status | Sumber |
|---|---|---|
| Jumlah citra, objek, distribusi kelas | Terverifikasi | audit file lokal (`audit_rekap.csv`) |
| Metrik deteksi dan klasifikasi | Terverifikasi | `metrics.json` hasil run |
| Angka paper Khurshid et al. (2026) | Terverifikasi | naskah PMC/full text |
| Kuartil jurnal | Tidak dijelaskan | belum diverifikasi ke Scimago/Scopus |
| Angka paper E-MTMYOLO & mTMCNN | Tidak dijelaskan | tidak diambil pada tahap ini |
| Citra 6 angulasi publik | Tidak dijelaskan (belum tersedia) | Mendeley `xn5bz6fdm6` hanya berisi paket label+kode |
