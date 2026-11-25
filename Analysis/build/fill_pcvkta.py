"""Isi tabel pcvkTA.docx tanpa mengubah template (hanya sel tabel)."""
import copy

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

SRC = r"C:\Kuliah\Tingkat 3\PCVK\Project\Analysis\build\pcvkTA.docx"
OUT = r"C:\Kuliah\Tingkat 3\PCVK\Project\Analysis\pcvkTA_terisi.docx"
DIAG = r"C:\Kuliah\Tingkat 3\PCVK\Project\Analysis\build\diagram_alur5.png"

d = Document(SRC)
T = d.tables


def fill(cell, text, size=8.5, bold=False):
    """Tulis teks ke sel, pertahankan properti paragraf yang ada."""
    p = cell.paragraphs[0]
    for extra in cell.paragraphs[1:]:
        extra._element.getparent().remove(extra._element)
    for r in list(p.runs):
        r._element.getparent().remove(r._element)
    lines = str(text).split("\n")
    for i, ln in enumerate(lines):
        if i:
            p = cell.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(ln)
        run.font.size = Pt(size)
        run.bold = bold


def row(table, idx, values, start_col=3, size=8.5):
    cells = table.rows[idx].cells
    for j, v in enumerate(values):
        fill(cells[start_col + j], v, size=size)


# ------------------------------------------------------------------ T0 identitas
fill(T[0].rows[5].cells[1], "Deteksi dan klasifikasi posisi impaksi molar ketiga mandibula "
                            "pada radiograf panoramik (citra medis 2D)", size=10)
fill(T[0].rows[6].cells[1], "Radiograf panoramik dental (orthopantomogram/OPG), grayscale 2D", size=10)
fill(T[0].rows[7].cells[1], "9 November 2026", size=10)

# ------------------------------------------------------------------ T2 Tabel A
A = [
 ["✓ 2026", "✓ 2025", "✓ 2025", "✓ 2025"],
 ["✓ OPG 2D (radiograf panoramik dental)",
  "✓ OPG 2D (radiograf panoramik dental)",
  "✓ OPG 2D (radiograf panoramik dental)",
  "✓ OPG 2D — objek restorasi gigi, bukan molar ketiga"],
 ["✓ YOLOv10 dan YOLOv11n (deteksi); ResNet50/InceptionNetV3 + 10 classifier klasik",
  "✓ ANN-MLP 6-35-1; pembanding 2 CNN kustom dan 7 CNN pretrained",
  "✓ VGG16 (deteksi) dan ResNet50 (klasifikasi); YOLOv7 pembanding",
  "✓ SVM-RBF, KNN, Decision Tree, Random Forest, CNN kustom"],
 ["✓ Deep: feature map YOLO dan embedding ResNet50/InceptionNetV3",
  "✓ 6 fitur radiologis terukur (darkening akar, interupsi dan defleksi IAC, penyempitan akar/IAC)",
  "✓ End-to-end: fitur dipelajari lapisan konvolusi; Sobel dan OCR hanya praproses",
  "✓ GLCM: contrast, correlation, energy, homogeneity, entropy"],
 ["✗ murni deep (embedding CNN, bukan fitur terukur)",
  "✓ 6 fitur handcrafted terukur",
  "✗ end-to-end tanpa fitur terukur",
  "✓ GLCM 20 fitur + seleksi metaheuristik HGWO-PSO"],
 ["✓ accuracy, precision, recall, F1, mAP@0.5, mAP@0.5:0.95, confusion matrix, AP per kelas",
  "✓ accuracy, F1, sensitivity, specificity, PPV, NPV, confusion matrix, uji statistik",
  "✓ accuracy, precision, recall, F1, AUC, confusion matrix",
  "✓ accuracy, precision, recall, F1, 95% CI bootstrap, feature importance"],
 ["✓ Impacted Mandibular Third Molar Dataset (Mendeley 10.17632/ckt876jzr6.1), 5.796 OPG",
  "✓ CONTACT dataset, 1.478 M3M dari 1.010 pasien, CBCT sebagai gold standard",
  "✓ Arsip institusional, 1.100 OPG berlabel + 711 OPG negatif",
  "✓ Arsip Dental Imaging Center Ankara, 353 OPG, 2.137 restorasi"],
 ["✓ Publik — Mendeley Data, CC BY 4.0",
  "✓ Publik — Kaggle CONTACT",
  "✗ Privat — tersedia atas permintaan penulis",
  "✗ Privat — akses melalui izin etik institusi"],
 ["✓ International Dental Journal (Elsevier), Q1",
  "✓ Scientific Reports (Nature Portfolio), Q1",
  "✓ Journal of Oral Medicine and Oral Surgery, open access",
  "✓ Healthcare (MDPI), open access"],
 ["✓ 10.1016/j.identj.2026.109430",
  "✓ 10.1038/s41598-024-82915-5",
  "✓ 10.1051/mbcb/2025008",
  "✓ 10.3390/healthcare13222904"],
]
for i, vals in enumerate(A, start=1):
    row(T[2], i, vals, start_col=2, size=7.5)

# ------------------------------------------------------------------ T3 identitas artikel
row(T[3], 1, [
 "Dual Framework for Classification and Detection of Third Molar Impaction in Panoramic Radiographs",
 "Panoramic radiographic features for machine learning based detection of mandibular third molar root and inferior alveolar canal contact",
 "Fully automated deep learning framework for detection and classification of impacted mandibular third molars in panoramic radiographs",
 "Decision-Support for Restorative Dentistry: Hybrid Optimization Enhances Detection on Panoramic Radiographs"])
row(T[3], 2, [
 "Khurshid Z. dkk. (2026) — King Faisal University, Arab Saudi",
 "Ulusoy A.C. dkk. (2025) — Ege University & Dokuz Eylül University",
 "Kandagal Veerabhadrappa S. dkk. (2025) — SEGi University & APU",
 "Ateş G. dkk. (2025) — Yıldırım Beyazıt, Gazi, Lokman Hekim University"])
row(T[3], 3, [
 "International Dental Journal 76(2):109430 — Q1 (Elsevier)",
 "Scientific Reports 15:4178 — Q1 (Nature Portfolio)",
 "Journal of Oral Medicine and Oral Surgery 31(1):7 — open access",
 "Healthcare 13(22):2904 — Q1–Q2, open access (MDPI)"])
row(T[3], 4, [
 "10.1016/j.identj.2026.109430 (terbit, open access)",
 "10.1038/s41598-024-82915-5 (terbit, open access)",
 "10.1051/mbcb/2025008 (terbit, open access)",
 "10.3390/healthcare13222904 (terbit, open access)"])
row(T[3], 5, [
 "Menilai posisi impaksi molar ketiga mandibula: deteksi otomatis gigi dan klasifikasi 6 kategori sudut impaksi pada OPG.",
 "Mendeteksi kontak akar molar ketiga mandibula dengan kanal alveolar inferior (M3M–IAC) yang meningkatkan risiko cedera saraf saat odontektomi.",
 "Mendeteksi dan mengklasifikasi posisi impaksi molar ketiga ke 4 kelas Winter secara otomatis pada OPG.",
 "Membantu pemilihan tindakan restorasi gigi dengan mengklasifikasi 5 jenis restorasi pada OPG."])
row(T[3], 6, [
 "Dataset publik 5.796 OPG beranotasi ganda (κ=0,92) dan pembandingan YOLOv10 vs YOLOv11n untuk deteksi dan klasifikasi sudut impaksi.",
 "Dataset publik pertama dengan anotasi semantik kontak M3M–IAC, plus bukti bahwa 6 fitur radiologis terukur mengalahkan 7 CNN dan 3 radiolog.",
 "Kerangka dua tahap VGG16 (deteksi) + ResNet50 (klasifikasi Winter 4 kelas) tanpa fitur manual, akurasi deteksi 93,51%.",
 "Seleksi fitur GLCM dengan optimasi hybrid HGWO-PSO yang mengalahkan CNN kustom pada dataset kecil."])

# ------------------------------------------------------------------ T4 data & praproses
row(T[4], 1, [
 "Impacted Mandibular Third Molar Dataset, Mendeley Data 10.17632/ckt876jzr6.1 — publik, CC BY 4.0",
 "CONTACT dataset (Kaggle) + kode ekstraksi fitur — publik, lisensi artikel CC BY-NC-ND 4.0",
 "Arsip institusional tanpa nama formal — privat, tersedia atas permintaan penulis",
 "Arsip Dental Imaging Center Ankara tanpa nama formal — privat, akses via izin etik"])
row(T[4], 2, [
 "OPG 2D grayscale; dimensi distandarkan; jumlah piksel asli tidak dilaporkan",
 "OPG 2D 2.700×1.249 px, grayscale, 4 perangkat radiografi berbeda",
 "OPG 2D dari DICOM 2.943×1.435 px, di-resize 224×224, satu institusi",
 "OPG 2D 2.775×1.504 px -> 1.700×880 -> 224×224, satu perangkat"])
row(T[4], 3, [
 "5.796 citra, 6 kelas: Disto 1.470, Mesio 1.100, Vertical 939, Horizontal 817, Inverted 736, Buccolingual 734 — tidak seimbang",
 "1.478 M3M dari 1.010 pasien: kontak 1.100 vs tanpa kontak 378 — tidak seimbang",
 "1.100 OPG berlabel (1.200 gigi) + 711 negatif; Vertical 368, Mesio 328, Horizontal 295, Disto 209 — tidak seimbang",
 "353 OPG, 2.137 restorasi, 5 kelas — tidak seimbang"])
row(T[4], 4, [
 "Bounding box di CVAT oleh mahasiswa/intern, diverifikasi 2 spesialis; Cohen κ=0,92",
 "Anotasi semantik poligon oleh ahli radiologi mulut; kesepakatan antar-pembaca κ=0,43",
 "LabelImg oleh 2 radiolog >10 tahun; nilai kesepakatan tidak dilaporkan",
 "Anotasi region oleh dokter gigi terkalibrasi; nilai kesepakatan tidak dilaporkan"])
row(T[4], 5, [
 "Standarisasi dimensi, kecerahan, kontras; augmentasi geometrik + fotometrik + StyleGAN2-ADA",
 "Penskalaan, crop ROI, k-means 4 klaster, morfologi, skeletonization, ambang darkening 0,1/0,2/0,35",
 "Redaksi teks (OCR), deteksi tepi Sobel, resize 224×224",
 "Crop, ImageEnhance, histogram equalization + CLAHE (clip 2,0; grid 8×8), smoothing, z-score"])
row(T[4], 6, [
 "Tidak ada crop manual; lokalisasi diserahkan ke YOLO, klasifikasi memakai ROI hasil deteksi",
 "Segmen semantik gigi dan kanal (k-means 4 klaster + morfologi) sebagai dasar fitur",
 "ROI dari bounding box YOLOv7, di-resize 224×224",
 "Tanpa ROI anatomi; fitur GLCM dihitung pada region hasil crop"])
row(T[4], 7, [
 "Geometrik + fotometrik + StyleGAN2-ADA hingga 2.000 citra/kelas",
 "Tidak memakai augmentasi",
 "Rotasi 45°, shift 10%, shear, zoom, flip, perubahan kecerahan",
 "Flip, rotasi ±10°, perubahan kecerahan ±15%"])
row(T[4], 8, [
 "Train 1.796 / validasi 2.000 / uji 2.000; pembagian per citra, pemisahan per pasien tidak dilaporkan",
 "Monte Carlo 30 ulangan, skema 50/50 dan 80/20; pembagian per citra",
 "70/20/10 sekali; pemisahan per pasien tidak dilaporkan",
 "80/20 per pasien + 5-fold cross-validation (stratified)"])

# ------------------------------------------------------------------ T5 ekstraksi fitur
row(T[5], 1, [
 "Deep features: peta fitur YOLO (deteksi) dan embedding ResNet50/InceptionNetV3 (klasifikasi)",
 "6 fitur radiologis terukur: darkening akar, interupsi garis putih IAC, defleksi IAC, penyempitan IAC, defleksi akar, penyempitan akar",
 "Tidak ada metode manual; representasi dipelajari lapisan konvolusi VGG16/ResNet50",
 "GLCM (gray-level co-occurrence matrix): contrast, correlation, energy, homogeneity, entropy"])
row(T[5], 2, [
 "Deep feature (pembelajaran representasi)",
 "Campuran intensitas/tekstur, bentuk, dan geometri",
 "Deep feature (end-to-end)",
 "Tekstur statistik orde kedua (GLCM)"])
row(T[5], 3, [
 "Bobot ImageNet; ukuran input klasifikasi tidak seragam; normalisasi mengikuti backbone",
 "Ambang darkening 0,1/0,2/0,35; toleransi kemiringan dan ambang penyempitan 20%; k-means 4 klaster",
 "Resolusi 224×224; normalisasi implisit pada arsitektur",
 "GLCM simetris, jarak d=1, 64 level keabuan, orientasi 0°/45°/90°/135°"])
row(T[5], 4, [
 "Embedding berdimensi tinggi (ratusan sampai ribuan); dimensi tepat tidak dirinci",
 "6 dimensi (fitur ke-7 'bifid apex' belum diimplementasikan)",
 "Tidak berlaku (fitur implisit); keluaran softmax 4 kelas",
 "20 fitur (5 deskriptor × 4 orientasi), direduksi HGWO-PSO sekitar 45%"])
row(T[5], 5, [
 "Tidak ada seleksi fitur; seleksi pada tingkat classifier (10 classifier diuji)",
 "Uji chi-square (fscchi2): interupsi garis IAC dan darkening akar paling prediktif",
 "Tidak ada seleksi fitur",
 "HGWO-PSO (populasi 10, 100 iterasi; fitness 0,9·akurasi + 0,1·(1−rasio fitur))"])
row(T[5], 6, [
 "Embedding CNN memberi akurasi tinggi tanpa rekayasa fitur manual",
 "Fitur mengikuti indikator radiografis baku sehingga dapat dihitung ulang dan dipertanggungjawabkan secara klinis",
 "Menghindari bias pemilihan fitur manual dan mengejar akurasi maksimum",
 "Fitur tekstur murah dan menjelaskan, seleksi menekan overfitting pada data kecil"])
row(T[5], 7, [
 "Kelebihan: akurasi klasifikasi tinggi (F1 96,10). Kelemahan: tanpa fitur terukur dan tanpa interpretabilitas; label 'handcrafted' pada artikel ini tidak tepat",
 "Kelebihan: specificity 81,92 dan F1 90,76 melampaui 7 CNN dan radiolog, fitur dapat diaudit. Kelemahan: anotasi manual berat, bergantung kualitas segmentasi, fitur ke-7 belum ada",
 "Kelebihan: akurasi deteksi 93,51 dan alur sederhana. Kelemahan: black box, butuh data besar, tanpa metrik per kelas",
 "Kelebihan: fitur jelas dan tahan data kecil. Kelemahan: berbasis region/global bukan ROI anatomi, akurasi mutlak 73,15"])

# ------------------------------------------------------------------ T6 model ML
row(T[6], 1, [
 "YOLOv10 dan YOLOv11n + MHSA (deteksi); ResNet50 dan InceptionNetV3 dengan 10 classifier klasik: Fine KNN, KNN, SVM linear/kubik, RF, DT, NB, GB, AdaBoost, NN",
 "ANN-MLP 6-35-1 (tansig); pembanding 2 CNN kustom, 7 CNN pretrained, dan kombinasi hybrid",
 "VGG16 (deteksi, sigmoid, ambang 0,25) dan ResNet50 (klasifikasi Winter 4 kelas); YOLOv7 pembanding",
 "SVM-RBF, KNN (k=5), Decision Tree, Random Forest (100 pohon), CNN kustom"])
row(T[6], 2, [
 "YOLO 100 epoch; Fine KNN k=1 jarak Euclidean; hyperparameter classifier lain tidak dirinci",
 "Goal 1e-3, laju belajar 0,01 adaptif, maksimum 65.000 epoch, ambang klasifikasi 0,65",
 "YOLOv7: lr 0,75, IoU 0,65, input 224; ResNet50: dense 1000/500, L2 0,01/0,03, dropout 40%/30%",
 "SVM C=10, γ=0,1; CNN: Adam 1e-4, batch 32, maksimum 50 epoch"])
row(T[6], 3, [
 "2 ekstraktor × 10 classifier = 20 kombinasi; 2 varian detektor",
 "3 skema fitur (fitur, citra, hybrid) × beberapa konfigurasi node ANN + 9 model DL",
 "6 arsitektur deteksi × 1 arsitektur klasifikasi",
 "4 classifier × (fitur penuh vs fitur hasil seleksi) × CNN pembanding"])
row(T[6], 4, [
 "Pembanding utama YOLOv10 dan InceptionNetV3; baseline antar-classifier klasik",
 "Pembanding kuat: 7 CNN pretrained dan 3 radiolog (76,65–82,40)",
 "Pembanding YOLOv7 dan 5 arsitektur deteksi lain",
 "Pembanding CNN kustom, KNN, DT, RF, serta GLCM tanpa seleksi"])
row(T[6], 5, [
 "Augmentasi + StyleGAN2-ADA menyeimbangkan tiap label hingga 2.000 citra",
 "ANN2 memakai data 50/50 (hasil lebih buruk); tanpa SMOTE; kasus sulit tetap dipertahankan",
 "Ambang sigmoid 0,25 + augmentasi; tanpa penyeimbangan eksplisit",
 "Stratified 5-fold; tanpa penyeimbangan eksplisit"])
row(T[6], 6, [
 "Google Colab A100 (YOLO) dan Kaggle P100 (fitur + klasifikasi)",
 "MATLAB R2023a; GPU tidak dirinci; 30 ulangan Monte Carlo",
 "Tidak dilaporkan",
 "GPU RTX A4000; inferensi SVM 1,6 s/citra, CNN 0,9 s/citra; memori 2,3 GB"])

# ------------------------------------------------------------------ T7 evaluasi & hasil
row(T[7], 1, [
 "Accuracy, precision, recall, F1, mAP@0.5, mAP@0.5:0.95, per-class AP, confusion matrix",
 "Accuracy, F1, sensitivity, specificity, PPV, NPV, confusion matrix, uji statistik",
 "Accuracy, precision, recall, F1, AUC, confusion matrix",
 "Accuracy, precision, recall, F1, 95% CI bootstrap, feature importance"])
row(T[7], 2, [
 "Deteksi YOLOv11n mAP@0.5 88,90 (YOLOv10 87,60); klasifikasi Fine KNN + ResNet50 accuracy 97,56, F1 96,10",
 "ANN 6-35-1: accuracy 85,45, F1 90,76, SE 86,36, SP 81,92; DL terbaik 80,50; radiolog 76,65–82,40",
 "Deteksi VGG16: accuracy 93,51, P 94,64, R 89,47, F1 91,97; klasifikasi ResNet50: accuracy 92,17, AUC 98,28, F1 91,7",
 "SVM + GLCM + HGWO-PSO: accuracy 73,15 (95% CI 71,1–75,2), macro-F1 0,728; CNN 68,52 (p<0,05)"])
row(T[7], 3, [
 "Mesioangular vs Horizontal (ambiguitas proyeksi 2D); presisi terendah pada Horizontal dan Mesioangular",
 "Kontak semu (false positive contact); specificity ANN tanpa penyeimbangan turun sampai 44,91",
 "Tidak dianalisis; kelas Buccolingual dan Inverted justru dikecualikan",
 "Restorasi mirip (filling vs crown vs bridge); citra dengan artefak logam"])
row(T[7], 4, [
 "Tidak ada — angka 97,56 dari dataset yang sama",
 "Tidak ada — satu negara, 4 perangkat; generalisasi dibatasi",
 "Tidak ada",
 "Tidak ada — satu pusat, 353 citra"])
row(T[7], 5, [
 "Tidak ada Grad-CAM/saliency; hanya confusion matrix",
 "Ada: peringkat fitur dari chi-square + visualisasi ROI dan fitur",
 "Tidak ada",
 "Ada: bobot fitur hasil HGWO-PSO + confusion matrix"])
row(T[7], 6, [
 "Ambiguitas proyeksi 2D, presisi kelas sudut moderat, butuh studi multisenter",
 "Anotasi manual berat dan mahal; fitur bergantung segmentasi; sebagian fitur tidak rutin dipakai radiolog",
 "Dataset moderat; kelas Buccolingual/Inverted dikecualikan; M2 tidak dianotasi; sistem bukan pengganti dokter",
 "Data kecil dan satu pusat; fitur global; klasifikasi hanya tingkat citra"])

# ------------------------------------------------------------------ T8 sintesis
for i, vals in zip(range(1, 5), [
 ["Publik 5.796 OPG, 6 kelas sudut, κ=0,92", "Standarisasi + augmentasi + StyleGAN2-ADA; ROI dari detektor",
  "Deep (feature map YOLO, embedding ResNet50/Inception)", "YOLOv11n + Fine KNN/ResNet50",
  "mAP@0.5 88,90; accuracy 97,56; F1 96,10", "Data besar, label ganda, dua tahap lengkap",
  "Tanpa interpretabilitas; tanpa uji eksternal; klaim 'handcrafted' keliru"],
 ["Publik 1.478 M3M/1.010 pasien; CBCT gold standard", "Segmentasi semantik + k-means + skeletonization; tanpa augmentasi",
  "6 fitur radiologis terukur", "ANN 6-35-1; pembanding 7 CNN + radiolog",
  "Accuracy 85,45; F1 90,76; SP 81,92", "Fitur terbukti bersaing dengan CNN dan manusia; kode tersedia",
  "Anotasi berat; fitur ke-7 belum ada; satu negara"],
 ["Privat 1.100 OPG/1.200 gigi + 711 negatif", "OCR redaksi teks, Sobel, resize; augmentasi geometrik",
  "Deep end-to-end (VGG16, ResNet50)", "VGG16 + ResNet50; YOLOv7 pembanding",
  "Deteksi 93,51; klasifikasi 92,17; AUC 98,28", "Winter 4 kelas; akurasi tinggi; alur sederhana",
  "Privat; tanpa κ; tanpa metrik per kelas; tanpa interpretabilitas"],
 ["Privat 353 OPG/2.137 restorasi; 5 kelas", "Crop, HE/CLAHE, z-score; augmentasi ringan",
  "GLCM 20 fitur + seleksi HGWO-PSO", "SVM-RBF; pembanding CNN, KNN, DT, RF",
  "Accuracy 73,15; macro-F1 0,728; CNN 68,52", "Fitur jelas, seleksi terukur, tahan data kecil",
  "Objek bukan M3M; fitur global; satu pusat; akurasi mutlak rendah"],
]):
    row(T[8], i, vals, start_col=1, size=7.5)

# ------------------------------------------------------------------ T9 keputusan
D = [
 ("Masalah klinis: penilaian posisi impaksi molar ketiga mandibula dan risiko kontak akar dengan kanal alveolar inferior "
  "pada radiograf panoramik masih manual sehingga hasilnya bervariasi antar-pembaca. Pengguna: dokter gigi umum di puskesmas/klinik "
  "dan mahasiswa kedokteran gigi sebagai alat bantu edukasi. A1 dan A3 menunjukkan posisi impaksi (Winter) dapat diklasifikasi otomatis; "
  "A2 menunjukkan risiko kontak M3M–IAC dapat dideteksi dari fitur radiografis.",
  "A1, A2, A3"),
 ("ExAn-MTM (973 citra, anotasi YOLO, 2 kelas i-MTM/e-MTM) untuk Tahap 1 deteksi ROI karena sudah diunduh dan diaudit: 0 citra rusak, "
  "0 label tidak valid, 1.784 objek. Untuk Tahap 2 klasifikasi Winter 4 kelas dipakai dataset Khurshid 5.796 OPG (A1, publik, CC BY 4.0) "
  "yang sudah memuat Mesio 1.100, Disto 1.470, Horizontal 817, Vertical 939. Dataset m-TM hanya untuk uji eksternal karena ExAn-MTM "
  "terbukti subset-nya (973 citra identik MD5) sehingga tidak boleh dipakai sebagai train dan test sekaligus.",
  "A1; audit lokal"),
 ("Urutan: (1) redaksi identitas pasien (OCR + masking) mengikuti A3; (2) resize ke 1.024 px untuk deteksi; (3) CLAHE clip 2,0 grid 8×8 "
  "dan normalisasi [0,1] mengikuti A4; (4) denoise median 3×3. Praproses ringan dipilih karena A4 membuktikan CLAHE + z-score menaikkan "
  "akurasi, sedangkan A2 menunjukkan praproses berat tidak wajib bila fitur sudah terukur.",
  "A3, A4, A2"),
 ("Dua tingkat. Tingkat pertama deteksi objek: YOLOv8n/YOLOv11n menghasilkan bounding box M3 dan M2 (A1: mAP@0.5 88,90; A3: akurasi deteksi 93,51). "
  "Tingkat kedua: crop ROI dari bbox M2+M3, resize 224×224 untuk jalur deep, dan ROI penuh untuk jalur fitur. Segmentasi semantik seperti A2 "
  "tidak dipakai karena anotasi poligon manual terlalu mahal untuk 973 citra.",
  "A1, A3, A2"),
 ("Utama: fitur handcrafted — sudut Winter M3 terhadap M2, rasio geometri (jarak servikal, kedalaman relatif, rasio area bbox), "
  "GLCM 20 fitur (contrast, correlation, energy, homogeneity, entropy; d=1; 0/45/90/135°) seperti A4, plus intensitas akar untuk darkening "
  "seperti A2. Pembanding: embedding deep ResNet50/InceptionNetV3 seperti A1 dan A3. A2 membuktikan fitur terukur dapat mengalahkan CNN "
  "(85,45 vs 80,50), sehingga jalur handcrafted dipilih sebagai utama.",
  "A2, A4 (utama); A1, A3 (pembanding)"),
 ("Utama: SVM-RBF (C=10, γ=0,1) dan Random Forest, mengikuti A4 yang menunjukkan SVM terbaik pada fitur tekstur dan tahan data kecil. "
  "Pembanding: ANN-MLP 6-35-1 seperti A2 dan Fine KNN k=1 seperti A1. Ketiga kandidat murah secara komputasi dan dapat dijalankan di Colab.",
  "A4, A2, A1"),
 ("Split terkunci per citra: train 70%, validasi 15%, test 15%, dengan cek duplikasi MD5/dHash sebelum split untuk mencegah kebocoran "
  "(ExAn-MTM terbukti subset m-TM). Uji eksternal memakai 344 citra unik m-TM. Ketidakseimbangan ditangani dengan class weight dan augmentasi "
  "ringan; SMOTE tidak dipakai karena fitur berdimensi rendah dan kelas minoritas sedikit — berbeda dari A1 yang memakai StyleGAN2-ADA pada data besar.",
  "Audit lokal; A1"),
 ("Metrik utama: macro-F1 dan F1 per kelas, karena kelas tidak seimbang dan kesalahan antar-kelas Winter (mis. mesioangular vs horizontal) "
  "berisiko klinis berbeda. Dilengkapi accuracy, confusion matrix, dan 95% CI bootstrap seperti A4. Untuk Tahap 1 dipakai mAP@0.5 dan "
  "mAP@0.5:0.95 seperti A1. Sensitivity/specificity dilaporkan bila fokus bergeser ke deteksi kontak akar seperti A2.",
  "A4, A1, A2"),
 ("Risiko: (1) kebocoran data ExAn-MTM ⊂ m-TM -> split terkunci + cek hash; (2) label Winter tidak tersedia lokal -> pakai dataset Khurshid "
  "atau anotasi manual 300–500 citra oleh 2 anotator dengan κ≥0,80; (3) ambiguitas proyeksi 2D (A1, A3) -> laporkan confusion matrix dan "
  "batasi klaim; (4) lisensi NC-ND/NC-SA -> tidak mendistribusikan ulang data; (5) kuota Colab -> input 1.024 px, batch 8, model n-series.",
  "Audit lokal; A1, A3"),
 ("Batasan: sistem adalah prototipe penelitian dan alat bantu edukasi, bukan alat diagnosis medis; keputusan terapi tetap pada dokter. "
  "Tidak ada ID pasien pada dataset sehingga split per citra tidak menjamin pemisahan per pasien. Etika: radiograf berasal dari sumber publik "
  "teranonimisasi, tidak ada data pasien yang diunggah ulang, dataset tidak didistribusikan ulang karena lisensi, dan keluaran sistem selalu "
  "disertai confidence score yang harus diverifikasi manusia.",
  "Audit lokal; A1–A4"),
 ("Pembeda: artikel A1/A3 hanya melaporkan angka agregat tanpa interpretabilitas, sedangkan A2/A4 menjelaskan fitur tetapi tidak meneliti skema "
  "Winter 4 kelas. Proyek ini menggabungkan ROI otomatis (A1/A3) dengan keputusan berbasis fitur terukur (A2/A4), melaporkan F1 per kelas + "
  "95% CI, dan menyiapkan uji eksternal pada 344 citra unik — hal yang tidak dilakukan satu pun dari keempat artikel.",
  "A1–A4; audit lokal"),
]
for i, (ans, ref) in enumerate(D, start=1):
    cells = T[9].rows[i].cells
    fill(cells[2], ans, size=8)
    fill(cells[3], ref, size=8)

# ------------------------------------------------------------------ T10 dataset
DS = [
 ("ExAn-MTM (Expert Annotated Mandibular Third Molar), Mendeley Data — arsip lokal Datasets/Expert Annotated Mandibular Third Molar/ "
  "(train 875 + valid 98 citra). Dataset pembanding: m-TM; rencana Tahap 2: 10.17632/ckt876jzr6.1", ),
 ("ExAn-MTM CC BY-NC-ND 4.0 (non-komersial, tanpa distribusi karya turunan); m-TM CC BY-NC-SA 4.0; Khurshid CC BY 4.0. Wajib sitasi.", ),
 ("2 kelas: i-MTM 1.097 objek (61,5%), e-MTM 687 objek (38,5%); total 1.784 objek pada 973 citra. Sebagian citra memuat lebih dari satu gigi "
  "sehingga jumlah citra per kelas tidak dijumlahkan.", ),
 ("144,2 MB, 973 file JPG grayscale 1.991×1.127 px (resolusi seragam); arsip asli RAR 192 MB.", ),
 ("Tidak tersedia ID pasien. Split dilakukan per citra dengan cek duplikasi MD5/dHash; keterbatasan ini dinyatakan pada laporan.", ),
 ("Subset: 973 citra dipakai apa adanya (Tahap 1); untuk klasifikasi Winter 4 kelas dipakai dataset Khurshid 5.796 citra atau subset 300–500 citra "
  "hasil anotasi manual. Input deteksi 1.024 px, batch 8, model n-series agar muat GPU T4.", ),
 ("Sudah diunduh dan diaudit. Bukti: Analysis/06_Audit_Dataset.py + run.log (rc=0) + grafik distribusi kelas (Lampiran 2 dokumen studi literatur); "
  "tangkapan layar Colab dilampirkan terpisah setelah notebook dijalankan.", ),
]
for i, (v,) in enumerate(DS, start=1):
    fill(T[10].rows[i].cells[2], v, size=8)

# ------------------------------------------------------------------ T11 diagram
cell = T[11].rows[0].cells[0]
p = cell.paragraphs[0]
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run().add_picture(DIAG, width=Cm(15.5))

# ------------------------------------------------------------------ T13 pustaka
REFS = [
 "Z. Khurshid, M. H. Alsleem, F. A. Aljubairah, H. A. Alghafli, A. O. Alasafirah, B. A. Alibrahim, A. A. Alshamrani, dan A. N. Alsuhaymi, "
 "\u201cDual framework for classification and detection of third molar impaction in panoramic radiographs,\u201d International Dental Journal, "
 "vol. 76, no. 2, art. 109430, 2026, doi: 10.1016/j.identj.2026.109430.",
 "A. C. Ulusoy, T. Toprak, M. A. Selver, P. Güneri, dan B. İlhan, \u201cPanoramic radiographic features for machine learning based detection of mandibular "
 "third molar root and inferior alveolar canal contact,\u201d Scientific Reports, vol. 15, art. 4178, 2025, doi: 10.1038/s41598-024-82915-5.",
 "S. Kandagal Veerabhadrappa, S. Vengusamy, S. Padarha, K. Iyer, dan S. Yadav, \u201cFully automated deep learning framework for detection and classification "
 "of impacted mandibular third molars in panoramic radiographs,\u201d Journal of Oral Medicine and Oral Surgery, vol. 31, no. 1, art. 7, 2025, "
 "doi: 10.1051/mbcb/2025008.",
 "G. Ateş, F. Türk, E. T. Akçın, dan M. Güngör, \u201cDecision-support for restorative dentistry: Hybrid optimization enhances detection on panoramic "
 "radiographs,\u201d Healthcare, vol. 13, no. 22, art. 2904, 2025, doi: 10.3390/healthcare13222904.",
 "Z. Khurshid dkk., \u201cImpacted Mandibular Third Molar Dataset,\u201d Mendeley Data, V1, 2026, doi: 10.17632/ckt876jzr6.1.",
]
for i, r in enumerate(REFS, start=1):
    fill(T[13].rows[i].cells[1], r, size=8.5)

# ------------------------------------------------------------------ T14 status luaran
for i, st in zip(range(1, 8), ["✓ Selesai", "✓ Selesai", "Sebagian (angka terisi; tangkapan layar Colab menyusul)", "✓ Selesai", "✓ Selesai", "✓ Selesai", "✓ Selesai"]):
    fill(T[14].rows[i].cells[2], st, size=8.5)

# ------------------------------------------------------------------ T1 subtopik kelompok
c = T[1].rows[10].cells
fill(c[1], "Deteksi dan klasifikasi posisi impaksi molar ketiga mandibula (Winter) pada radiograf panoramik", size=9)
fill(c[2], "Radiograf panoramik dental (OPG), grayscale 2D", size=9)
fill(c[3], "ExAn-MTM (Mendeley Data); pembanding: m-TM; klasifikasi Winter: dataset Khurshid dkk. 10.17632/ckt876jzr6.1", size=9)
fill(c[4], "Alat bantu edukasi dan prototipe penelitian bagi dokter gigi serta mahasiswa dalam menilai posisi impaksi M3; bukan alat diagnosis medis", size=9)

# ------------------------------------------------------------------ T12 narasi
NARASI = [
 "Pola metodologis empat artikel. Keempat artikel dapat dipetakan ke dua kubu. Kubu pertama menyerahkan seluruh proses "
 "pada jaringan dalam: A1 memakai YOLO untuk menemukan gigi lalu ResNet50/InceptionNetV3 untuk mengklasifikasi, dan A3 "
 "melatih VGG16 sebagai detektor serta ResNet50 sebagai pengklasifikasi Winter. Kubu kedua mengekstraksi fitur yang dapat "
 "dihitung ulang: A2 merumuskan enam indikator radiografis kontak M3M–IAC, sedangkan A4 menghitung matriks kookurensi "
 "keabuan (GLCM) lalu menyeleksinya dengan optimasi hybrid. Perbedaan ini penting bagi proyek PCVK karena kompetensi mata "
 "kuliah berada pada pengolahan citra klasik — praproses, segmentasi, ekstraksi ciri, seleksi ciri, dan pengklasifikasi — "
 "bukan semata pada penyetelan arsitektur CNN.",
 "Bukti bahwa fitur handcrafted masih kompetitif. A2 memberi bukti paling kuat: dengan hanya enam fitur, ANN 6-35-1 mencapai "
 "accuracy 85,45%, F1 90,76%, sensitivity 86,36%, dan specificity 81,92%, mengungguli tujuh CNN pretrained (accuracy terbaik "
 "80,50%) dan tiga radiolog (76,65–82,40%). A4 menguatkan pola serupa pada skala kecil: GLCM 20 fitur yang diseleksi HGWO-PSO "
 "mencapai 73,15% berbanding 68,52% pada CNN kustom, dengan selisih signifikan (p<0,05). Sebaliknya, A1 dan A3 memperlihatkan "
 "bahwa deep learning memang unggul ketika data besar dan label rapi tersedia: A1 mencapai F1 96,10% pada 5.796 citra dengan "
 "κ=0,92, dan A3 mencapai accuracy 92,17% pada 1.200 gigi. Kesimpulannya bukan 'CNN buruk', melainkan bahwa nilai deep learning "
 "bergantung pada volume data dan kualitas label — dua hal yang justru menjadi batas proyek ini.",
 "Pelajaran dari sisi data. Audit lokal menunjukkan dataset yang tersedia untuk proyek hanya 973 citra beranotasi biner "
 "(i-MTM/e-MTM). Pada volume itu, mengejar arsitektur end-to-end seperti A1 berisiko overfitting dan sulit dipertanggungjawabkan. "
 "A2 dan A4 menunjukkan jalur yang lebih hemat: fitur sedikit, terukur, dan diseleksi. Audit juga menemukan dua hal yang tidak "
 "boleh diabaikan. Pertama, ExAn-MTM adalah subset m-TM — 973 dari 973 citra identik secara MD5 — sehingga memakai keduanya "
 "sebagai train dan test akan menghasilkan kebocoran 100% dan angka evaluasi palsu. Kedua, tidak ada ID pasien pada kedua "
 "dataset, sehingga split hanya dapat dilakukan per citra; ini harus dinyatakan sebagai limitasi, bukan disembunyikan.",
 "Kesenjangan yang diisi proyek. Tiga kesenjangan terlihat dari sintesis. (i) A1 dan A3 melaporkan angka tinggi tetapi tanpa "
 "interpretabilitas; A2 dan A4 menjelaskan fitur tetapi tidak meneliti skema Winter 4 kelas. Proyek ini menggabungkan keduanya: "
 "ROI ditemukan otomatis (seperti A1/A3) lalu diputuskan dengan fitur terukur (seperti A2/A4). (ii) A3 tidak melaporkan hasil "
 "per kelas dan tidak melaporkan kesepakatan antar-anotator, sehingga klaim akurasinya tidak dapat diperiksa; proyek ini akan "
 "melaporkan F1 per kelas, confusion matrix, dan interval kepercayaan bootstrap. (iii) Tidak satu pun artikel melakukan validasi "
 "eksternal; proyek ini menyiapkan uji eksternal dari sisa unik m-TM (344 citra) agar generalisasi diuji, bukan diasumsikan.",
 "Konsekuensi rancangan. Berdasarkan keputusan pada Tabel 9, pipeline dibangun dua tahap. Tahap 1: deteksi bbox M3 dan M2 dengan "
 "YOLOv8n/YOLOv11n pada input 1.024 px, dengan augmentasi ringan dan mosaic dimatikan pada 10 epoch terakhir; target realistis "
 "adalah mAP@0.5 pada kisaran 80–89% mengacu A1 dan A3, bukan menyalin angka 97,56% A1 yang dihasilkan dari 5.796 citra. "
 "Tahap 2: dua jalur fitur pada ROI hasil deteksi — jalur handcrafted (sudut Winter, rasio geometri, GLCM, intensitas akar) dengan "
 "seleksi chi-square/ANOVA dan pembanding HGWO-PSO, serta jalur deep (embedding ResNet50) sebagai pembanding setara. Pengklasifikasi "
 "utama SVM-RBF dan Random Forest, dengan ANN-MLP sebagai pembanding mengikuti A2. Metrik utama accuracy, macro-F1, F1 per kelas, "
 "confusion matrix, dan 95% CI; untuk deteksi mAP@0.5 dan mAP@0.5:0.95.",
 "Batas klaim dan etika. Semua angka pada laporan akhir akan disajikan sebagai hasil prototipe pada dataset terbatas, bukan sebagai "
 "klaim klinis. Radiograf berasal dari sumber publik teranonimisasi dan tidak akan didistribusikan ulang karena lisensi CC BY-NC-ND. "
 "Sistem tidak digunakan untuk keputusan terapi; keluarannya adalah kelas posisi, confidence score, dan bounding box yang harus "
 "diverifikasi pembaca manusia. Dengan pembatasan ini, proyek tetap memenuhi tuntutan akademik — metode dapat direplikasi, hasil "
 "dapat diaudit, dan klaim sepadan dengan bukti.",
]
ncell = T[12].rows[0].cells[0]
np_ = ncell.paragraphs[0]
for r in list(np_.runs):
    r._element.getparent().remove(r._element)
for i, para in enumerate(NARASI):
    p = np_ if i == 0 else ncell.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(4)
    p.add_run(para).font.size = Pt(8.5)

d.save(OUT)
print("saved", OUT)