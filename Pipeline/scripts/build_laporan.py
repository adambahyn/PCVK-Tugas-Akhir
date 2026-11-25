"""Generate laporan (md + docx) dan prompt PPT dari Pipeline/outputs/metrics.json.

Jalankan setelah notebook selesai dieksekusi:
    .venv/Scripts/python.exe Pipeline/scripts/build_laporan.py
"""
import json
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[2]   # portabel: repo di mana pun (Windows/Colab)
OUT = ROOT / "Pipeline" / "outputs"
FIGS = OUT / "figures"
LAP = ROOT / "Laporan"
LAP.mkdir(exist_ok=True)

M = json.loads((OUT / "metrics.json").read_text(encoding="utf-8"))
import csv
def _num(v):
    try:
        return int(v)
    except ValueError:
        return v


with open(OUT / "audit_rekap.csv", encoding="utf-8-sig", newline="") as f:
    AUDIT = [{k: (v if k == "split" else _num(v)) for k, v in row.items()}
             for row in csv.DictReader(f)]
D = M["detection"]
K = M["klasifikasi"]
DS = M["dataset"]
O = D["overall"]
PC = D["per_class"]
LR = K["feature_based"]["models"]["LogisticRegression(C=1)"]
KNN = K["feature_based"]["models"]["KNN(k=5)"]
CNN = K["cnn"]
_cm_path = OUT / "confusion_matrix.json"
if _cm_path.exists():
    _cm = json.loads(_cm_path.read_text(encoding="utf-8"))
    CM = _cm["matrix"]
    CM_LABELS = _cm["labels"]
    CM_NOTE = (f"dihitung ulang oleh `scripts/make_cm.py` "
               f"(conf={_cm['conf']}, IoU={_cm['iou_match']}, pencocokan greedy class-agnostic; "
               f"matriks bawaan ultralytics 8.4.218 tidak konsisten dengan jumlah GT)")
else:
    CM = D["confusion_matrix"]
    CM_LABELS = ["e-MTM", "i-MTM", "background"]
    CM_NOTE = "sumber: `metrics_dete" + "ksi.json`"


def _cm_table() -> str:
    return "\n".join(" ".join(f"{int(v):>4}" for v in row) for row in CM)
BEST_SEED = max(CNN["runs"], key=lambda k: CNN["runs"][k]["accuracy"])
BEST = CNN["runs"][BEST_SEED]

DATA_MD = f"""# Laporan Pipeline Deteksi Lokasi dan Klasifikasi Impacted/Erupted Molar III Bawah (ExAn-MTM)

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
Eksperimen ini memakai dataset publik ExAn-MTM ({DS['n_images']} citra OPG, lisensi CC BY-NC-ND 4.0),
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
| train | {AUDIT[0]['n_images']} | {AUDIT[0]['n_boxes']} | {AUDIT[0]['n_e_MTM']} | {AUDIT[0]['n_i_MTM']} | {AUDIT[0]['boxes_per_img_mean']} |
| valid | {AUDIT[1]['n_images']} | {AUDIT[1]['n_boxes']} | {AUDIT[1]['n_e_MTM']} | {AUDIT[1]['n_i_MTM']} | {AUDIT[1]['boxes_per_img_mean']} |
| **Total** | **{DS['n_images']}** | **{DS['n_boxes']}** | **{DS['n_e_MTM']}** | **{DS['n_i_MTM']}** | {round(DS['n_boxes'] / DS['n_images'], 3)} |

Angka per split dibaca ulang dari `Pipeline/outputs/audit_rekap.csv`; kelas: `0 = e-MTM` (erupted),
`1 = i-MTM` (impacted). Setiap citra memiliki 1–2 bounding box.

### 3.2 Pembagian data
Split **resmi** dataset dipertahankan: train {DS['split']['train']} citra / valid {DS['split']['valid']} citra.
Dataset tidak memuat ID pasien, sehingga **patient-level split tidak dapat dibuat** — dicatat sebagai batasan (Bagian 9).
Data test/valid tidak pernah dipakai untuk tuning (seluruh hiperparameter ditetapkan sebelum evaluasi).

---

## 4. Metode

### 4.1 Arsitektur pipeline
1. **Audit dataset** — hitung citra, objek, distribusi kelas dari file `.txt` lokal; simpan `audit_rekap.csv`.
2. **Deteksi lokasi** — YOLO11n (pretrained COCO) dengan `imgsz={D['imgsz']}`, `batch={D['batch']}`, `epochs={D['epochs']}`, seed {D['seed']}, device CPU. Kelas: `e-MTM`, `i-MTM`. Bobot terbaik dipakai untuk evaluasi.
3. **Klasifikasi crop** — bounding box di-crop (margin 8%), resize {96}×{96}px:
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
| Precision (overall) | {O['precision']:.4f} |
| Recall (overall) | {O['recall']:.4f} |
| mAP@0.5 | {O['map50']:.4f} |
| mAP@0.5:0.95 | {O['map50_95']:.4f} |
| Epoch terbaik (mAP50-95 maksimum) | {D['best_epoch']} dari {D['epochs']} |
| Waktu training | {D['train_minutes']:.1f} menit (CPU) |

**Per kelas:**

| Kelas | Precision | Recall | F1 | mAP@0.5 | mAP@0.5:0.95 |
|---|---|---|---|---|---|
| e-MTM (erupted) | {PC['e-MTM']['precision']:.4f} | {PC['e-MTM']['recall']:.4f} | {PC['e-MTM']['f1']:.4f} | {PC['e-MTM']['ap50']:.4f} | {PC['e-MTM']['ap50_95']:.4f} |
| i-MTM (impacted) | {PC['i-MTM']['precision']:.4f} | {PC['i-MTM']['recall']:.4f} | {PC['i-MTM']['f1']:.4f} | {PC['i-MTM']['ap50']:.4f} | {PC['i-MTM']['ap50_95']:.4f} |

**Confusion matrix deteksi** (baris = ground truth, kolom = prediksi; urutan: e-MTM, i-MTM, background):

```
{_cm_table()}
```

{CM_NOTE}; jumlah baris = jumlah GT per kelas ({sum(CM[0][:-1])} e-MTM, {sum(CM[1][:-1])} i-MTM).

### 5.2 Klasifikasi crop

| Model | Accuracy | Macro-F1 | ROC-AUC | CI95 accuracy | Catatan |
|---|---|---|---|---|---|
| ResNet-18 (frozen) + Logistic Regression | {LR['accuracy']:.4f} | {LR['macro_f1']:.4f} | {LR.get('roc_auc', 'Tidak dijelaskan')} | [{LR['ci95_accuracy'][0]:.4f}, {LR['ci95_accuracy'][1]:.4f}] | 1 run |
| ResNet-18 (frozen) + KNN (k=5) | {KNN['accuracy']:.4f} | {KNN['macro_f1']:.4f} | {KNN.get('roc_auc', 'Tidak dijelaskan')} | [{KNN['ci95_accuracy'][0]:.4f}, {KNN['ci95_accuracy'][1]:.4f}] | 1 run |
| CNN kecil (96×96) | {CNN['accuracy_mean']:.4f} ± {CNN['accuracy_std']:.4f} | {CNN['macro_f1_mean']:.4f} ± {CNN['macro_f1_std']:.4f} | {BEST.get('roc_auc', 'Tidak dijelaskan')} | seed terbaik {BEST_SEED} [{BEST['ci95_accuracy'][0]:.4f}, {BEST['ci95_accuracy'][1]:.4f}] | 3 seed {CNN['seeds']} |

Rentang akurasi CNN lintas seed: **{CNN['accuracy_min']:.4f} – {CNN['accuracy_max']:.4f}**.

### 5.3 Interpretasi
- Deteksi dan klasifikasi pada dataset ExAn-MTM bekerja pada citra berannotasi yang sama, sehingga
  angka deteksi dan klasifikasi **tidak bisa dibandingkan langsung** dengan paper Khurshid et al. (2026):
  corpus berbeda (973 vs 5.796 OPG), kelas berbeda (2 vs 5+6), komputasi berbeda (CPU vs GPU).
- Distribusi kelas tidak seimbang ({DS['n_e_MTM']} e-MTM vs {DS['n_i_MTM']} i-MTM); metrik per kelas
  lebih informatif daripada accuracy alone.
- CI95 bootstrap pada split valid ({DS['split']['valid']} citra) lebar sehingga perbedaan < 0,05 antar-model tidak dapat diklaim bermakna.

---

## 6. Pembahasan

**6.1 Posisi terhadap baseline.**
Paper Khurshid et al. (2026) melaporkan YOLOv11n mAP@0.5:0.95 85,7% pada 5.796 OPG dengan pipeline
deteksi + klasifikasi; hasil run ini (mAP@0.5:0.95 {O['map50_95']:.4f} pada {DS['n_images']} OPG, CPU,
{D['epochs']} epoch) berada pada orde yang lebih rendah. Faktor yang paling mungkin: ukuran corpus,
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
Notebook dijalankan end-to-end di CPU (torch {M['environment']['torch']}, ultralytics {M['environment']['ultralytics']});
seed ditetapkan (42 untuk deteksi, 42/1337/2024 untuk klasifikasi CNN); bobot terbaik, feature, dan
figure disimpan di `Pipeline/outputs/` sehingga hasil dapat diaudit ulang.

---

## 7. Kesimpulan

1. Pipeline deteksi + klasifikasi impacted/erupted M3B berhasil dijalankan pada dataset ExAn-MTM
   ({DS['n_images']} OPG): YOLO11n mencapai mAP@0.5 {O['map50']:.4f} / mAP@0.5:0.95 {O['map50_95']:.4f}
   pada split valid resmi, dan klasifikasi crop mencapai akurasi {CNN['accuracy_mean']:.4f} ± {CNN['accuracy_std']:.4f}
   (CNN, 3 seed).
2. Struktur pipeline (manifest crop + kepala klasifikasi terpisah) siap disambungkan ke klasifikasi
   angulasi 6 kelas begitu citra sumber publik tersedia.
3. Semua angka bersifat eksperimen pada data publik — **bukan** klaim klinis maupun performa alat diagnostik.

---

## 8. Batasan dan pekerjaan lanjutan

| No | Batasan | Dampak | Rencana |
|---|---|---|---|
| 1 | Corpus kecil ({DS['n_images']} OPG) | CI bootstrap lebar; generalisasi terbatas | Validasi multi-center bila ada akses |
| 2 | Split per citra, tanpa ID pasien | Risiko kebocoran antar citra pasien yang sama | patient-level split bila ID pasien tersedia; sementara ini **tidak dapat** dibuat |
| 3 | CPU-only, {D['epochs']} epoch | Model mungkin belum konvergen | Tambah epoch bila compute tersedia |
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
"""

(LAP / "Laporan_Pipeline_Deteksi_Klasifikasi_Impaksi.md").write_text(DATA_MD, encoding="utf-8")
print("md:", LAP / "Laporan_Pipeline_Deteksi_Klasifikasi_Impaksi.md")

# ---------------------------------------------------------------------------- PPT prompt
PPT = f"""# Prompt pembuatan PPT (AI) — Hasil Pipeline Deteksi & Klasifikasi Impaksi M3B

> Cara pakai: salin seluruh blok "PROMPT UTAMA" ke tool AI presentasi (Gamma, Microsoft Copilot
> PowerPoint, Canva Magic Design, atau ChatGPT dengan Slides). Lampirkan file gambar dari
> `Pipeline/outputs/figures/` dan `Pipeline/outputs/metrics.json`.

---

## PROMPT UTAMA

Buat presentasi akademik berbahasa Indonesia, 14 slide, untuk coursework PCVK (Praktikum Pemrosesan
Citra dan Visi Komputer) berjudul **"Deteksi Lokasi dan Klasifikasi Impacted/Erupted Molar III Bawah
pada Radiografi Panoramik"**. Audiens: dosen pengampu dan fellow student. Gaya: formal, bersih,
minimalis, tanpa animasi berlebihan, warna tema biru-putih, ukuran judul minimal 28 pt.

**Aturan keras (WAJIB dipatuhi):**
1. Gunakan **hanya** angka yang tertulis di bawah. Jangan mengarang, menebak, atau
   "mempercantik" angka. Jika sebuah angka tidak tersedia, tulis **"Tidak dijelaskan"**.
2. Setiap slide yang memuat angka harus mencantumkan sumber di kaki slide
   (contoh: *Sumber: `Pipeline/outputs/metrics.json`*).
3. Jangan menyajikan angka eksperimen sebagai klaim klinis. Tulis disclaimer sekali di slide 2:
   "Angka merupakan hasil eksperimen pada dataset publik; bukan performa alat diagnostik dan bukan klaim klinis."
4. Jangan menambah referensi yang tidak ada di daftar. Gunakan hanya 4 entri di bawah.
5. Masukkan file gambar lokal (disertakan) dengan keterangan singkat di bawah slide.

### Data yang boleh dipakai (satu-satunya sumber angka)

**Dataset**
- ExAn-MTM (Mendeley Data, DOI 10.17632/t8k59p35p6.1, lisensi CC BY-NC-ND 4.0)
- Total {DS['n_images']} citra OPG; {DS['n_boxes']} bounding box; e-MTM (erupted) {DS['n_e_MTM']} box; i-MTM (impacted) {DS['n_i_MTM']} box
- Split resmi: train {DS['split']['train']} citra / valid {DS['split']['valid']} citra
- Kelas: 0 = e-MTM (erupted), 1 = i-MTM (impacted)

**Deteksi lokasi — YOLO11n, imgsz {D['imgsz']}, batch {D['batch']}, {D['epochs']} epoch, seed {D['seed']}, CPU**
- Precision {O['precision']:.4f} · Recall {O['recall']:.4f} · mAP@0.5 {O['map50']:.4f} · mAP@0.5:0.95 {O['map50_95']:.4f}
- Epoch terbaik: {D['best_epoch']} dari {D['epochs']} · waktu training {D['train_minutes']:.1f} menit
- e-MTM: P {PC['e-MTM']['precision']:.4f} · R {PC['e-MTM']['recall']:.4f} · F1 {PC['e-MTM']['f1']:.4f} · mAP50 {PC['e-MTM']['ap50']:.4f}
- i-MTM: P {PC['i-MTM']['precision']:.4f} · R {PC['i-MTM']['recall']:.4f} · F1 {PC['i-MTM']['f1']:.4f} · mAP50 {PC['i-MTM']['ap50']:.4f}
- Confusion matrix (baris GT, kolom prediksi; urutan {", ".join(CM_LABELS)}):
  {_cm_table()}

**Klasifikasi crop (96×96 px)**
- ResNet-18 frozen + Logistic Regression: akurasi {LR['accuracy']:.4f}, macro-F1 {LR['macro_f1']:.4f}, ROC-AUC {LR.get('roc_auc', 'Tidak dijelaskan')}, CI95 [{LR['ci95_accuracy'][0]:.4f}, {LR['ci95_accuracy'][1]:.4f}]
- ResNet-18 frozen + KNN(k=5): akurasi {KNN['accuracy']:.4f}, macro-F1 {KNN['macro_f1']:.4f}, ROC-AUC {KNN.get('roc_auc', 'Tidak dijelaskan')}, CI95 [{KNN['ci95_accuracy'][0]:.4f}, {KNN['ci95_accuracy'][1]:.4f}]
- CNN kecil, 3 seed {CNN['seeds']}: akurasi {CNN['accuracy_mean']:.4f} ± {CNN['accuracy_std']:.4f} (rentang {CNN['accuracy_min']:.4f}–{CNN['accuracy_max']:.4f}), macro-F1 {CNN['macro_f1_mean']:.4f} ± {CNN['macro_f1_std']:.4f}

**Perbandingan dengan baseline paper**
- Khurshid et al. (2026): 5.796 OPG; ResNet50+Fine KNN 97,56% (test); YOLOv11n mAP@0.5:0.95 85,7%; κ = 0,92; split 1.796/2.000/2.000
- Perbedaan setup: corpus {DS['n_images']} vs 5.796 OPG; kelas 2 vs 5+6; CPU vs GPU — **tidak boleh** disimpulkan lebih buruk secara langsung

### Struktur slide yang diminta

1. **Judul** — judul coursework, nama kelompok (isi sendiri), mata kuliah, tanggal.
2. **Disclaimer & tujuan** — disclaimer di atas + tujuan pipeline (deteksi lokasi + klasifikasi impacted/erupted).
3. **Latar belakang** — M3B impacted pada panoramik; importance untuk next step (angulasi Winter/Adams–Lunt).
4. **Tujuan & ruang lingkup** — 3 tujuan pipeline + batasan (CPU-only, dataset 973 OPG, angulasi belum dijalankan).
5. **Dataset** — tabel split & distribusi kelas + gambar `fig_audit_kelas.png`.
6. **Baseline paper** — tabel 3 paper + peran masing-masing + catatan angka E-MTMYOLO/mTMCNN "Tidak dijelaskan".
7. **Arsitektur pipeline** — diagram alur 5 tahap (audit → deteksi YOLO11n → crop → klasifikasi → ringkasan).
8. **Tahap deteksi: konfigurasi** — model, imgsz, epoch, batch, seed, device CPU; gambar `fig_kurva_training_deteksi.png`.
9. **Hasil deteksi** — tabel metrik overall + per kelas + `fig_pr_deteksi.png`.
10. **Confusion matrix deteksi** — gambar `fig_confusion_deteksi.png` + interpretasi singkat (tanpa klaim klinis).
11. **Tahap klasifikasi** — tabel 3 model + gambar `fig_klasifikasi_cnn.png`; tekankan variasi antar-seed.
12. **Demo end-to-end** — gambar `fig_end_to_end.png` + penjelasan warna kotak (hijau e-MTM, merah i-MTM).
13. **Pembahasan & batasan** — tabel batasan (7 baris) + posisi terhadap baseline paper.
14. **Kesimpulan & lanjutan** — 3 kesimpulan + rencana penyambungan klasifikasi angulasi 6 kelas (Winter) + daftar pustaka ringkas.

### Referensi (hanya yang ini boleh dipakai)
- Kayadibi, İ., Köse, U., Güraksın, G. E., & Çetin, B. (2025). E-MTMYOLO. *The Journal of Supercomputing*, 81(13), 1286. https://doi.org/10.1007/s11227-025-07775-w
- Kayadibi, İ., Köse, U., Güraksın, G. E., & Çetin, B. (2025). *Expert Annotated Mandibular Third Molar (ExAn-MTM) Dataset* [Data set]. Mendeley Data. https://doi.org/10.17632/t8k59p35p6.1
- Kayadibi, İ., Köse, U., Güraksın, G. E., & Çetin, B. (2025). An AI-assisted explainable mTMCNN architecture. *International Journal of Medical Informatics*, 195, 105724. https://doi.org/10.1016/j.ijmedinf.2024.105724
- Khurshid, Z., Alsleem, M. H., Aljubairah, F. A., Alghafli, H. A., Alasafirah, A. O., Alibrahim, B. A., Alshamrani, A. A., & Alsuhaymi, A. N. (2026). Dual framework for classification and detection of third molar impaction in panoramic radiographs. *International Dental Journal*, 76(2), 109430. https://doi.org/10.1016/j.identj.2026.109430

### File gambar yang dilampirkan (dari `Pipeline/outputs/figures/`)
- `fig_audit_kelas.png` — slide 5
- `fig_kurva_training_deteksi.png` — slide 8
- `fig_pr_deteksi.png` — slide 9
- `fig_confusion_deteksi.png` — slide 10
- `fig_klasifikasi_cnn.png` — slide 11
- `fig_end_to_end.png` — slide 12
- `fig_contoh_crop.png` — opsional slide 11

Output: file .pptx yang bisa diunduh, plus ringkasan singkat per slide (bullet) untuk disunting.

---

## CATATAN UNTUK PENGGUNA
- Angka di prompt ini diambil otomatis dari `Pipeline/outputs/metrics.json`; ubah pipeline → jalankan ulang
  `Pipeline/scripts/build_laporan.py` → prompt ikut ter-update.
- Kuartil jurnal (Q1/Q2) sengaja tidak dicantumkan: belum diverifikasi sumbernya.
"""
(LAP / "Prompt_PPT_AI.md").write_text(PPT, encoding="utf-8")
print("md:", LAP / "Prompt_PPT_AI.md")

# ---------------------------------------------------------------------------- docx
doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.left_margin = sec.right_margin = sec.top_margin = sec.bottom_margin = Cm(2.5)
TEXT_W = 21 - 5.0  # 16 cm

st = doc.styles["Normal"]
st.font.name = "Calibri"
st.font.size = Pt(11)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
st.paragraph_format.space_after = Pt(6)
st.paragraph_format.line_spacing = 1.15

def H(text, level=1):
    p = doc.add_heading(text, level=level)
    for r in p.runs:
        r.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)
    return p

def P(text, bold=False, italic=False, size=11, align=None):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold, r.italic, r.font.size = bold, italic, Pt(size)
    if align:
        p.alignment = align
    return p

def BUL(items):
    for it in items:
        doc.add_paragraph(it, style="List Bullet")

def TABLE(headers, rows, widths):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]
        c.text = ""
        run = c.paragraphs[0].add_run(h)
        run.bold = True
        c.width = Cm(widths[i])
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = str(v)
            cells[i].width = Cm(widths[i])
    assert abs(sum(widths) - TEXT_W) < 0.01, sum(widths)
    return t

def FIG(name, caption, width=TEXT_W):
    p = FIGS / name
    if not p.exists():
        return
    doc.add_picture(str(p), width=Cm(width))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    P(caption, italic=True, size=9.5, align=WD_ALIGN_PARAGRAPH.CENTER)

# --- cover ---
H("Laporan Pipeline Deteksi Lokasi dan Klasifikasi Impacted/Erupted Molar III Bawah", 0)
P("Dataset ExAn-MTM (973 citra OPG) — YOLO11n (deteksi) + klasifikasi crop", italic=True, size=12)
P("Mata kuliah PCVK — Praktikum Pemrosesan Citra dan Visi Komputer", size=11)
P("Tanggal verifikasi hasil: 25 November 2026", size=11)
P("Artefak: Pipeline/PCVK_Pipeline_Deteksi_Klasifikasi_Impaksi.ipynb (sudah dieksekusi) | "
  "Sumber angka: Pipeline/outputs/metrics.json", size=11)

# --- 1 pendahuluan ---
H("1. Pendahuluan", 1)
H("1.1 Latar belakang", 2)
P("Molar ketiga bawah (mandibular third molar, M3B) yang impacted sering ditemukan pada radiografi panoramik. "
  "Klasifikasi impacted/erupted adalah langkah awal sebelum menentukan tindakan; pada pipeline riset, tahap ini "
  "dipakai sebagai gate menuju klasifikasi yang lebih rinci seperti angulasi (Winter) dan kedalaman "
  "(deepest point by Adams–Lunt). Paper baseline: Khurshid et al. (2026) membangun framework ganda "
  "(deteksi + klasifikasi) untuk impaksi M3B; Kayadibi et al. (2025) merilis dataset ExAn-MTM "
  "sekaligus model deteksi YOLO explainable.")
H("1.2 Tujuan", 2)
BUL(["Mendeteksi lokasi M3B pada citra panoramik (bounding box).",
     "Mengklasifikasikan tiap kandidat sebagai impacted (i-MTM) atau erupted (e-MTM).",
     "Menyiapkan titik sambung agar klasifikasi lanjutan 6 angulasi (Winter) dapat disambungkan tanpa menulis ulang pipeline."])
H("1.3 Ruang lingkup", 2)
P(f"Eksperimen memakai dataset publik ExAn-MTM ({DS['n_images']} citra OPG, lisensi CC BY-NC-ND 4.0), "
  "komputasi CPU-only, dan belum menjalankan klasifikasi angulasi (alasan di Bagian 8).")

# --- 2 tinjauan pustaka ---
H("2. Tinjauan pustaka", 1)
TABLE(["Sumber", "Peran", "Metrik paper"],
      [["Kayadibi et al. (2025), J Supercomput 81(13), 1286 — E-MTMYOLO",
        "Sumber dataset ExAn-MTM; acuan deteksi YOLO multi-kelas", "Tidak dijelaskan"],
       ["Khurshid et al. (2026), Int Dent J 76(2), 109430",
        "Acuan pipeline deteksi + klasifikasi",
        "5.796 OPG; ResNet50+Fine KNN 97,56%; YOLOv11n mAP@0.5:0.95 85,7%; κ = 0,92"],
       ["Kayadibi et al. (2025), Int J Med Inform 195, 105724 — mTMCNN",
        "Acuan deteksi keberadaan M3B", "Tidak dijelaskan"]],
      [6.0, 5.0, 5.0])
P("Kuartil jurnal (Q1/Q2): belum diverifikasi terhadap Scimago/Scopus pada penyusunan laporan ini — "
  "ditulis Tidak dijelaskan.", italic=True, size=10)
P("Dataset: Kayadibi, İ., Köse, U., Güraksın, G. E., & Çetin, B. (2025). Expert Annotated Mandibular Third "
  "Molar (ExAn-MTM) Dataset [Data set]. Mendeley Data. https://doi.org/10.17632/t8k59p35p6.1 — "
  "lisensi CC BY-NC-ND 4.0: training lokal, tidak boleh mengunggah ulang citra ke repo publik.")

# --- 3 data ---
H("3. Data", 1)
H("3.1 Ringkasan dataset (audit file lokal)", 2)
TABLE(["Split", "Citra", "Objek", "e-MTM", "i-MTM", "Box/citra"],
      [[r["split"], r["n_images"], r["n_boxes"], r["n_e_MTM"], r["n_i_MTM"], r["boxes_per_img_mean"]]
       for r in AUDIT] +
      [["Total", DS['n_images'], DS['n_boxes'], DS['n_e_MTM'], DS['n_i_MTM'],
        round(DS['n_boxes'] / DS['n_images'], 3)]],
      [3.0, 2.5, 2.5, 2.5, 2.5, 3.0])
P("Angka per split dari Pipeline/outputs/audit_rekap.csv; kelas 0 = e-MTM (erupted), 1 = i-MTM (impacted). "
  "Setiap citra memiliki 1–2 bounding box.", size=10, italic=True)
FIG("fig_audit_kelas.png", "Gambar 1. Distribusi objek per kelas pada ExAn-MTM (audit file lokal).")
H("3.2 Pembagian data", 2)
P(f"Split resmi dataset dipertahankan: train {DS['split']['train']} citra / valid {DS['split']['valid']} citra. "
  "Dataset tidak memuat ID pasien sehingga patient-level split tidak dapat dibuat — dicatat sebagai batasan. "
  "Data valid tidak pernah dipakai untuk tuning.")

# --- 4 metode ---
H("4. Metode", 1)
H("4.1 Arsitektur pipeline", 2)
BUL(["Audit dataset: hitung citra, objek, distribusi kelas dari file .txt lokal.",
     f"Deteksi lokasi: YOLO11n (COCO pretrained), imgsz {D['imgsz']}, batch {D['batch']}, epochs {D['epochs']}, "
     f"seed {D['seed']}, device CPU; kelas e-MTM dan i-MTM.",
     "Klasifikasi crop: bounding box di-crop (margin 8%) resize 96×96 px; (a) ResNet-18 frozen + Logistic Regression & KNN; "
     "(b) CNN kecil dari nol, 3 seed untuk mengukur variasi antar-run.",
     "Demo end-to-end: citra valid → deteksi → crop → klasifikasi → citra berannotasi.",
     "Ringkasan angka digabung di Pipeline/outputs/metrics.json (sumber angka tunggal laporan)."])
H("4.2 Metrik", 2)
P("Deteksi: precision, recall, mAP@0.5, mAP@0.5:0.95 (overall dan per kelas), confusion matrix biner. "
  "Klasifikasi: accuracy, precision/recall/F1 per kelas, macro-F1, ROC-AUC, bootstrap 95% CI. "
  "Variansi dilaporkan sebagai mean ± std lintas 3 seed.")

# --- 5 hasil ---
H("5. Hasil", 1)
H("5.1 Deteksi lokasi (YOLO11n, split valid resmi)", 2)
TABLE(["Metrik", "Nilai"],
      [["Precision (overall)", f"{O['precision']:.4f}"], ["Recall (overall)", f"{O['recall']:.4f}"],
       ["mAP@0.5", f"{O['map50']:.4f}"], ["mAP@0.5:0.95", f"{O['map50_95']:.4f}"],
       ["Epoch terbaik", f"{D['best_epoch']} dari {D['epochs']}"],
       ["Waktu training", f"{D['train_minutes']:.1f} menit (CPU)"]],
      [8.0, 8.0])
TABLE(["Kelas", "Precision", "Recall", "F1", "mAP@0.5", "mAP@0.5:0.95"],
      [["e-MTM (erupted)", f"{PC['e-MTM']['precision']:.4f}", f"{PC['e-MTM']['recall']:.4f}",
        f"{PC['e-MTM']['f1']:.4f}", f"{PC['e-MTM']['ap50']:.4f}", f"{PC['e-MTM']['ap50_95']:.4f}"],
       ["i-MTM (impacted)", f"{PC['i-MTM']['precision']:.4f}", f"{PC['i-MTM']['recall']:.4f}",
        f"{PC['i-MTM']['f1']:.4f}", f"{PC['i-MTM']['ap50']:.4f}", f"{PC['i-MTM']['ap50_95']:.4f}"]],
      [3.5, 2.5, 2.5, 2.5, 2.5, 2.5])
TABLE(["GT \\ Pred"] + CM_LABELS,
      [[CM_LABELS[i]] + [str(int(v)) for v in CM[i]] for i in range(len(CM))],
      [16.0 / (len(CM_LABELS) + 1)] * (len(CM_LABELS) + 1))
P(f"Confusion matrix deteksi: {CM_NOTE}. Jumlah baris = jumlah GT per kelas "
  f"({sum(CM[0][:-1])} e-MTM, {sum(CM[1][:-1])} i-MTM).", size=9)
FIG("fig_kurva_training_deteksi.png", "Gambar 2. Kurva training deteksi (ultralytics, run yolo11n_exanmtm).")
FIG("fig_confusion_deteksi.png", "Gambar 3. Confusion matrix deteksi pada split valid.")
FIG("fig_pr_deteksi.png", "Gambar 4. Kurva precision–recall deteksi.")
H("5.2 Klasifikasi crop", 2)
TABLE(["Model", "Accuracy", "Macro-F1", "ROC-AUC", "CI95 accuracy", "Catatan"],
      [["ResNet-18 (frozen) + Logistic Regression", f"{LR['accuracy']:.4f}", f"{LR['macro_f1']:.4f}",
        f"{LR.get('roc_auc', 'Tidak dijelaskan')}", f"[{LR['ci95_accuracy'][0]:.4f}, {LR['ci95_accuracy'][1]:.4f}]", "1 run"],
       ["ResNet-18 (frozen) + KNN (k=5)", f"{KNN['accuracy']:.4f}", f"{KNN['macro_f1']:.4f}",
        f"{KNN.get('roc_auc', 'Tidak dijelaskan')}", f"[{KNN['ci95_accuracy'][0]:.4f}, {KNN['ci95_accuracy'][1]:.4f}]", "1 run"],
       ["CNN kecil (96×96)", f"{CNN['accuracy_mean']:.4f} ± {CNN['accuracy_std']:.4f}",
        f"{CNN['macro_f1_mean']:.4f} ± {CNN['macro_f1_std']:.4f}",
        f"{BEST.get('roc_auc', 'Tidak dijelaskan')}",
        f"[{BEST['ci95_accuracy'][0]:.4f}, {BEST['ci95_accuracy'][1]:.4f}] (seed {BEST_SEED})",
        f"3 seed {CNN['seeds']}"]],
      [4.5, 2.4, 2.4, 1.8, 2.7, 2.2])
P(f"Rentang akurasi CNN lintas seed: {CNN['accuracy_min']:.4f} – {CNN['accuracy_max']:.4f}.", size=10)
FIG("fig_contoh_crop.png", "Gambar 5. Contoh crop bounding box per kelas.")
FIG("fig_klasifikasi_cnn.png", f"Gambar 6. Confusion matrix dan ROC klasifikasi crop (CNN, seed terbaik = {BEST_SEED}).")
H("5.3 Interpretasi", 2)
BUL([f"Dataset, kelas, dan komputasi berbeda dari paper baseline (973 vs 5.796 OPG; 2 vs 5+6 kelas; CPU vs GPU), "
      "sehingga angka deteksi dan klasifikasi tidak dapat dibandingkan langsung.",
      f"Distribusi kelas tidak seimbang ({DS['n_e_MTM']} e-MTM vs {DS['n_i_MTM']} i-MTM); metrik per kelas lebih informatif.",
      f"CI95 bootstrap pada {DS['split']['valid']} citra lebar, sehingga selisih < 0,05 antar-model tidak dapat diklaim bermakna."])

# --- 6 pembahasan ---
H("6. Pembahasan", 1)
H("6.1 Posisi terhadap baseline", 2)
P(f"Paper Khurshid et al. (2026) melaporkan YOLOv11n mAP@0.5:0.95 85,7% pada 5.796 OPG; hasil run ini "
  f"(mAP@0.5:0.95 {O['map50_95']:.4f} pada {DS['n_images']} OPG, CPU, {D['epochs']} epoch) lebih rendah. "
  "Faktor yang paling mungkin: ukuran corpus, keterbatasan epoch/CPU, perbedaan definisi kelas. "
  "Tidak disimpulkan sebagaiperformanya lebih buruk karena setup berbeda.")
H("6.2 Dampak ke tahap angulasi (Winter)", 2)
BUL(["Pipeline/outputs/crops/manifest.csv sudah memetakan citra → bounding box → crop.",
      "Label angulasi (kelas 0–5 pada data.yaml paket Multi-Label) tinggal disatukan ke kolom cls manifest.",
      "Kepala klasifikasi tinggal diganti n_classes=6; metrik berpindah dari accuracy ke macro-F1 per kelas.",
      "Citra sumber 6 angulasi belum publik di Mendeley Data (10.17632/xn5bz6fdm6.1 hanya memuat paket label + kode), "
      "sehingga tahap ini ditunda — bukan dikerjakan dengan data tidak terverifikasi."])
H("6.3 Replikasi", 2)
P(f"Notebook dijalankan end-to-end di CPU (torch {M['environment']['torch']}, ultralytics {M['environment']['ultralytics']}); "
  "seed ditetapkan (42 deteksi; 42/1337/2024 klasifikasi CNN); bobot, feature, dan figure tersimpan di "
  "Pipeline/outputs/ sehingga dapat diaudit ulang.")

# --- 7 kesimpulan ---
H("7. Kesimpulan", 1)
BUL([f"Pipeline deteksi + klasifikasi impacted/erupted M3B berjalan pada ExAn-MTM ({DS['n_images']} OPG): "
      f"YOLO11n mAP@0.5 {O['map50']:.4f} / mAP@0.5:0.95 {O['map50_95']:.4f} pada split valid resmi.",
      f"Klasifikasi crop mencapai akurasi {CNN['accuracy_mean']:.4f} ± {CNN['accuracy_std']:.4f} (CNN, 3 seed).",
      "Struktur pipeline siap disambungkan ke klasifikasi angulasi 6 kelas begitu citra sumber publik tersedia.",
      "Semua angka bersifat eksperimen pada data publik — bukan klaim klinis maupun performa alat diagnostik."])

# --- 8 batasan ---
H("8. Batasan dan pekerjaan lanjutan", 1)
TABLE(["No", "Batasan", "Dampak", "Rencana"],
      [["1", f"Corpus kecil ({DS['n_images']} OPG)", "CI bootstrap lebar; generalisasi terbatas",
        "Validasi multi-center bila akses tersedia"],
       ["2", "Split per citra, tanpa ID pasien", "Risiko kebocoran antar citra pasien yang sama",
        "Patient-level split bila ID pasien tersedia; saat ini tidak dapat dibuat"],
       ["3", f"CPU-only, {D['epochs']} epoch", "Model mungkin belum konvergen", "Tambah epoch bila compute tersedia"],
       ["4", "Deteksi dilatih 1 seed", "Variasi mAP antar-run belum diukur", "Ulangi 3 seed bila compute tersedia"],
       ["5", "Klasifikasi dievaluasi pada crop GT", "Domain-shift dari prediksi detektor belum terukur",
        "Evaluasi ulang memakai crop dari prediksi"],
       ["6", "Citra 6 angulasi belum publik", "Tahap Winter belum bisa dijalankan",
        "Ambil dari sumber publik + fetch script + catatan lisensi"],
       ["7", "Lisensi data NC-ND", "Tidak boleh mengunggah ulang citra", "Training lokal; repo hanya berisi kode, config, metrik"]],
      [1.0, 4.6, 5.2, 5.2])

# --- 9 daftar pustaka ---
H("9. Daftar pustaka", 1)
for ref in [
    "Kayadibi, İ., Köse, U., Güraksın, G. E., & Çetin, B. (2025). Expert Annotated Mandibular Third Molar "
    "(ExAn-MTM) Dataset [Data set]. Mendeley Data. https://doi.org/10.17632/t8k59p35p6.1",
    "Kayadibi, İ., Köse, U., Güraksın, G. E., & Çetin, B. (2025). An AI-assisted explainable mTMCNN architecture "
    "for detection of mandibular third molar presence from panoramic radiography. International Journal of "
    "Medical Informatics, 195, 105724. https://doi.org/10.1016/j.ijmedinf.2024.105724",
    "Kayadibi, İ., Köse, U., Güraksın, G. E., & Çetin, B. (2025). E-MTMYOLO: an explainable YOLOv5-based "
    "architecture for accurate detection of mandibular third molar using a novel expert-annotated dataset. "
    "The Journal of Supercomputing, 81(13), 1286. https://doi.org/10.1007/s11227-025-07775-w",
    "Khurshid, Z., Alsleem, M. H., Aljubairah, F. A., Alghafli, H. A., Alasafirah, A. O., Alibrahim, B. A., "
    "Alshamrani, A. A., & Alsuhaymi, A. N. (2026). Dual framework for classification and detection of third "
    "molar impaction in panoramic radiographs. International Dental Journal, 76(2), 109430. "
    "https://doi.org/10.1016/j.identj.2026.109430"]:
    p = doc.add_paragraph(ref)
    p.paragraph_format.left_indent = Cm(1.0)
    p.paragraph_format.first_line_indent = Cm(-1.0)

# --- 10 lampiran ---
H("10. Lampiran", 1)
H("10.1 Struktur keluaran", 2)
code = ("Pipeline/\n"
        "  PCVK_Pipeline_Deteksi_Klasifikasi_Impaksi.ipynb   # notebook (sudah dieksekusi)\n"
        "  data.yaml                                          # konfigurasi YOLO\n"
        "  scripts/build_notebook.py, build_laporan.py         # pembangun artefak\n"
        "  outputs/\n"
        "    metrics.json                # sumber angka tunggal\n"
        "    audit_rekap.csv, audit_dataset.csv, dataset_integrity.json\n"
        "    metrics_deteksi.json, metrics_klasifikasi_feature.json, metrics_klasifikasi_cnn.json\n"
        "    figures/                    # figure untuk laporan & PPT\n"
        "    crops/manifest.csv          # peta citra -> bounding box -> crop (hook angulasi)\n"
        "    runs/yolo11n_exanmtm/       # bobot YOLO + results.csv\n"
        "    annotated/                  # keluaran demo end-to-end")
p = doc.add_paragraph(code)
p.runs[0].font.name = "Consolas"
p.runs[0].font.size = Pt(9)
H("10.2 Perintah replikasi", 2)
p = doc.add_paragraph(
    "uv venv --python 3.12 .venv\n"
    "uv pip install --python .venv/Scripts/python.exe torch torchvision --index-url https://download.pytorch.org/whl/cpu\n"
    "uv pip install --python .venv/Scripts/python.exe ultralytics jupyter nbconvert ipykernel matplotlib pandas "
    "scikit-learn opencv-python seaborn pillow python-docx\n"
    ".venv/Scripts/python.exe -m jupyter nbconvert --to notebook --execute --inplace "
    "Pipeline/PCVK_Pipeline_Deteksi_Klasifikasi_Impaksi.ipynb\n"
    ".venv/Scripts/python.exe Pipeline/scripts/build_laporan.py")
p.runs[0].font.name = "Consolas"
p.runs[0].font.size = Pt(9)
H("10.3 Checklist pelacakan klaim", 2)
TABLE(["Klaim", "Status", "Sumber"],
      [["Jumlah citra, objek, distribusi kelas", "Terverifikasi", "audit file lokal (audit_rekap.csv)"],
       ["Metrik deteksi dan klasifikasi", "Terverifikasi", "metrics.json hasil run"],
       ["Angka paper Khurshid et al. (2026)", "Terverifikasi", "naskah full text paper"],
       ["Kuartil jurnal", "Tidak dijelaskan", "belum diverifikasi ke Scimago/Scopus"],
       ["Angka paper E-MTMYOLO dan mTMCNN", "Tidak dijelaskan", "tidak diambil pada tahap ini"],
       ["Citra 6 angulasi publik", "belum tersedia", "Mendeley xn5bz6fdm6 hanya berisi paket label+kode"]],
      [6.0, 3.0, 7.0])

FIG("fig_end_to_end.png", "Gambar 7. Demo end-to-end: deteksi YOLO11n + klasifikasi crop CNN "
                           "(hijau = e-MTM, merah = i-MTM).")

docx_path = LAP / "Laporan_Pipeline_Deteksi_Klasifikasi_Impaksi.docx"
doc.save(str(docx_path))
print("docx:", docx_path, docx_path.stat().st_size, "bytes")
