# Penjelasan Sel per Sel — Notebook `PCVK_Pipeline_Deteksi_Klasifikasi_Impaksi.ipynb`

Dokumen ini menjelaskan **setiap sel** dalam notebook pipeline: apa yang dikerjakan, kode kuncinya, angka yang
dihasilkan, file yang ditulis, dan jebakan yang perlu diwaspai. Semua angka di bawah diambil dari
`Pipeline/outputs/metrics.json` (sumber tunggal angka laporan) dan dari output notebook yang sudah dieksekusi.

**Ringkasan alur (10 sel kode, harus dijalankan berurutan dari atas):**

| Sel | Nama | Fungsi | Output utama |
|---|---|---|---|
| 1 | SETUP | env, seed, path, konfigurasi eksperimen | `ENV` dict |
| 3 | AUDIT DATASET | hitung citra/objek/kelas dari file label lokal | `audit_rekap.csv`, `audit_dataset.csv`, `fig_audit_kelas.png` |
| 5 | PREP YOLO + INTEGRITAS | tulis `data.yaml`, cek pasangan citra-label | `data.yaml`, `dataset_integrity.json` |
| 7 | TRAINING DETEKSI | latih YOLO11n 20 epoch (CPU) | `runs/yolo11n_exanmtm/weights/best.pt` |
| 9 | EVALUASI DETEKSI | metrik + confusion matrix di split valid | `metrics_deteksi.json`, 3 figure |
| 11 | BUILD CROP | potong bounding box jadi 96×96 + manifest | `crops/manifest.csv`, `fig_contoh_crop.png` |
| 13 | KLASIFIKASI FEATURE | ResNet-18 frozen + LR & KNN | `metrics_klasifikasi_feature.json` |
| 15 | KLASIFIKASI CNN | CNN kecil dari nol, 3 seed | `metrics_klasifikasi_cnn.json`, `fig_klasifikasi_cnn.png` |
| 17 | DEMO END-TO-END | deteksi → klasifikasi crop pada 6 citra | `demo_end_to_end.csv`, `fig_end_to_end.png` |
| 19 | RINGKASAN METRIK | satukan semua angka ke satu file | `metrics.json` |

Sel markdown (0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 21) adalah judul + penjelasan; **tidak ada kode**, aman
di-lewati. Sel 20 menjelaskan cara menambah kelas angulasi Winter 6 kelas, sel 21 menyebut batasan eksperimen.

---

## Sel 1 — SETUP: environment, seed, path, konfigurasi

**Fungsi.** Menyiapkan semua hal yang dipakai sel berikutnya: library, seed acak, folder kerja, dan parameter
eksperimen (imgsz, epochs, batch, device).

**Kode kunci.**

```python
SEED = 42
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)

ROOT = Path(r"C:/Kuliah/Tingkat 3/PCVK/Project")
EXAN = ROOT / "Datasets" / "Expert Annotated Mandibular Third Molar (ExAn-MTM)" / \
       "Expert Annotated Mandibular Third Molar (ExAn-MTM)" / "ExAn-MTM dataset" / "ExAn-MTM dataset"
PIPE = ROOT / "Pipeline"
OUT  = PIPE / "outputs"

CLASSES = {0: "e-MTM", 1: "i-MTM"}     # 0 = erupted, 1 = impacted
IMG_SIZE_CROP = 96
DET = dict(model="yolo11n.pt", imgsz=448, epochs=20, batch=8, workers=2, patience=8)
CNN = dict(epochs=20, batch=32, lr=1e-3, seeds=[42, 1337, 2024])
BOOTSTRAP_N = 2000
```

**Penjelasan.** `seed` dikunci di 42 supaya training bisa diulang dengan hasil yang sama (deterministic=True
juga dipakai di sel 7). `EXAN` menunjuk folder dataset yang berisi `train/` dan `valid/`; nama foldernya
bertingkat karena arsip Mendeley dil extract berlapis. `DET`/`CNN` adalah **satu-satunya tempat** mengubah
setting eksperimen — ubah di sini, bukan di dalam sel.

**Angka/keluaran.** `ENV` (versi python, torch, ultralytics, opencv, sklearn, pandas, numpy, device `cpu`,
jumlah thread, seed, timestamp UTC) dicetak sebagai JSON — ini yang dipakai untuk menulis bagian "lingkungan
eksperimen" di laporan. Dua baris terakhir mencetak jumlah citra train dan valid yang ditemukan.

**Jebakan.** Di Colab, `ROOT` harus diganti ke `/content/PCVK-Tugas-Akhir` dan `EXAN` ke lokasi dataset
yang diunggah; `data.yaml` sendiri tidak perlu diedit (dihasilkan sel 5). Kalau `EXAN` salah, seluruh sel
berikutnya gagal dengan `FileNotFoundError`.

---

## Sel 3 — Audit dataset (sebelum training)

**Fungsi.** Menghitung ulang angka dataset **dari file label lokal**, bukan mengambil klaim paper. Semua
angka laporan yang menyangkut jumlah data berasal dari sini.

**Kode kunci.** `read_labels()` membaca file `.txt` YOLO (format `cls cx cy w h`, semua ternormalisasi) dan
mengabaikan baris yang tidak lengkap. `audit_split()` mencocokkan setiap citra dengan file label-nya, lalu
menghitung `n_box` per citra. Terakhir, `recap` menggabungkan semuanya per split dan per kelas.

**Angka hasil (sudah terverifikasi).**

| Split | Citra | Box | e-MTM | i-MTM | Box/citra |
|---|---|---|---|---|---|
| train | 875 | 1.604 | 624 | 980 | 1,83 |
| valid | 98 | 180 | 63 | 117 | 1,84 |

Total 973 citra / 1.784 objek. Ukuran citra (sampel 120): median 1.991 × 1.127 px.

**File yang ditulis.** `outputs/audit_rekap.csv` (rekap per split), `outputs/audit_dataset.csv` (per citra),
`outputs/figures/fig_audit_kelas.png` (bar chart distribusi kelas train vs valid).

**Jebakan.** Distribusi kelas tidak seimbang (i-MTM 61,5 %). Karena itu laporan memakai **macro-F1**, bukan
akurasi saja — akurasi saja bisa menipu di kelas minoritas.

---

## Sel 5 — Preparasi data YOLO + uji integritas

**Fungsi.** Menulis `data.yaml` yang dipakai Ultralytics, lalu mengecek data tidak berantakan.

**Kode kunci.**

```python
data_yaml = PIPE / "data.yaml"
data_yaml.write_text(
    f"path: {EXAN.as_posix()}\ntrain: train/images\nval: valid/images\n\nnames:\n  0: e-MTM\n  1: i-MTM\n",
    encoding="utf-8", newline="\n")
```

Di bawahnya, untuk tiap split: himpun nama file citra (`*.jpg`) dan label (`*.txt`), lalu bandingkan.
`img_tan_label` = citra tanpa label, `label_tan_img` = label tanpa citra (keduanya harus kosong).

**File yang ditulis.** `Pipeline/data.yaml` (ditulis ulang tiap run — jangan diedit manual, akan tertimpa) dan
`outputs/dataset_integrity.json`.

**Jebakan.** `as_posix()` dipakai supaya separator `/` dipakai walau dijalankan di Windows; Ultralytics
bermasalah dengan `\` di `path`.

---

## Sel 7 — Training deteksi (YOLO11n)

**Fungsi.** Melatih detektor bounding box + kelas molar ketiga. Model `yolo11n` sudah dilatih di COCO
(pretrained), lalu di-fine-tune pada ExAn-MTM.

**Kode kunci — guard agar tidak training ulang.**

```python
_prev_best = OUT / "runs" / "yolo11n_exanmtm" / "weights" / "best.pt"
_prev_csv  = OUT / "runs" / "yolo11n_exanmtm" / "results.csv"
_skip_train = (_prev_best.exists() and _prev_csv.exists()
               and len(pd.read_csv(_prev_csv)) >= DET["epochs"])
```

Kalau run sebelumnya lengkap, training **dilewati** dan `best.pt` langsung dipakai lagi (waktu training diambil
dari kolom `time` di `results.csv`). Ini yang membuat notebook bisa di-re-run dalam hitungan menit tanpa
mengulang 98 menit training. Kalau belum lengkap → `det_model.train(...)` dengan `device="cpu"`,
`deterministic=True`, `patience=8` (early stop).

**Setelah training.** `results.csv` dibaca, baris dengan `metrics/mAP50-95(B)` maksimum dicari → inilah
"epoch terbaik". Baris itu ditampilkan (precision/recall/mAP50/mAP50-95).

**Angka hasil.** Epoch terbaik = **20 dari 20** (belum kena early stop), mAP50 0,9847, mAP50-95 0,6020,
waktu training **98,79 menit** CPU. Tidak ada klaim GPU — semua berjalan di CPU Intel Core i3-1005G1.

**Jebakan.** `yolo11n.pt` diunduh otomatis oleh Ultralytics saat pertama kali jalan; butuh internet. Kalau
offline, taruh file `.pt` manual di folder kerja.

---

## Sel 9 — Evaluasi deteksi pada split valid resmi (98 citra)

**Fungsi.** Menghitung metrik deteksi **di luar training** (split valid resmi) dan menyimpan satu sumber
angka untuk laporan.

**Kode kunci.**

```python
val_res = best_det.val(data=str(data_yaml), imgsz=DET["imgsz"], split="val",
                        plots=True, device="cpu", ...)
rd  = val_res.results_dict      # metrik overall
box = val_res.box               # metrik per kelas (p, r, ap50, ap)
```

Per kelas dihitung manual: `f1 = 2pr/(p+r)` dari `box.p[i]` dan `box.r[i]`.

**Bagian penting — confusion matrix.** Matriks bawaan Ultralytics 8.4.218 dipakai **tidak** karena tidak
konsisten (jumlah kolom terakhir 237, padahal GT hanya 180 box). Sebagai gantinya:

```python
sys.path.insert(0, str(ROOT / "Pipeline" / "scripts"))
import make_cm
make_cm.main()          # IoU 0,5, class-agnostic, conf 0,25 -> confusion_matrix.json
```

`make_cm.py` mencocokkan prediksi dengan ground truth secara greedy dan diverifikasi bahwa jumlah baris
matriks sama dengan jumlah GT per kelas.

**Angka hasil.**

| Metrik | Overall | e-MTM | i-MTM |
|---|---|---|---|
| Precision | 0,9458 | 0,8951 | 0,9964 |
| Recall | 0,9611 | 0,9479 | 0,9744 |
| F1 | — | 0,9207 | 0,9853 |
| mAP@0.5 | 0,9847 | 0,9745 | 0,9948 |
| mAP@0.5:0.95 | 0,6020 | 0,5666 | 0,6373 |

Confusion matrix (baris = GT, kolom = prediksi; kolom terakhir = background/tidak terdeteksi):

```
[[ 61   0   2]
 [  3 114   0]
 [  8   2   0]]
```

Artinya: 2 e-MTM terlewat, 3 i-MTM terlewat, 10 false positive (8 diprediksi e-MTM, 2 i-MTM).

**File yang ditulis.** `outputs/metrics_deteksi.json`, `outputs/confusion_matrix.json`, plus figure yang
disalin dari folder run: `fig_pr_deteksi.png`, `fig_f1_deteksi.png`, `fig_kurva_training_deteksi.png`.

**Jebakan.** `import make_cm` memakai path absolut dari `ROOT`; kalau notebook dijalankan dari working
directory lain, `Path.cwd()` akan salah. Jalankan dari root repo.

---

## Sel 11 — Build dataset crop (tahap klasifikasi)

**Fungsi.** Mengubah bounding box YOLO menjadi potongan citra 96×96 — inilah input klasifikasi tahap 2.

**Kode kunci.**

```python
x1, x2 = (cx - w/2)*W, (cx + w/2)*W      # YOLO normalized -> piksel
pad = 0.08 * max(x2-x1, y2-y1)           # margin 8% sisi terpanjang
crop = cv2.resize(crop, (96, 96), interpolation=cv2.INTER_AREA)
```

Margin 8% dipakai supaya konteks di sekitar gigi masih terlihat (bukan hanya gigi). Potongan yang terlalu kecil
(<5 px) dibuang. Tiap crop disimpan sebagai `outputs/crops/<split>/<kelas>/<nama>_b<index>.jpg`.

**Manifest — kunci reproducible.** Semua metadata crop disimpan di `outputs/crops/manifest.csv`:
`split, image, box_idx, cls, cls_name, crop, box_w_px, box_h_px, area_frac`. Path ditulis relatif terhadap
`ROOT` dengan separator `/` supaya tetap valid di Windows maupun Colab.

**Angka hasil.** Train 1.604 crop (624 e-MTM + 980 i-MTM), valid 180 crop (63 + 117), total 1.784 crop —
sama dengan jumlah bounding box di sel 3, artinya tidak ada crop yang hilang.

**File yang ditulis.** `outputs/crops/**`, `outputs/crops/manifest.csv`, `outputs/figures/fig_contoh_crop.png`
(4 contoh crop: train/valid × e-MTM/i-MTM).

**Kenapa manifest penting.** Nanti kelas angulasi (Winter 6 kelas) cukup ditambahkan sebagai **kolom baru**
di manifest — seluruh pipeline lain tidak berubah.

---

## Sel 13 — Klasifikasi crop: feature + classifier klasik

**Fungsi.** Mengambil fitur dari tiap crop dengan ResNet-18 **pretrained ImageNet yang dibekukan**, lalu
mencoba dua classifier klasik.

**Kode kunci.**

```python
weights = ResNet18_Weights.IMAGENET1K_V1
backbone = resnet18(weights=weights)
backbone.fc = nn.Identity()      # buang kepala 1000-kelas -> jadi extractor 512-d
backbone.eval()                  # tidak dilatih (tanpa gradien)
```

Ekstraksi fitur memakai `torch.no_grad()` → 512 angka per crop. Ada `try/except`: kalau unduh bobot ImageNet
gagal (offline), otomatis jatuh ke `weights=None` (random init) dan dicatat di `feat_stats` — jadi hasilnya
tidak pernah diam-diam berbeda tanpa catatan.

Classifier yang diuji: `LogisticRegression(C=1, max_iter=3000)` dan `KNeighborsClassifier(n_neighbors=5)`.
Fungsi `evaluate()` menghitung akurasi, precision/recall/F1 per kelas, macro-F1, confusion matrix, dan ROC-AUC;
`bootstrap_ci()` menghitung CI 95% akurasi dengan 2.000 resampling.

**Angka hasil (split valid, 180 crop).**

| Classifier | Accuracy | Macro-F1 | ROC-AUC | CI 95% akurasi |
|---|---|---|---|---|
| Logistic Regression | **0,9389** | **0,9326** | 0,9742 | [0,9000 – 0,9722] |
| KNN (k=5) | 0,8667 | 0,8460 | 0,9267 | [0,8167 – 0,9111] |

Feature extraction 1.784 crop ≈ 1–2 menit CPU.

**File yang ditulis.** `outputs/metrics_klasifikasi_feature.json`.

**Kenapa LR menang.** 1.604 contoh itu kecil untuk KNN (butuh banyak tetangga); dengan 512 fitur, regresi
logistik lebih stabil.

---

## Sel 15 — Klasifikasi crop: CNN kecil, 3 seed

**Fungsi.** Bandingkan jalur "deep learning from scratch" dengan jalur feature-based di sel 13, dan laporkan
**variansi antar-run**, bukan hanya run terbaik.

**Kode kunci.**

```python
class SmallCNN(nn.Module):        # 3 blok Conv-BN-ReLU-MaxPool, lalu AdaptiveAvgPool -> Linear(64, 2)
tf_train = transforms.Compose([Resize(96), RandomHorizontalFlip(0.5), RandomRotation(7),
                               ColorJitter(0.15, 0.15), ToTensor(), Normalize(...)])
```

Augmentasi dipakai untuk training saja; evaluasi memakai `tf_eval` (tanpa augmentasi). Optimizer Adam,
lr 1e-3, `CrossEntropyLoss`, 20 epoch. Loop diulang untuk **3 seed (42, 1337, 2024)**.

Setelah itu: `accuracy_mean ± std`, `macro_f1_mean ± std`, CI bootstrap per seed, model terbaik
(`best_seed`) disimpan sebagai `outputs/cnn_crop_best.pt`, dan figure CM + ROC.

**Angka hasil.**

| Seed | Accuracy |
|---|---|
| 42 | 0,8556 |
| 1337 (terbaik) | 0,8722 |
| 2024 | 0,8667 |
| **Rata-rata ± std** | **0,8648 ± 0,0189** |

Macro-F1 0,8543 ± 0,0149; CI 95% akurasi seed terbaik [0,8389 – 0,9278].

**File yang ditulis.** `outputs/metrics_klasifikasi_cnn.json`, `outputs/cnn_crop_best.pt`,
`outputs/figures/fig_klasifikasi_cnn.png`.

**Jebakan.** Angka CNN **di bawah** jalur feature (0,865 vs 0,939) dan CI-nya tumpang tindih dengan LR.
Kesimpulan|report: dengan 1.604 crop, dataset terlalu kecil untuk dilatih CNN dari nol; pretrained +
classifier klasik lebih hemat dan lebih akurat. Jangan klaim "CNN lebih baik".

---

## Sel 17 — Demo end-to-end (deteksi → klasifikasi crop)

**Fungsi.** Menunjukkan alur kerja nyata: citra OPG → YOLO memberi kotak + kelas → tiap kotak dipotong →
CNN crop memberi kelas kedua. Ini alur yang akan dipakai nanti saat kelas angulasi ditambahkan.

**Kode kunci.**

```python
r = best_det.predict(img, imgsz=DET["imgsz"], conf=0.25, device="cpu")[0]
boxes   = r.boxes.xyxy.tolist()
det_cls = [CLASSES[int(c)] for c in r.boxes.cls.tolist()]
cls_out = classify_crops_from_image(img, boxes, cnn_runs[best_seed][0])
```

Kotak digambar hijau (e-MTM) / merah (i-MTM) dengan teks `kelas detektor conf | kelas crop conf`. Enam citra
valid pertama diproses, hasilnya disimpan ke `outputs/demo_end_to_end.csv` dan dirakit jadi montage
`fig_end_to_end.png`.

**Angka hasil.** Contoh ada satu kasus berbeda: `cate1-00007.jpg` → detektor bilang i-MTM (0,732), klasifikasi
crop bilang e-MTM (0,565). Kasus seperti ini yang perlu diperiksa visual sebelum dipakai sebagai bukti
kualitas — jangan dipakai sebagai klaim performa.

**Jebakan.** Demo memakai model CNN (bukan LR), karena bobot CNN tersimpan di `.pt`; jalur LR tidak disimpan
sebagai objek terpisah.

---

## Sel 19 — Ringkasan metrik (satu sumber angka)

**Fungsi.** Menggabungkan audit + deteksi + klasifikasi ke dalam **satu file** `outputs/metrics.json`.

**Aturan penting.** Semua angka di laporan harus dibaca dari `metrics.json`, bukan diketik ulang. Ini
mencegah angka berbeda antar bab (misalnya 0,939 vs 0,9389) dan membuat laporan bisa diaudit.

**Isi file.** `project`, `dataset` (nama, DOI, lisensi, jumlah citra/objek/kelas, split), `environment`,
`detection` (lengkap dengan confusion matrix), `klasifikasi.feature_based`, `klasifikasi.cnn`.

**Cetakan.** Ringkasan satu baris per bagian, contoh:

```
[data] 973 citra, 1784 objek (e-MTM 687 / i-MTM 1097), split train 875 / valid 98
[deteksi YOLO11n] mAP@0.5 0.9847 | mAP@0.5:0.95 0.6020 | P 0.9458 | R 0.9611 | epoch terbaik 20
[klasifikasi LogisticRegression(C=1)] acc 0.9389 macroF1 0.9326 CI95 [0.9, 0.9722] AUC 0.9742
```

---

## Sel 20 — Ekstensi: kelas angulasi (Winter 6 kelas)

Sel markdown, tidak ada kode. Memetakan tabel "yang perlu → file → yang diubah":

| Yang perlu | File | Yang diubah |
|---|---|---|
| Citra sumber 6 angulasi | arsip dataset m-TM / mirror Kaggle | pasangan nama `p*`/`t*` |
| Peta label angulasi | `crops/manifest.csv` | tambah kolom `angulation` per crop |
| Kepala klasifikasi | sel 1 (`CNN`) + `class SmallCNN` | `n_classes=6`, metrik → macro-F1 per kelas |
| Deteksi lanjutan | `Pipeline/data.yaml` | kelas baru + label YOLO |

Intinya: pipeline **tidak** ditulis ulang, cukup ditambah label dan diubah kepala klasifikasi.

---

## Sel 21 — Batasan & hal yang belum diukur

Sel markdown, daftar jujur tentang apa yang **belum** terbukti:

* CPU-only; deteksi dilatih 1 seed (42) → variasi antar-run belum diukur.
* Split valid kecil (98 citra / 180 objek) → CI bootstrap lebar.
* Split per citra, bukan per pasien (dataset tidak memuat ID pasien).
* Klasifikasi pada tahap evaluasi memakai crop dari **ground truth**, bukan crop dari prediksi detektor →
  dampak domain-shift belum diukur.
* Kelas angulasi 6 kelas belum dijalankan.
* Tidak ada klaim klinis; hasil ini eksperimen pada data ExAn-MTM.

---

## Kalau mau menjalankan ulang

1. Jalankan sel 1–5 (persiapan, < 1 menit).
2. Sel 7: **boleh dilewati** kalau `outputs/runs/yolo11n_exanmtm/` sudah ada run lengkap; kalau tidak, training
   ± 99 menit CPU. Di Colab dengan GPU jauh lebih cepat.
3. Sel 9–19 berurutan; total ± 10 menit (feature extraction + CNN 3 seed + demo).
4. Setelah selesai, bangun ulang laporan dari angka yang sama:
   ```
   python Pipeline/scripts/build_laporan.py
   ```
5. Kalau angka di sel 19 berubah, angka laporan **wajib** dibangun ulang — jangan menyalin angka lama.
