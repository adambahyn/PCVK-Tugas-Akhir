# 05 — Rencana Pipeline (berbasis hasil audit)

> Prototipe penelitian & alat bantu edukasi — bukan alat diagnosis medis.

## 0. Data yang dipakai (dikunci dari hasil audit)
| Peran | Dataset | Jumlah | Label | Catatan wajib |
|---|---|---|---|---|
| Train/val Tahap 1 | ExAn-MTM | 875 / 98 citra (split resmi) | bbox + e-MTM/i-MTM | tanpa `data.yaml` → kelas 0=e-MTM, 1=i-MTM (sumber: deskripsi Mendeley) |
| Test eksternal | m-TM **minus** 973 file yang identik dengan ExAn | 344 citra | sisi: ada/tidak impaksi | verifikasi MD5 sebelum pakai; jangan sebaliknya |
| Studi handcrafted | `archive` (CONTACT) | 1034 / 444 (+masker, +xlsx fitur) | masker M3M-IAC; kontak biner | citra 227², bukan 2700×1249 |
| Tahap 2 Winter | **belum tersedia** | — | — | lihat §4 |

## 1. Tahap 1 — Object Detection
- Model: **YOLOv8n / YOLOv11n** (pilihan paling ringan; acuan Khurshid memakai YOLOv11n 8.9M param / 19.7 GFLOPs → cukup untuk laptop kampus). Bandingkan minimal 2 backbone (n dan s) seperti Lei dkk.
- Input: 1024 px (citra asli 1991×1127; 640 terlalu kecil untuk gigi).
- Augmentasi hemat: HSV ringan, ±10° rotasi, skala 0.8–1.2, mosaic **dimatikan di 10 epoch terakhir**.
- Keluaran: bbox M3 (dan opsional M2, karena Winter butuh M2 sebagai acuan).
- Metrik: mAP@0.5, mAP@0.5:0.95, precision, recall **per kelas**, kurva PR, waktu inferensi (ms/citra).

## 2. Tahap 2 — Klasifikasi posisi
Dua jalur, dibandingkan pada split yang sama:

**(a) Jalur deep (acuan Khurshid / Kandagal):** crop ROI dari bbox → resize 224² → ResNet50 pretrained (ImageNet) → ekstraksi embedding 1024-D → classifier klasik (Fine KNN / SVM / Logistic Regression). Ini yang membuat hasil dapat dibandingkan langsung dengan literatur.

**(b) Jalur handcrafted (acuan Ulusoy / Ateş):** dari ROI yang sama hitung fitur:
- **Geometri (Winter):** sudut sumbu panjang M3 terhadap sumbu panjang M2 — perlu M2 terlihat; klasifikasi ambang: mesioangular (−90°…−20°), distoangular (>20°…90°), horizontal (|θ|>70° thd bidang oklusal), vertical (<20°). Ambang **wajib dikutip dari definisi Winter/Pell-Gregory**, bukan dikarang.
- **Tekstur:** GLCM (contrast, correlation, energy, homogeneity, entropy) × 4 sudut (0/45/90/135), jarak d=1, kuantisasi 64 level.
- **Bentuk/rasio:** aspect ratio bbox, luas ROI/citra, rasio luas gigi (bila masker tersedia).
- Seleksi fitur: uji signifikansi (ANOVA/Kruskal) atau PCA; jangan klaim HGWO-PSO kalau tidak diimplementasikan.
- Classifier: SVM RBF, Random Forest, KNN.

## 3. Pencegahan kebocoran (wajib sebelum training)
1. Hash MD5 + dHash seluruh citra; buang duplikat.
2. ExAn-MTM dan m-TM **tidak boleh** ada di split berbeda (973 file identik).
3. Split per-pasien bila metadata pasien diperoleh; bila tidak, split per-citra dan **nyatakan sebagai keterbatasan**.
4. Dataset multi-label **tidak dipakai** (tanpa citra) — sebutkan di laporan sebagai alasan.

## 4. Jalur Winter 4 kelas — keputusan yang harus diambil
- **Opsi A (disarankan):** anotasi manual 300–500 citra ExAn-MTM (dua anotator, hitung Cohen κ) dengan M2 ikut terlihat → label Winter. Ini kontribusi orisinal dan bisa dipertanggungjawabkan.
- **Opsi B:** minta citra 5796 ke penulis Khurshid dkk. (Mendeley, CC BY 4.0) → label 6 kelas sudah ada.
- **Opsi C (hindari):** Winter dihitung dari bbox hasil model sendiri → label sirkular; kalau tetap dipakai, tulis eksplisit sebagai keterbatasan, jangan sebagai ground truth.
- Jika tidak ada yang ditempuh: turunkan klaim menjadi **deteksi + klasifikasi e-MTM/i-MTM**, dan nyatakan itu di rumusan masalah.

## 5. Evaluasi
- Deteksi: mAP@0.5, mAP@0.5:0.95, P/R/F1 per kelas, confusion matrix, ms/citra.
- Klasifikasi: accuracy, **macro-F1** (kelas tidak seimbang: i-MTM 61.5% vs e-MTM 38.5%), F1 per kelas, confusion matrix, 95% CI bootstrap.
- Wajib ada **baseline**: (i) classifier pada embedding deep, (ii) classifier pada fitur handcrafted, (iii) CNN end-to-end. Tanpa baseline, klaim "handcrafted lebih baik" tidak sah.
- Uji signifikansi: paired t-test / McNemar antar model pada fold sama.

## 6. Struktur folder usulan
```
Project/
  Analysis/            01..07 (audit, hasil, script)
  Datasets/            (read-only, jangan dimodifikasi)
  src/
    prepare_split.py   hash, dedup, split, verifikasi kebocoran
    detect/            train_yolo.py, infer.py
    features/          geometric.py, glcm.py
    classify/          train_classifier.py
    evaluate/          metrics.py
  notebooks/           eksplorasi
  reports/             tabel + gambar untuk laporan
```
Hasil ekstraksi/scratch tetap di `%LOCALAPPDATA%\hermes\cache\...`, bukan di repo.

## 7. Lingkup yang harus ditulis di laporan (jujur dari audit)
- Dataset non-komersial (BY-NC-SA / BY-NC-ND): tidak ada redistribusi citra, tidak ada klaim komersial.
- Licensi ND pada ExAn-MTM/CONTACT berarti tidak boleh merilis versi termodifikasi dataset.
- Dataset `archive` hanya 227×227 → tidak cukup untuk fitur kanal halus; batasi klaim.
- Multi-label: label saja, skema 5/6/12 kelas tidak konsisten → jangan dipakai sebagai bukti utama.