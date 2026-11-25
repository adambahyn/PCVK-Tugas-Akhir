# 01 — Laporan Audit Jurnal & Dataset
**Proyek:** Deteksi dan Klasifikasi Posisi Gigi Impaksi Geraham Ketiga (M3) pada Radiograf Panoramik
**Tanggal audit:** 9 November 2026 · **Lokasi:** `C:\Kuliah\Tingkat 3\PCVK\Project`
**Metode:** baca penuh 7 PDF (pdftotext -layout, halaman dirujuk), cek DOI/jurnal/lisensi ke sumber penerbit, ekstraksi + hitung ulang seluruh dataset dengan `Analysis/06_Audit_Dataset.py` (read-only).

> Sistem yang dibangun adalah prototipe penelitian dan alat bantu edukasi, bukan alat diagnosis medis.

---

## FASE 1 — Inventaris & verifikasi identitas

### 1.1 Jurnal (7 PDF, tidak ada subfolder)
| File | Identitas sebenarnya (dari isi) | DOI | Status |
|---|---|---|---|
| `applsci-13-09970.pdf` | Lei Y., Chen X., Wang Y., Tang R., Zhang B. — *A Lightweight Knowledge-Distillation-Based Model for the Detection and Classification of Impacted Mandibular Third Molars*, **Applied Sciences 13(9970), 2023** | 10.3390/app13179970 | Peer review terbukti (Academic Editor Kathrin Becker; submit 30-06-2023, accept 15-08-2023) |
| `s41598-024-82915-5.pdf` | Ulusoy A.C., Toprak T., Selver M.A., Güneri P., İlhan B. — *Panoramic radiographic features for ML based detection of M3M root and IAC contact*, **Scientific Reports 15:4178 (2025)** | 10.1038/s41598-024-82915-5 | Peer review terbukti (received 14-02-2024, accepted 10-12-2024) |
| `healthcare-13-02904.pdf` | Ateş G., Türk F., Akçin E.T., Güngör M. — *Decision-Support for Restorative Dentistry…*, **Healthcare 13:2904 (2025)** | 10.3390/healthcare13222904 | Peer review terbukti (editor Daisuke Ekuni; accept 12-11-2025) |
| `41598_2025_Article_93783.pdf` | Balel Y., Sata K. — *Deep learning-based approach to third molar impaction analysis with clinical classifications*, **Scientific Reports 15:23688 (2025)** | 10.1038/s41598-025-93783-y | Peer review terbukti (received 01-12-2024, accepted 10-03-2025) |
| `main.pdf` | Khurshid Z. dkk. — *Dual Framework for Classification and Detection of Third Molar Impaction in Panoramic Radiographs*, **International Dental Journal 76 (2026) 109430** | 10.1016/j.identj.2026.109430 | Peer review terbukti (received 26-11-2025, accepted 12-01-2026; CC BY 4.0) |
| `mbcb240248.pdf` | Kandagal Veerabhadrappa S., Vengusamy S., Padarha S., Iyer K., Yadav S. — *Fully automated deep learning framework for detection and classification of impacted mandibular third molars*, **J Oral Med Oral Surg 31:7 (2025)** | 10.1051/mbcb/2025008 | Peer review terbukti (received 20-11-2024, accepted 03-02-2025) |
| `7743-19068-1-PB.pdf` | Wihasti W.P., Suseno J.E., Widodo C.E. — *Deep Learning-Based Classification of Impacted Teeth from Panoramic Radiographic Images*, **IJPSAT 55(1):524–534, Jan 2026** | **tidak ada DOI** | **Tidak ada bukti peer review** (tanpa tanggal submit/accept, tanpa editor, "© 2026 Scholar AI LLC") |

### 1.2 Dataset (4 entitas, isi aktual)
| Entitas | Isi nyata | Lisensi resmi (terverifikasi) |
|---|---|---|
| `archive/` | = **CONTACT dataset** (Kaggle `tugcetoprak92/contact-dataset`), 1478 citra + 1478 masker, anotasi poligon M3M & kanal alveolar inferior (IAC), + 2 tabel fitur radiografis | CC BY-NC-ND 4.0 (mengikuti artikel s41598-024-82915-5); status lisensi Kaggle belum terverifikasi |
| `Expert Annotated Mandibular Third Molar (ExAn-MTM)` | 973 citra, bbox YOLO, 2 kelas e-MTM / i-MTM. Turunan m-TM | CC BY-NC-ND 4.0 (Mendeley 10.17632/t8k59p35p6.1, 2025-09-01) |
| `Mandibular Third Molar (m-TM) Dataset` | 1317 citra, folder per sisi L+/L−, tanpa bbox. Turunan dataset UESB (Silva dkk. 2018) | CC BY-NC-SA 4.0 (Mendeley 10.17632/xn5bz6fdm6.1, 2024-12-03) |
| `Multi-Label Classification and Detection of Third` | **label saja**: 686 file label, 1796 objek, 12 kelas dideklarasikan, **0 citra**; + fitur deep `.npy` + bobot YOLO | CC BY 4.0 (Mendeley 10.17632/ckt876jzr6.1, 2025-07-07) |

Rantai lineage: **UESB → m-TM → ExAn-MTM**; `archive` (CONTACT) dan multi-label berasal dari sumber lain.

---

## FASE 2 — Ringkasan kritis per artikel (metodologi, hasil, kesimpulan, fitur)

### A. `main.pdf` — Khurshid dkk., Int Dent J 2026 (TERKUAT)
- **Tugas:** dua framework — deteksi bbox (YOLOv10 / YOLOv11n) + klasifikasi 6 kelas angulasi (ResNet50 / InceptionNetV3 + classifier ML klasik).
- **Dataset:** Mendeley `10.17632/ckt876jzr6.1` (CC BY 4.0), **5796 panoramik**, split train 1796 / val 2000 / test 2000, anotasi bbox via CVAT, Cohen κ = 0.92.
- **Kelas (6), jumlah instans (Tabel 1, hlm. 5):** Distoangular 1470, Mesioangular 1100, Vertical 939, Horizontal 817, Inverted 736, Buccolingual 734 — relatif seimbang (15–25% per kelas).
- **Hasil:** klasifikasi terbaik ResNet50 + Fine KNN **acc 97.56 / P 96.07 / R 96.21 / F1 96.10** (hlm. 6). Deteksi YOLOv11n **mAP@0.5 88.90**, mAP@0.5:0.95 85.70, 19.7 GFLOPs; YOLOv10 87.60 / 84.20 (hlm. 7). mAP@0.5 per kelas: Buccolingual 97.4, Inverted 99.6, Mesioangular 82.1, Horizontal 82.1, Distoangular 86.1, Vertical 84.9.
- **Fitur:** Deep features (embedding ResNet50/InceptionNetV3 + classifier klasik). Klaim "handcrafted feature representations" di hlm. 2 **tidak didukung metode apa pun**.
- **Kelemahan yang harus dikutip di laporan kita:** Tabel 3 bergeser baris (atribusi classifier↔metrik tidak pasti dari tabel); angka 100% di Tabel 4 mencurigakan; sitasi dataset di teks menunjuk ref 22/23 yang salah; metrik per kelas tidak dilaporkan; satu label per citra padahal citra bisa punya 2+ impaksi.
- **Verdict fitur:** **Deep features**.

### B. `s41598-024-82915-5.pdf` — Ulusoy dkk., Sci Rep 2025 (TERKUAT UNTUK FITUR HANDCRAFTED)
- **Tugas:** deteksi kontak akar M3M–IAC (biner) dari panoramik; bukan Winter.
- **Dataset:** **CONTACT** publik (Kaggle, 1478 M3M / 1010 pasien dari 4454 CBCT; 1100 kontak vs 377 non-kontak; 4 alat panoramik). Anotasi poligon IAC+M3M (Colabeler), κ inter-rater hanya **0.43**.
- **Fitur handcrafted (6, dari indikator radiologis):** Obscuration, Deflection, Narrowing of roots, Narrowing of canal, Discontinuity of canal, Canal deviation — formula `(I_dentin − I_root)/(I_dentin + I_root)`, skeleton + slope piecewise-linear, kriteria penyempitan 20% (hlm. 6–8).
- **Hasil:** ANN6 (fitur) **acc 85.45, F1 90.76, SE 86.36, SP 81.92** vs 7 CNN pretrained pada ROI (acc 72.9–74.7, SP 5.3–37.3) dan CNN pada semantic annotation (maks 79.9; hybrid 80.5) (hlm. 10). Radiolog 76.65 / 82.40.
- **Verdict fitur:** **Handcrafted terbukti** — DL diberi kesempatan setara dan tetap kalah pada SP/F1/akurasi.

### C. `mbcb240248.pdf` — Kandagal dkk., J Oral Med Oral Surg 2025 (BLUEPRINT DUA TAHAP)
- **Tugas:** pipeline dua tahap: deteksi M3M (VGG16/STMD, +YOLOv7 pembanding) → klasifikasi **Winter 4 kelas** (ResNet50) dari ROI crop. **Struktur paling mirip target proyek kita.**
- **Dataset:** privat, 1100 panoramik berisi 1200 IMTM + 711 panoramik tanpa M3 (true negative); DICOM 2943×1435 → 224×224; bbox LabelImg (mahkota+akar); split 70/20/10.
- **Hasil:** deteksi test acc 93.51 / P 94.64 / R 89.47 / F1 91.97 (hlm. 3); klasifikasi Winter test acc 92.17, AUC 98.28, F1 91.7 (hlm. 4). **Metrik per kelas Winter tidak dilaporkan.** Distribusi Winter (Tabel I): Vertical 368, Mesioangular 328, Horizontal 295, Distoangular 209.
- **Kelemahan diakui:** buccolingual & inverted dikecualikan (jarang), molar kedua tidak dianotasi padahal dipakai menilai angulasi (hlm. 9) — batasan ini berlaku juga untuk rencana kita.
- **Verdict fitur:** **End-to-end** (Sobel hanya praproses).

### D. `41598_2025_Article_93783.pdf` — Balel & Sata, Sci Rep 2025 (SKEMA LABEL KLINIS TERLENGKAP)
- **Tugas:** YOLOv11 deteksi + klasifikasi sekaligus lewat **block labeling**: satu label = `38-Mesioangular-Position A-Class I` (kuadran + Winter + Pell-Gregory kedalaman + kelas ramus). **98 label unik.**
- **Dataset:** privat, 3830 panoramik (2014–2024, satu alat Instrumentarium OP200 D, 66 kVp/10 mA); split 2300/765/765; objek 7624/2580/2493.
- **Hasil test:** P 0.980, R 0.948, F1 0.974, mAP@50 **0.990**, mAP@50:95 0.974, 12.8 ms/inferensi (hlm. 1, 3, 5).
- **Jebakan yang wajib dicatat:** label `48-Distoangular-C-II` F1 **0.000**, `48-Distoangular-C-III` 0.633 (hlm. 4) → 98 kelas terlalu halus untuk ukuran data; model gagal total pada kelas jarang.
- **Verdict fitur:** **Deep features**.

### E. `applsci-13-09970.pdf` — Lei dkk., Appl Sci 2023 (DETEKSI 6 KELAS WINTER, DATA PRIVAT)
- **Dataset:** privat 1645 panoramik (Lanzhou, Gendex Orthoralix 9200 DDE), DICOM → JPG 2720×1444, bbox mencakup **M2 + M3** (sesuai definisi angulasi Winter), LabelImg, split 8:1:1.
- **Hasil:** YOLOv5s-x (distilasi) **mAP 0.925** vs YOLOv5s 0.896, YOLOv7 0.920, YOLOv8n 0.913, YOLOv8s 0.918, DETR 0.874 (hlm. 8). **Tidak ada P/R/F1, tidak ada mAP per kelas, hyperparameter tidak dilaporkan.**
- **Kelemahan:** dataset tidak dirilis ("Due to privacy restrictions…", hlm. 11) → tidak dapat direproduksi.
- **Verdict fitur:** **Deep features / end-to-end**.

### F. `healthcare-13-02904.pdf` — Ateş dkk., Healthcare 2025 (BUKTI HANDCRAFTED, TOPIK BERBEDA)
- **Tugas:** deteksi **restorasi gigi** (filling, implant, RCT, bridge, crown) — **bukan molar ketiga**. Relevansi = metodologi fitur.
- **Dataset:** privat 353 panoramik / 2137 restorasi, satu alat (Morita Veraviewepocs X-550), 2775×1504 → crop 1700×880 → 224².
- **Hasil:** GLCM (5 deskriptor × 4 sudut, 64 level, d=1) + seleksi **HGWO-PSO** + SVM RBF **73.15%** mengalahkan CNN from-scratch 68.52% (paired t-test p<0.05); CI bootstrap [71.1, 75.2] (hlm. 11).
- **Verdict fitur:** **Handcrafted terbukti** (hanya pada rezim data kecil; penulis sendiri membatasi klaim, hlm. 15).

### G. `7743-19068-1-PB.pdf` — Wihasti dkk., IJPSAT 2026 (TIDAK LAYAK)
- 2000 citra (1200 dari RSUD Margono Soekarjo + 800 dari "a Kaggle repository" **tanpa nama/URL**), label biner impacted/non-impacted, CNN 224², test acc 94.65. Tanpa DOI, tanpa bukti peer review, tanpa identitas dataset, tanpa split per kelas. **Tidak boleh jadi acuan utama.**

---

## FASE 3 — Keputusan: 4 artikel terbaik

| Peringkat | Artikel | Peran dalam proyek | Alasan masuk |
|---|---|---|---|
| 1 | **Khurshid dkk. 2026** (`main.pdf`, Int Dent J) | acuan utama deteksi + klasifikasi 6 kelas; sumber dataset Mendeley | Satu-satunya yang datasetnya publik & jelas, metrik per kelas dilaporkan, κ=0.92, dua tahap lengkap |
| 2 | **Ulusoy dkk. 2025** (`s41598-024-82915-5`, Sci Rep) | acuan jalur **fitur handcrafted** + sumber dataset `archive` | Bukti eksperimental handcrafted > CNN untuk tugas M3M pada panoramik; dataset dapat diakses |
| 3 | **Kandagal dkk. 2025** (`mbcb240248`, JOMOS) | blueprint arsitektur dua tahap deteksi → Winter 4 kelas | Struktur = target proyek; Winter 4 kelas persis |
| 4 | **Balel & Sata 2025** (`41598_2025_93783`, Sci Rep) | acuan skema label klinis (Winter + Pell-Gregory) & batas granularitas label | Bukti bahwa 98 kelas gagal di kelas jarang → justifikasi membatasi ke 4–6 kelas |

**Ditolak sebagai acuan utama:**
- `healthcare-13-02904` — objek riset restorasi, bukan molar ketiga. **Dipindah ke acuan metodologi fitur** (bagian handcrafted), bukan acuan domain.
- `applsci-13-09970` — dataset privat, tanpa P/R/F1 dan tanpa metrik per kelas → tidak dapat direproduksi/dibandingkan.
- `7743-19068-1-PB` — tanpa DOI, tanpa bukti peer review, dataset tak teridentifikasi.

---

## FASE 4 — Audit dataset (angka aktual, hasil `06_Audit_Dataset.py`)

Ringkasan (detail: `03_Audit_Dataset.csv`, `04_Distribusi_Kelas.csv`, `audit_raw.json`):

| Dataset | Citra | File dibuka | Rusak | Objek | Resolusi | Ukuran | Anotasi |
|---|---|---|---|---|---|---|---|
| `archive` (CONTACT) | 1478 (+1478 masker) | 2956/2956 | 0 | — | **227×227** (semua) | 16.8 MB | masker semantik 227² |
| ExAn-MTM | 973 | 973/973 | 0 | 1784 bbox | 1991×1127 | 144.2 MB | YOLO, **0 bbox invalid** |
| m-TM | 1317 | 1317/1317 | 0 | — | 1991×1127 | 196.1 MB | folder per sisi |
| Multi-Label | **0** | — | — | 1796 (dari label) | — | 45 KB label + 71 MB fitur/bobot | label YOLO + fitur `.npy` |

### 4.1 Kelas & distribusi nyata
- **ExAn-MTM:** kelas 0 = **e-MTM (erupted)** 687 objek/437 citra (38.5%); kelas 1 = **i-MTM (impacted)** 1097 objek/608 citra (61.5%). Split resmi: train 875 citra/1604 obj, valid 98 citra/180 obj. **Tidak ada data.yaml** → nama kelas harus diambil dari deskripsi Mendeley, bukan dari file.
- **m-TM:** `m-M3(L+,R+)` 810, `m-M3(L−,R−)` 344, `m-M3(L−,R+)` 89, `m-M3(L+,R−)` 74. **Prefix nama file `cate1`–`cate10` tidak terdokumentasi** (cate8 436, cate2 215, cate4 138, cate5 112, cate7 110, cate10 106, cate1 73, cate3 44, cate9 42, cate6 41) dan **tidak berkorelasi bersih dengan folder sisi** → jangan dipakai sebagai label.
- **Multi-Label:** 12 kelas dideklarasikan di `data.yaml` (Mesioangular, Vertical, Distoangular, Horizontal, Buccolingual, Inverted, CD-1…CD-6). **Aktual hanya kelas 0–5 muncul.** Objek: Vertical 702, Horizontal 517, Mesioangular 313, Distoangular 137, Buccolingual 60, Inverted 7, CD-1 21, CD-2 14, CD-3 4, CD-4 20, CD-5 1, **CD-6 = 0**. Per subset: Pak-1 111 label file/204 objek, Pak-2 41/121, TH-1 28/35, TH-2 506/1436.
- **archive/CONTACT:** dua tabel fitur `trainImageFeatures.xlsx` (1034×8) dan `testImageFeatures.xlsx` (444×8): `ImageNum, Obscuration, Deflection, NarrowingRoots, NarrowingCanal, DiscontinuityCanal, CanalDeviation, Class`. Rasio luas masker rata-rata 0.159 (0.090–0.321) → objek besar, mendominasi citra 227².

### 4.2 Integritas & kebocoran data (temuan kritis)
1. **ExAn-MTM adalah subset m-TM.** 973 dari 973 file ExAn punya MD5 identik dengan file m-TM bernama sama. **Dilarang** memakai keduanya sebagai train/test berbeda → kebocoran 100%.
2. Duplikat internal: ExAn 970 hash unik dari 973 (3 file ganda); m-TM 1312 dari 1317 (5 ganda); pasangan near-duplicate (dHash, Hamming ≤ 2): ExAn 16, m-TM 19. Pada 5796 citra multi-label tidak dapat diperiksa (citra tidak ada).
3. **Multi-Label tidak dapat dilatih.** Repositori Mendeley hanya berisi label + kode + fitur + bobot ("Apart from this READ ME file, this repository contains…"), **tanpa citra**. Jalur `data/images/train/p330.png` menunjuk citra yang tidak pernah dirilis; artikel menyebut sumbernya ref 22/23 yang justru bukan dataset molar ketiga.
4. **Skema label multi-label tidak konsisten dengan isi rilis:** fitur `.npy` berlabel vektor **5 kolom multi-hot** (train 7750×1024, val 970, test 971) sedangkan `data.yaml` mendeklarasikan **12 kelas** dan artikel menulis **6 kelas** → tiga skema berbeda dalam satu rilis.
5. **`archive` bukan 2700×1249.** Artikel menulis PR di-rescale ke 2700×1249; file yang dirilis adalah crop 227×227. Konsekuensi: detail akar/kanal untuk fitur *narrowing/discontinuity* kemungkinan hilang → fitur pada `.xlsx` **tidak dapat dihitung ulang** dari citra 227².
6. **Lisensi membatasi:** m-TM **BY-NC-SA** dan ExAn-MTM/CONTACT **BY-NC-ND** → hanya non-komersial, **tanpa karya turunan** (ND) untuk ExAn/CONTACT. Untuk laporan kampus: boleh, wajib sitasi; **tidak boleh** merilis ulang model/derivatif dataset.
7. Tidak ditemukan citra rusak, format campur, atau anotasi bbox di luar rentang pada semua dataset yang punya citra (`bbox_invalid = 0`).

### 4.3 Kesesuaian dengan target 4 kelas Winter
| Dataset | Winter 4 kelas? | Bukti |
|---|---|---|
| Multi-Label | **Ya, deklaratif** (Mesio/Vertical/Disto/Horizontal + 2 ekstra) | `data.yaml`; tetapi **tanpa citra** → tidak dapat dipakai |
| ExAn-MTM | **Tidak** | hanya e-MTM / i-MTM |
| m-TM | **Tidak** | hanya ada/tidaknya impaksi per sisi |
| archive/CONTACT | **Tidak** | kontak M3M–IAC (biner), geometri poligon M3M, **M2 tidak dianotasi** |

**Kesimpulan Fase 4: tidak ada satu pun dataset lokal yang menyediakan (citra + bbox + label Winter 4 kelas) sekaligus.** Memaksakan pemetaan e/i-MTM → Winter adalah kesalahan metodologis.

---

## FASE 5 — Dataset utama & cadangan

**Utama (Tahap 1 — deteksi):** **ExAn-MTM** — 973 citra 1991×1127, YOLO siap pakai, 1784 bbox valid, 0 rusak, split resmi 875/98, CC BY-NC-ND.
- Tahap 2 pada dataset ini hanya dapat mengklasifikasi **e-MTM vs i-MTM** (label nyata, 61.5% : 38.5%).

**Cadangan / uji generalisasi:** **m-TM** (1317 citra) — **hanya** sebagai test-set eksternal setelah file yang beririsan dengan ExAn dibuang (973 file), menyisakan **344 citra** unik; label tetap level-sisi (ada/tidak impaksi).

**Cadangan untuk jalur handcrafted:** **CONTACT/`archive`** — 1478 citra 227² + masker + tabel 6 fitur radiografis; dipakai untuk mereplikasi bukti handcrafted (Ulusoy) dan sebagai studi banding ROI IAC, bukan untuk Winter.

**Untuk mencapai target Winter 4 kelas (keputusan yang harus diambil dosen/pemilik proyek):**
- Opsi A (paling sahih): anotasi manual subset ExAn-MTM (~300–500 citra, dua anotator, hitung κ) memakai sumbu panjang M3 vs M2 → label Winter. Ini justru kontribusi orisinal skripsi.
- Opsi B: minta citra 5796 kepada penulis Khurshid dkk. via Mendeley (lisensi CC BY 4.0 memungkinkan) → label 6 kelas sudah tersedia.
- Opsi C (paling lemah, harus dinyatakan eksplisit sebagai keterbatasan): Winter dihitung otomatis dari bbox M3 + M2 yang dideteksi model sendiri → label sirkular, tidak boleh dilaporkan sebagai ground truth.

**Yang dilarang dipakai:** dataset multi-label sebagai data latih (tidak ada citra); ExAn + m-TM dalam satu split (duplikat 100%); prefix `cate1`–`cate10` sebagai label.

---

## FASE 6 — Pipeline yang direkomendasikan

Lihat `05_Rencana_Pipeline.md`. Ringkas: YOLO (deteksi M3/ROI) → crop ROI → dua jalur pembanding (a) deep: classifier CNN, (b) handcrafted: fitur geometri/texture dari ROI + classifier klasik. Evaluasi: mAP@0.5 & mAP@0.5:0.95 untuk deteksi; accuracy, macro-F1, confusion matrix, dan **metrik per kelas** untuk klasifikasi; split dikunci per-pasien; uji kebocoran dengan hash sebelum training.

---

## Kesimpulan keputusan
1. Empat artikel acuan: **Khurshid 2026, Ulusoy 2025, Kandagal 2025, Balel 2025**; `healthcare-13-02904` tetap dipakai **hanya** sebagai acuan metode fitur handcrafted (GLCM+HGWO-PSO); `applsci` dan IJPSAT tidak dipakai sebagai acuan utama.
2. Dataset utama **ExAn-MTM** (deteksi) + **m-TM** sebagai test eksternal bersih (344 citra) + **CONTACT** untuk jalur handcrafted.
3. Target Winter 4 kelas **belum tersedia** pada data lokal; harus melalui anotasi sendiri (Opsi A) atau permintaan data ke penulis (Opsi B). Jika tidak ditempuh, klaim proyek harus diturunkan menjadi deteksi + klasifikasi e-MTM/i-MTM.
4. Semua dataset berlisensi non-komersial (BY-NC-*): gunakan untuk riset/edukasi, jangan redistribusi citra.