"""Bangun dokumen studi literatur PCVK (terisi) dari data audit + 4 artikel terverifikasi."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

BUILD = r"C:\Kuliah\Tingkat 3\PCVK\Project\Analysis\build"
OUT = r"C:\Kuliah\Tingkat 3\PCVK\Project\Analysis\Studi_Literatur_PCVK_Terisi.docx"

# ---------------------------------------------------------------- lampiran grafik
def chart():
    kelas = ["i-MTM (impacted)", "e-MTM (erupted)"]
    obj = [1097, 687]
    fig, ax = plt.subplots(figsize=(5.2, 2.4), dpi=200)
    bars = ax.bar(kelas, obj, width=0.5, color=["#2563eb", "#93c5fd"])
    tot = sum(obj)
    for b, v in zip(bars, obj):
        ax.text(b.get_x() + b.get_width() / 2, v + 30, f"{v} ({v/tot:.1%})",
                ha="center", fontsize=8)
    ax.set_ylabel("jumlah objek", fontsize=8); ax.set_ylim(0, 1300)
    ax.tick_params(labelsize=8)
    ax.set_title("ExAn-MTM: 973 citra, 1.784 objek (hasil audit lokal)", fontsize=8)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    pth = BUILD + r"\lampiran_distribusi.png"
    fig.savefig(pth, bbox_inches="tight", facecolor="white")
    return pth


CHART = chart()

doc = Document()
sec = doc.sections[0]
sec.orientation = WD_ORIENT.LANDSCAPE
sec.page_width, sec.page_height = Cm(29.7), Cm(21.0)
for m in ("left_margin", "right_margin"):
    setattr(sec, m, Cm(1.6))
sec.top_margin = Cm(1.5); sec.bottom_margin = Cm(1.5)

st = doc.styles["Normal"]
st.font.name = "Calibri"; st.font.size = Pt(9)
st.paragraph_format.space_after = Pt(3)
st.paragraph_format.line_spacing = 1.05


def h(text, lvl=1):
    p = doc.add_heading(text, level=lvl)
    p.paragraph_format.space_before = Pt(8 if lvl == 1 else 6)
    p.paragraph_format.space_after = Pt(3)
    for r in p.runs:
        r.font.name = "Calibri"
        r.font.size = Pt(12 if lvl == 1 else 10)
        r.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)
    return p


def para(text, italic=False, size=9, align=None, space=3):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.italic = italic; r.font.size = Pt(size)
    p.paragraph_format.space_after = Pt(space)
    if align == "c":
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return p


def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    el = OxmlElement("w:shd")
    el.set(qn("w:val"), "clear"); el.set(qn("w:fill"), hexcolor)
    tcPr.append(el)


def repeat_header(row):
    trPr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader"); el.set(qn("w:val"), "true")
    trPr.append(el)


def fixed_layout(t, widths):
    """Paksa lebar kolom benar-benar dipakai Word/LibreOffice (tblLayout fixed + gridCol)."""
    tblPr = t._tbl.tblPr
    for tag in ("w:tblLayout", "w:tblW"):
        for el in tblPr.findall(qn(tag)):
            tblPr.remove(el)
    lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed")
    tblPr.append(lay)
    tw = OxmlElement("w:tblW")
    tw.set(qn("w:type"), "dxa"); tw.set(qn("w:w"), str(int(sum(widths) * 567)))
    tblPr.append(tw)
    grid = t._tbl.find(qn("w:tblGrid"))
    if grid is not None:
        t._tbl.remove(grid)
    grid = OxmlElement("w:tblGrid")
    for w in widths:
        gc = OxmlElement("w:gridCol"); gc.set(qn("w:w"), str(int(w * 567)))
        grid.append(gc)
    t._tbl.insert(list(t._tbl).index(tblPr) + 1, grid)
    for row in t.rows:
        trPr = row._tr.get_or_add_trPr()
        if trPr.find(qn("w:cantSplit")) is None:
            trPr.append(OxmlElement("w:cantSplit"))


def table(widths, header, rows, fs=7.4, hdr_fill="DCE6F1", bold_first_col=True):
    t = doc.add_table(rows=1, cols=len(widths))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    hdr = t.rows[0]
    repeat_header(hdr)
    for i, txt in enumerate(header):
        c = hdr.cells[i]
        c.text = ""
        p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(1)
        r = p.add_run(txt); r.bold = True; r.font.size = Pt(fs)
        shade(c, hdr_fill)
    for row in rows:
        cells = t.add_row().cells
        for i, txt in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.0
            r = p.add_run(str(txt))
            r.font.size = Pt(fs)
            if i == 0 and bold_first_col:
                r.bold = True
    for row in t.rows:
        for i, w in enumerate(widths):
            row.cells[i].width = Cm(w)
    fixed_layout(t, widths)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def caption(text):
    p = doc.add_paragraph()
    r = p.add_run(text); r.italic = True; r.font.size = Pt(8)
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(6)
    return p


A1, A2, A3, A4 = "A1", "A2", "A3", "A4"

# ---------------------------------------------------------------- judul
t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("STUDI LITERATUR DAN PERANCANGAN ARSITEKTUR\n"
              "KLASIFIKASI POSISI IMPAKSI MOLAR KETIGA MANDIBULA PADA RADIOGRAF PANORAMIK")
r.bold = True; r.font.size = Pt(15)
t.paragraph_format.space_after = Pt(2)
para("Mata Kuliah Pengolahan Citra dan Visi Komputer (PCVK) — Proyek Akhir\n"
     "Subtema: deteksi objek dan klasifikasi pada citra medis 2D (radiograf panoramik dental)",
     size=9, align="c")

table([2.4, 22.5], ["Item", "Keterangan"], [
    ["Anggota kelompok", "1) ........................................  (NIM ................)\n"
                          "2) ........................................  (NIM ................)\n"
                          "3) ........................................  (NIM ................)"],
    ["Dosen pengampu", "........................................................"],
    ["Tanggal", "9 November 2026"],
], fs=8.5)

# ---------------------------------------------------------------- bagian 2 no.2
h("1. Rumusan Masalah Klinis", 1)
para("Ekstraksi molar ketiga mandibula yang impaksi merupakan tindakan bedah mulut yang berisiko: "
     "posisi gigi terhadap molar kedua dan kanal alveolar inferior menentukan tingkat kesulitan, lama operasi, "
     "dan risiko cedera nervus alveolar inferior. Penilaian posisi saat ini dilakukan manual pada radiograf "
     "panoramik dengan mengukur sudut aksis gigi terhadap molar kedua (kriteria Winter), sehingga hasilnya "
     "bergantung pada pengalaman pembaca dan rentan variasi antar-pembaca. Masalah yang dirumuskan: "
     "dapatkah sistem visi komputer (a) menemukan region of interest molar ketiga secara otomatis dan "
     "(b) mengklasifikasikan posisi impaksinya ke dalam kelas mesioangular, distoangular, horizontal, dan "
     "vertical menggunakan fitur yang dapat dihitung ulang dan dijelaskan, dengan kinerja yang terukur "
     "secara jujur pada data uji yang tidak bocor? Sistem yang dibangun adalah prototipe penelitian dan "
     "alat bantu edukasi, bukan alat diagnosis medis.")

# ---------------------------------------------------------------- tabel A
h("2. Tabel A — Matriks Kelayakan Artikel", 1)
caption("Tanda ✓/✗ sesuai rubrik. Kriteria 4b dan 6b dinilai pada tingkat keempat artikel bersama-sama; "
        "catatan koreksi ditulis pada baris terkait.")

rowsA = [
 ["1", "Rentang tahun terbit 2021–2026", "✓ 2026", "✓ 2025", "✓ 2025", "✓ 2025"],
 ["2", "Modalitas citra medis sesuai subtopik",
  "✓ Radiograf panoramik (OPG) 2D",
  "✓ Radiograf panoramik (OPG) 2D",
  "✓ Radiograf panoramik (OPG) 2D",
  "✓ Radiograf panoramik (OPG) 2D — objek restorasi, bukan M3"],
 ["3", "Menerapkan metode ML/DL",
  "✓ YOLOv10 & YOLOv11n (deteksi) + ResNet50 & InceptionNetV3 sebagai ekstraktor + 10 classifier klasik",
  "✓ ANN-MLP 6-35-1, 2 CNN kustom, 7 CNN pretrained, dan kombinasinya (hybrid)",
  "✓ VGG16 & ResNet50 end-to-end (deteksi + klasifikasi); YOLOv7 pembanding",
  "✓ SVM-RBF, KNN, DT, RF, CNN kustom + optimasi hybrid HGWO-PSO"],
 ["4a", "Menjelaskan cara mengekstraksi fitur (handcrafted/deep)",
  "✓ Deep: feature map YOLO dan embedding 2048-D dari backbone ImageNet; arsitektur & sumber bobot disebut",
  "✓ 6 fitur radiologis dirumuskan eksplisit (rumus darkening, skeletonization, deteksi tepi) + kode tersedia",
  "✓ End-to-end: fitur dipelajari lapisan konvolusi; Sobel dan OCR hanya praproses, bukan fitur",
  "✓ GLCM 5 deskriptor × 4 orientasi, d=1, 64 level, simetris, langkah demi langkah"],
 ["4b", "Menggunakan fitur handcrafted (bukan hanya CNN end-to-end)",
  "✗ murni deep (fitur deep, bukan handcrafted) — artikel tetap menyebut 'handcrafted' untuk embedding, klaim ini keliru",
  "✓ 6 fitur terukur terkait kontak M3M–IAC",
  "✗ end-to-end tanpa fitur terukur",
  "✓ GLCM + seleksi fitur metaheuristik (HGWO-PSO)"],
 ["5", "Metrik evaluasi memadai (≥3)",
  "✓ accuracy, precision, recall, F1, mAP@0.5, mAP@0.5:0.95, confusion matrix, per-class AP",
  "✓ accuracy, F1, sensitivity, specificity, PPV, NPV, confusion matrix, uji statistik",
  "✓ accuracy, precision, recall, F1, AUC, confusion matrix",
  "✓ accuracy, precision, recall, F1, 95% CI bootstrap, confusion matrix, feature importance"],
 ["6a", "Dataset jelas (nama/sumber/jumlah)",
  "✓ 'Impacted Mandibular Third Molar Dataset', Mendeley Data 10.17632/ckt876jzr6.1, 5.796 OPG (1.796/2.000/2.000)",
  "✓ CONTACT dataset (Kaggle), 1.478 M3M dari 1.010 pasien, 4 perangkat radiografi, CBCT sebagai gold standard",
  "✓ Arsip institusional, 1.100 OPG berlabel + 711 OPG negatif; sumber & jumlah jelas (tanpa nama formal)",
  "✓ Arsip Dental Imaging Center Ankara, 353 OPG, 2.137 restorasi; sumber & jumlah jelas (tanpa nama formal)"],
 ["6b", "Dataset publik",
  "✓ Publik — Mendeley Data, CC BY 4.0",
  "✓ Publik — Kaggle CONTACT (lisensi artikel CC BY-NC-ND 4.0)",
  "✗ Privat — 'available from the corresponding author on reasonable request'",
  "✗ Privat — akses melalui izin etik institusi"],
 ["7", "Peer review / status publikasi",
  "✓ International Dental Journal (Elsevier), Q1",
  "✓ Scientific Reports (Nature Portfolio), Q1",
  "✓ Journal of Oral Medicine and Oral Surgery (JOMOS), open access",
  "✓ Healthcare (MDPI), Q1–Q2, open access"],
 ["8", "DOI",
  "✓ 10.1016/j.identj.2026.109430",
  "✓ 10.1038/s41598-024-82915-5",
  "✓ 10.1051/mbcb/2025008",
  "✓ 10.3390/healthcare13222904"],
 ["9", "Kesesuaian subtopik kelompok",
  "✓ Paling dekat: deteksi + klasifikasi M3 impaksi (6 kelas sudut) pada OPG",
  "✓ Sangat dekat: M3 impaksi & hubungan akar–kanal alveolar inferior pada OPG",
  "✓ Sangat dekat: deteksi + klasifikasi Winter 4 kelas pada OPG",
  "~ Sebagian: modalitas dan objek dental sama, tetapi restorasi; dipakai sebagai acuan metode fitur GLCM"],
]
table([1.0, 5.4, 5.2, 5.2, 4.6, 5.0], ["No", "Kriteria", "A1 — Khurshid dkk. (2026)",
                                        "A2 — Ulusoy dkk. (2025)", "A3 — Kandagal dkk. (2025)",
                                        "A4 — Ateş dkk. (2025)"], rowsA, fs=6.9)

para("Catatan kelayakan. Empat artikel di atas lolos seleksi; tiga artikel lain pada basis bacaan "
     "dikeluarkan dengan alasan tercatat: (i) 10.3390/app13179970 — dataset privat, tanpa precision/recall/F1 "
     "per kelas, dan kategori Winter-nya memakai kelas tambahan 'other' sehingga bukan Winter 4 kelas; "
     "(ii) 10.1038/s41598-025-93783-y — dataset privat, murni end-to-end, satu kelas minoritas ber-F1 0,000; "
     "(iii) IJPSAT 55(1):524–534 — tanpa DOI dan tanpa bukti peer review yang dapat diverifikasi. "
     "Untuk A4, kriteria 9 diberi tanda sebagian: artikel tidak meneliti M3 impaksi, sehingga perannya "
     "adalah rujukan metode (GLCM + seleksi metaheuristik + SVM) pada modalitas yang sama, bukan rujukan domain.",
     size=8, space=6)

# ---------------------------------------------------------------- tabel 1..5
HDR15 = ["No", "Informasi", "Pengaruh terhadap rancangan", "A1 Khurshid 2026",
         "A2 Ulusoy 2025", "A3 Kandagal 2025", "A4 Ateş 2025"]
W15 = [0.9, 4.4, 4.4, 4.2, 4.2, 4.2, 4.2]

def t15(title, cap, rows, fs=6.9):
    h(title, 2)
    caption(cap)
    table(W15, HDR15, rows, fs=fs)

t15("2.1 Tabel 1 — Identitas Artikel", "Seluruh identitas diverifikasi ulang melalui Crossref dan halaman penerbit.",
 [
  ["1", "Judul", "Menentukan kedekatan topik dengan proyek",
   "Dual Framework for Classification and Detection of Third Molar Impaction in Panoramic Radiographs",
   "Panoramic radiographic features for machine learning based detection of mandibular third molar root and inferior alveolar canal contact",
   "Fully automated deep learning framework for detection and classification of impacted mandibular third molars in panoramic radiographs",
   "Decision-Support for Restorative Dentistry: Hybrid Optimization Enhances Detection on Panoramic Radiographs"],
  ["2", "Penulis & tahun", "Reputasi penulis/afiliasi kedokteran gigi",
   "Khurshid Z., Alsleem M.H., Aljubairah F.A., Alghafli H.A., Alasafirah A.O., Alibrahim B.A., Alshamrani A.A., Alsuhaymi A.N. (2026) — King Faisal University, Saudi Arabia",
   "Ulusoy A.C., Toprak T., Selver M.A., Güneri P., İlhan B. (2025) — Ege University & Dokuz Eylül University, Türkiye",
   "Kandagal Veerabhadrappa S., Vengusamy S., Padarha S., Iyer K., Yadav S. (2025) — SEGi University & APU, Malaysia",
   "Ateş G., Türk F., Akçın E.T., Güngör M. (2025) — Yıldırım Beyazıt, Gazi, Lokman Hekim University, Türkiye"],
  ["3", "Jurnal, volume, halaman", "Menentukan kualitas terbitan",
   "International Dental Journal 76(2):109430 (Elsevier, Q1)",
   "Scientific Reports 15:4178 (Nature Portfolio, Q1)",
   "Journal of Oral Medicine and Oral Surgery 31(1):7 (JOMOS, OA)",
   "Healthcare 13(22):2904 (MDPI, Q1–Q2, OA)"],
  ["4", "DOI / status", "Keterlacakan dan verifikasi klaim",
   "10.1016/j.identj.2026.109430 — terbit, open access",
   "10.1038/s41598-024-82915-5 — terbit, open access",
   "10.1051/mbcb/2025008 — terbit, open access",
   "10.3390/healthcare13222904 — terbit, open access"],
  ["5", "Masalah & kontribusi", "Menentukan posisi proyek terhadap state of the art",
   "Deteksi otomatis + klasifikasi 6 kategori sudut impaksi; kontribusi: dataset publik 5.796 OPG beranotasi ganda (κ=0,92) dan pembanding YOLOv10 vs YOLOv11n.",
   "Deteksi kontak akar M3M–IAC; kontribusi: dataset publik pertama dengan anotasi semantik dan bukti bahwa fitur radiologis terukur dapat mengalahkan CNN.",
   "Deteksi + klasifikasi Winter 4 kelas end-to-end; kontribusi: kerangka dua tahap (VGG16 deteksi, ResNet50 klasifikasi) tanpa fitur manual.",
   "Klasifikasi 5 jenis restorasi; kontribusi: seleksi fitur GLCM dengan HGWO-PSO yang mengalahkan CNN pada data kecil."],
 ])

t15("2.2 Tabel 2 — Dataset dan Data", "Fokus pada lisensi, jumlah, kualitas anotasi, dan risiko kebocoran data.",
 [
  ["1", "Nama, sumber, lisensi", "Kelayakan pakai ulang data",
   "Impacted Mandibular Third Molar Dataset — Mendeley Data 10.17632/ckt876jzr6.1, CC BY 4.0 (boleh dipakai komersial, wajib sitasi)",
   "CONTACT dataset (Kaggle) — data, kode ekstraksi fitur, dan kode ML tersedia; lisensi artikel CC BY-NC-ND 4.0",
   "Arsip institusional tanpa nama formal; tersedia atas permintaan penulis; lisensi artikel CC BY 4.0",
   "Arsip Dental Imaging Center Ankara tanpa nama formal; akses via izin etik; lisensi artikel CC BY 4.0"],
  ["2", "Modalitas, resolusi, format", "Menentukan praproses dan beban komputasi",
   "OPG 2D grayscale; dimensi distandarkan; jumlah piksel asli tidak dilaporkan; citra mentah format umum (JPG/PNG)",
   "OPG 2D, 2.700×1.249 px, 4 perangkat berbeda; CBCT sebagai gold standard kontak",
   "OPG 2D dari DICOM 2.943×1.435 px, di-resize ke 224×224; satu institusi",
   "OPG 2D 2.775×1.504 px -> 1.700×880 -> 224×224; satu perangkat"],
  ["3", "Jumlah & kelas", "Menentukan kelayakan statistik dan imbalance",
   "5.796 citra; Disto 1.470, Mesio 1.100, Vertical 939, Horizontal 817, Inverted 736, Buccolingual 734; split 1.796/2.000/2.000",
   "1.478 M3M dari 1.010 pasien; kelompok kontak 1.100 vs tanpa kontak 378 (277 kasus sulit 'false positive contact')",
   "1.100 OPG berlabel (1.200 gigi) + 711 OPG negatif; Vertical 368, Mesio 328, Horizontal 295, Disto 209",
   "353 OPG, 2.137 restorasi; 5 kelas (filling, implant, root canal treatment, crown, bridge)"],
  ["4", "Anotasi & annotator", "Menentukan kualitas label acuan",
   "Bounding box di CVAT oleh mahasiswa dan intern, diverifikasi 2 spesialis; Cohen κ=0,92 (hampir sempurna)",
   "Anotasi semantik poligon (Colabeler) oleh ahli radiologi mulut; kesepakatan antar-pembaca κ=0,43 (moderat), intra 0,59–0,67",
   "LabelImg oleh 2 radiolog >10 tahun; nilai kesepakatan tidak dilaporkan",
   "Anotasi tingkat region oleh dokter gigi terkalibrasi; angka kesepakatan tidak dilaporkan"],
  ["5", "Praproses & augmentasi", "Menentukan kesetaraan perlakuan antar-kelas",
   "Standarisasi dimensi/kecerahan/kontras; augmentasi geometrik + fotometrik + StyleGAN2-ADA untuk kelas minoritas hingga 2.000 citra/kelas",
   "Penskalaan, crop ROI, k-means 4 klaster (enamel/dentin/pulpa), morfologi, skeletonization, ambang darkening 0,1/0,2/0,35; tanpa augmentasi",
   "Redaksi teks (OCR), deteksi tepi Sobel, resize; augmentasi rotasi 45°, shift 10%, shear, zoom, flip, kecerahan",
   "Crop, ImageEnhance, histogram equalization + CLAHE (clip 2,0; grid 8×8), smoothing, z-score, kuantisasi 64 level; augmentasi flip, rotasi ±10°, kecerahan ±15%"],
  ["6", "Pembagian data", "Menentukan validitas klaim generalisasi",
   "Train 1.796 / validasi 2.000 / uji 2.000; pembagian per citra, pemisahan per pasien tidak dilaporkan",
   "Monte Carlo 30 kali ulangan dengan skema 50/50 dan 80/20; pembagian per citra",
   "70/20/10; pemisahan per pasien tidak dilaporkan",
   "80/20 per pasien + 5-fold cross-validation; kelas minoritas ditangani lewat validasi silang"],
  ["7", "ROI / segmentasi", "Menentukan kebutuhan tahap deteksi",
   "Tidak ada crop manual; lokalisasi diserahkan ke YOLO, klasifikasi memakai ROI hasil deteksi",
   "Dua jalur: ROI anotasi semantik untuk CNN, dan fitur dari region hasil segmentasi untuk ML klasik",
   "ROI dari bbox YOLOv7, di-resize 224×224",
   "Tanpa ROI: fitur GLCM dihitung pada region anotasi/global setelah crop"],
 ])

t15("2.3 Tabel 3 — Rekayasa Fitur", "Menentukan apakah metode dapat direplikasi dan dijelaskan.",
 [
  ["1", "Fitur utama", "Menentukan bahan eksperimen Tahap 2",
   "Deep features: peta fitur YOLO (deteksi) dan embedding ResNet50/InceptionNetV3 (klasifikasi)",
   "6 fitur radiologis: darkening akar, interupsi garis putih IAC, defleksi IAC, penyempitan IAC, defleksi akar, penyempitan akar",
   "Tidak ada fitur manual; representasi dipelajari lapisan konvolusi VGG16/ResNet50",
   "GLCM: contrast, correlation, energy, homogeneity, entropy"],
  ["2", "Jenis fitur", "Menentukan materi PCVK yang dipakai",
   "Deep (pembelajaran representasi); bukan fitur terukur",
   "Campuran intensitas/tekstur (darkening), bentuk, dan geometri (defleksi, penyempitan)",
   "Deep (end-to-end)",
   "Tekstur statistik orde kedua (GLCM)"],
  ["3", "Cara perhitungan & dimensi", "Menentukan biaya implementasi",
   "Konvolusi backbone pretrained; vektor embedding berdimensi tinggi (ratusan–ribuan), dimensi tepat tidak dirinci",
   "Rumus darkening berbasis rasio intensitas; skeletonisasi untuk defleksi/penyempitan; vektor 6 dimensi (tanpa fitur ke-7 'bifid apex')",
   "Tidak berlaku (fitur implisit); keluaran softmax 4 kelas",
   "5 deskriptor × 4 orientasi (0°, 45°, 90°, 135°), jarak d=1, 64 level keabuan, simetris -> 20 fitur"],
  ["4", "Parameter & normalisasi", "Menentukan reproduktibilitas hasil",
   "Bobot ImageNet; ukuran input klasifikasi tidak seragam; normalisasi mengikuti backbone",
   "Ambang darkening 0,1/0,2/0,35; toleransi kemiringan & ambang penyempitan 20% (nilai lain tidak dirinci); k-means 4 klaster",
   "Resolusi 224×224; normalisasi implisit pada arsitektur",
   "GLCM simetris, d=1, 64 level; normalisasi z-score; kuantisasi 64 level"],
  ["5", "Seleksi fitur", "Menentukan kompleksitas pipeline",
   "Tidak ada seleksi fitur; seleksi dilakukan pada tingkat classifier (10 classifier diuji)",
   "Uji chi-square (fscchi2): fitur interupsi garis IAC dan darkening akar paling prediktif; fitur lain diuji kontribusinya",
   "Tidak ada seleksi fitur",
   "HGWO-PSO: populasi 10, 100 iterasi, fitness 0,9·akurasi + 0,1·(1−rasio fitur); mereduksi ±45% fitur"],
  ["6", "Alasan pemilihan", "Menentukan kesesuaian dengan tujuan proyek",
   "Embedding CNN memberi akurasi tinggi tanpa rekayasa fitur manual",
   "Fitur mengikuti indikator radiografis baku sehingga hasilnya dapat dipertanggungjawabkan secara klinis dan dihitung ulang",
   "Menghindari bias pemilihan fitur manual dan mengejar akurasi maksimum",
   "Fitur tekstur murah dan menjelaskan, dipakai bersama seleksi untuk menekan overfitting pada data kecil"],
  ["7", "Kelebihan & kelemahan", "Menentukan justifikasi metode proyek",
   "Unggul akurasi (F1 96,10), tetapi tidak ada fitur terukur, tidak ada interpretabilitas, dan label 'handcrafted' pada artikel ini tidak tepat",
   "Unggul specificity (81,92) dan F1 (90,76) melampaui 7 CNN dan radiolog, tetapi anotasi manual berat, fitur ke-7 belum diimplementasikan, dan bergantung kualitas segmentasi",
   "Akurasi tinggi (93,51) dan alur sederhana, tetapi black box, butuh data besar, tanpa metrik per kelas, dan tanpa interpretabilitas",
   "Fitur dapat dihitung ulang dan tahan data kecil, tetapi berbasis global (bukan ROI anatomi), akurasi mutlak rendah (73,15), dan hanya satu pusat"],
 ])

t15("2.4 Tabel 4 — Metode dan Eksperimen", "Menentukan pilihan arsitektur dan protokol evaluasi proyek.",
 [
  ["1", "Model / arsitektur", "Menentukan kandidat model Tahap 1 & 2",
   "Deteksi: YOLOv10 vs YOLOv11n + MHSA. Klasifikasi: ResNet50 & InceptionNetV3 + 10 classifier klasik (Fine KNN, KNN, SVM linear/kubik, RF, DT, NB, GB, AdaBoost, NN)",
   "ML klasik: ANN-MLP arsitektur 6-35-1 (tansig) dengan variasi jumlah node; pembanding 2 CNN kustom, 7 CNN pretrained, dan hybrid (fitur + citra)",
   "VGG16 (deteksi, sigmoid, ambang 0,25) + ResNet50 (klasifikasi Winter 4 kelas, softmax); pembanding YOLOv7 dan 5 arsitektur lain",
   "SVM-RBF, KNN (k=5), Decision Tree, Random Forest (100 pohon), CNN kustom; seleksi fitur HGWO-PSO"],
  ["2", "Hyperparameter", "Menentukan effort tuning",
   "YOLO: 100 epoch; Fine KNN k=1, jarak Euclidean; hyperparameter classifier lain tidak dirinci",
   "Goal 1e-3, laju belajar 0,01 adaptif, maksimum 65.000 epoch, ambang klasifikasi 0,65",
   "YOLOv7: lr 0,75, IoU 0,65, input 224; ResNet50: dense 1000/500, L2 0,01/0,03, dropout 40%/30%",
   "SVM C=10, γ=0,1; CNN: Adam 1e-4, batch 32, maksimum 50 epoch"],
  ["3", "Kombinasi yang diuji", "Menentukan luas perbandingan",
   "2 ekstraktor × 10 classifier = 20 kombinasi; 2 varian detektor",
   "ANN (beberapa konfigurasi node) × 3 skema fitur (fitur, citra, hybrid) + 9 model DL",
   "6 arsitektur deteksi × 1 arsitektur klasifikasi",
   "4 classifier × (fitur penuh vs fitur hasil seleksi) × CNN pembanding"],
  ["4", "Penanganan imbalance", "Menentukan keadilan antar-kelas",
   "Augmentasi + StyleGAN2-ADA menyeimbangkan tiap label hingga 2.000 citra",
   "ANN2 memakai data 50/50 (hasil lebih buruk); tidak memakai SMOTE; kelompok sulit tetap dipertahankan",
   "Ambang sigmoid 0,25 + augmentasi; tanpa penyeimbangan eksplisit",
   "Stratified 5-fold; tanpa penyeimbangan eksplisit"],
  ["5", "Kebutuhan komputasi", "Menentukan kelayakan Colab",
   "Google Colab A100 (YOLO) dan Kaggle P100 (fitur + klasifikasi); waktu latih per classifier dilaporkan",
   "MATLAB R2023a; perangkat GPU tidak dirinci; 30 ulangan Monte Carlo",
   "Tidak dilaporkan",
   "GPU RTX A4000; inferensi SVM 1,6 s/citra, CNN 0,9 s/citra; memori 2,3 GB"],
  ["6", "Strategi validasi", "Menentukan kejujuran angka",
   "Hold-out tetap (train/val/test) dari satu dataset; tanpa validasi eksternal",
   "Monte Carlo 30× dengan dua rasio split; tanpa validasi eksternal",
   "Split 70/20/10 sekali; tanpa validasi eksternal",
   "80/20 per pasien + 5-fold CV; tanpa validasi eksternal"],
  ["7", "Pembanding (baseline)", "Menentukan relevansi klaim 'lebih baik'",
   "Pembanding utama: YOLOv10 dan InceptionNetV3; baseline klasik antar-classifier",
   "Baseline kuat: 7 CNN pretrained + radiolog (3 pembaca); fitur tunggal vs gabungan",
   "Baseline: YOLOv7 dan 5 arsitektur deteksi lain",
   "Baseline: CNN kustom, KNN, DT, RF, serta GLCM tanpa seleksi"],
 ])

t15("2.5 Tabel 5 — Evaluasi dan Hasil", "Menentukan target kinerja dan batas klaim proyek.",
 [
  ["1", "Metrik & alasan", "Menentukan protokol evaluasi proyek",
   "Accuracy, precision, recall, F1, mAP@0.5, mAP@0.5:0.95, per-class AP — metrik deteksi dan klasifikasi dibedakan",
   "Accuracy, F1, sensitivity, specificity, PPV, NPV — specificity penting karena kasus 'false contact' banyak",
   "Accuracy, precision, recall, F1, AUC — AUC dipakai untuk menilai pemisahan 4 kelas",
   "Accuracy, precision, recall, F1, 95% CI bootstrap — CI dipakai karena sampel kecil"],
  ["2", "Hasil utama", "Menentukan target yang realistis",
   "Deteksi YOLOv11n mAP@0.5 88,90 vs YOLOv10 87,60; klasifikasi Fine KNN + ResNet50 accuracy 97,56, F1 96,10",
   "ANN 6-35-1: accuracy 85,45; F1 90,76; sensitivity 86,36; specificity 81,92; mengalahkan DL terbaik (accuracy 80,50) dan radiolog (76,65–82,40)",
   "Deteksi VGG16: accuracy 93,51, P 94,64, R 89,47, F1 91,97; klasifikasi ResNet50: accuracy 92,17, AUC 98,28, F1 91,7",
   "SVM + GLCM + HGWO-PSO: accuracy 73,15 (95% CI 71,1–75,2), macro-F1 0,728; CNN 68,52; beda signifikan (p<0,05)"],
  ["3", "Hasil per kelas", "Menentukan kelas yang perlu perhatian",
   "AP per kelas dilaporkan; presisi terendah pada Horizontal dan Mesioangular",
   "Kelas tanpa kontak paling lemah (specificity ANN tanpa penyeimbangan 44,91 pada ANN3)",
   "Tidak dilaporkan per kelas; hanya agregat",
   "Tidak ada F1 per kelas; kesalahan terbanyak antar-restorasi yang mirip (filling/crown/bridge)"],
  ["4", "Analisis kesalahan", "Menentukan fokus audit model proyek",
   "Kebingungan utama Mesioangular vs Horizontal akibat ambiguitas proyeksi 2D",
   "False positive kontak pada kasus kontak semu; fitur ke-7 (bifid apex) belum diimplementasikan",
   "Tidak dianalisis; kelas Buccolingual dan Inverted justru dikecualikan",
   "Kesalahan pada citra dengan restorasi bertumpuk dan artefak logam"],
  ["5", "Validasi eksternal", "Menentukan kejujuran klaim generalisasi",
   "Tidak ada — angka 97,56 berasal dari dataset yang sama",
   "Tidak ada — satu negara, 4 perangkat; klaim generalisasi dibatasi",
   "Tidak ada",
   "Tidak ada — satu pusat, 353 citra"],
  ["6", "Interpretabilitas", "Menentukan nilai edukatif sistem",
   "Tidak ada Grad-CAM/saliency; hanya confusion matrix",
   "Ada: uji chi-square memberi peringkat fitur + visualisasi ROI dan fitur",
   "Tidak ada",
   "Ada: bobot fitur hasil HGWO-PSO + confusion matrix"],
  ["7", "Keterbatasan penulis", "Menentukan kalimat batas klaim laporan",
   "Ambiguitas proyeksi 2D, presisi kelas sudut moderat, butuh studi multisenter",
   "Anotasi manual berat dan mahal; fitur bergantung segmentasi; sebagian fitur tidak selalu dipakai radiolog",
   "Dataset moderat, kelas Buccolingual/Inverted dikecualikan, M2 tidak dianotasi, sistem bukan pengganti dokter",
   "Data kecil dan satu pusat, fitur global (bukan ROI anatomi), hanya klasifikasi tingkat citra"],
 ])

# ---------------------------------------------------------------- tabel 6
h("3. Tabel 6 — Sintesis Perbandingan", 1)
caption("Ringkasan lintas artikel untuk memilih arsitektur akhir proyek.")
table([1.7, 4.2, 4.0, 3.6, 3.8, 4.0, 4.4, 4.0],
      ["Artikel", "Dataset & modalitas", "Praproses / segmentasi", "Fitur", "Model", "Metrik & hasil", "Kekuatan", "Kelemahan"],
      [
       ["A1 Khurshid 2026", "Publik 5.796 OPG, 6 kelas, κ=0,92", "Standarisasi + augmentasi + StyleGAN2-ADA; ROI dari detektor",
        "Deep (YOLO feature map, embedding ResNet50/Inception)", "YOLOv11n + Fine KNN/ResNet50",
        "mAP@0.5 88,90; accuracy 97,56; F1 96,10", "Data besar, label ganda, dua tahap lengkap", "Tanpa interpretabilitas; tanpa uji eksternal; klaim 'handcrafted' keliru"],
       ["A2 Ulusoy 2025", "Publik 1.478 M3M / 1.010 pasien; CBCT gold standard", "Segmentasi semantik + k-means + skeletonization; tanpa augmentasi",
        "6 fitur radiologis terukur (intensitas, bentuk, geometri)", "ANN 6-35-1; pembanding 7 CNN + radiolog",
        "Accuracy 85,45; F1 90,76; SP 81,92", "Fitur terbukti bersaing dengan CNN dan manusia; kode tersedia", "Anotasi berat; fitur ke-7 belum ada; satu negara"],
       ["A3 Kandagal 2025", "Privat 1.100 OPG / 1.200 gigi + 711 negatif", "OCR redaksi, Sobel, resize; augmentasi geometrik",
        "Deep end-to-end (VGG16, ResNet50)", "VGG16 + ResNet50; pembanding YOLOv7",
        "Deteksi 93,51; klasifikasi 92,17; AUC 98,28", "Winter 4 kelas; akurasi tinggi; alur sederhana", "Privat; tanpa κ; tanpa metrik per kelas; tanpa interpretabilitas"],
       ["A4 Ateş 2025", "Privat 353 OPG / 2.137 restorasi; 5 kelas", "Crop, HE/CLAHE, z-score; augmentasi ringan",
        "GLCM 20 fitur + seleksi HGWO-PSO", "SVM-RBF; pembanding CNN, KNN, DT, RF",
        "Accuracy 73,15; macro-F1 0,728; CNN 68,52", "Fitur jelas, seleksi terukur, tahan data kecil", "Objek bukan M3M; fitur global; satu pusat; akurasi mutlak rendah"],
      ], fs=7.0)

# ---------------------------------------------------------------- tabel 7
h("4. Tabel 7 — Keputusan dan Justifikasi", 1)
caption("Keputusan diambil setelah audit 7 artikel + audit dataset lokal (Analysis/01–07).")
table([0.9, 5.6, 13.2, 3.3], ["No", "Pertanyaan keputusan", "Jawaban dan justifikasi", "Rujukan"], [
 ["1", "Artikel mana paling relevan dengan proyek?",
  "A1 paling relevan (M3 impaksi, deteksi + klasifikasi, dataset publik, label ganda κ=0,92). A3 menyumbang taksonomi Winter 4 kelas yang paling dekat dengan target. A2 dan A4 dipakai sebagai bukti metodologis untuk jalur fitur terukur.",
  "A1, A3; A2, A4"],
 ["2", "Metode mana paling kuat, dan mengapa?",
  "Untuk akurasi: A1 (mAP@0.5 88,90; accuracy 97,56; 5.796 citra; κ=0,92). Untuk klaim berbasis fitur: A2, satu-satunya artikel yang membuktikan fitur handcrafted mengalahkan 7 CNN dan 3 radiolog dengan protokol 30 ulangan.",
  "A1 §Hasil; A2 §Hasil"],
 ["3", "Metode mana paling lemah untuk direplikasi?",
  "A3: dataset privat, tanpa κ, tanpa hasil per kelas, tanpa interpretabilitas sehingga hasil tidak dapat diverifikasi ulang. A4 lemah dari sisi domain (bukan M3M) dan akurasi mutlak (73,15%).",
  "A3, A4"],
 ["4", "Fitur mana yang akan dipakai?",
  "Dua jalur: (a) fitur geometri Winter (sudut aksis M3 terhadap M2, kedalaman relatif, rasio bbox) — inti label 4 kelas; (b) GLCM ROI (contrast, correlation, energy, homogeneity, entropy) + intensitas/tepi untuk darkening dan batas akar. Fitur deep (ResNet50 embedding) dipakai sebagai pembanding, bukan model utama.",
  "A3 (label), A2 (fitur klinis), A4 (GLCM), A1 (deep)"],
 ["5", "Lima fitur prioritas",
  "1) sudut Winter M3–M2 (°); 2) rasio jarak servikal M3 terhadap bidang oklusal M2; 3) GLCM contrast & homogeneity pada ROI M3; 4) rasio intensitas akar di daerah persilangan kanal (darkening); 5) rasio area/keliling bbox M3.",
  "A1, A2, A3, A4"],
 ["6", "Model paling sesuai untuk proyek ini",
  "Dua tahap: deteksi ROI dengan YOLOv8n/YOLOv11n (bukti mAP 88,90 di A1; 93,51 di A3), lalu klasifikasi dengan SVM-RBF/Random Forest di atas fitur terukur (bukti A2 dan A4). CNN end-to-end hanya sebagai pembanding, karena tidak dapat menjelaskan fitur dan boros data.",
  "A1, A3, A2, A4"],
 ["7", "Rekomendasi dataset",
  "Tahap 1 (deteksi + biner e/i-MTM): ExAn-MTM lokal — 973 citra, 1.784 objek, lisensi CC BY-NC-ND, sudah diunduh dan diaudit (0 citra rusak, 3 duplikat MD5). Tahap 2 (Winter 4 kelas): Khurshid 5.796 OPG (Mendeley, CC BY 4.0) yang memuat Mesio 1.100, Disto 1.470, Horizontal 817, Vertical 939; alternatif jika kuota unduh bermasalah: anotasi manual 300–500 citra dengan 2 anotator + κ.",
  "A1; audit lokal"],
 ["8", "Keputusan arsitektur akhir",
  "Pipeline dua jalur: YOLO ROI -> (A) embedding deep untuk pembanding, (B) fitur handcrafted -> seleksi (chi-square/ANOVA, HGWO-PSO sebagai pembanding) -> SVM/RF. Keluaran: kelas posisi + confidence + bbox, dengan disclaimer edukasi.",
  "A1, A2, A3, A4"],
 ["9", "Risiko yang harus dijaga",
  "Kebocoran data: ExAn-MTM terbukti subset m-TM (973 citra identik MD5 100%), sehingga keduanya tidak boleh dipakai sebagai train dan test sekaligus; test eksternal hanya 344 citra unik. Lisensi NC-ND melarang komersialisasi dan distribusi turunan. Imbalance kelas dan tidak adanya ID pasien membatasi klaim generalisasi.",
  "Audit lokal; A1–A4"],
], fs=7.0)

# ---------------------------------------------------------------- tabel 8
h("5. Tabel 8 — Rencana Dataset", 1)
caption("Basis: dataset yang sudah diunduh dan diaudit ulang (Analysis/03_Audit_Dataset.csv, 04_Distribusi_Kelas.csv, run.log).")
table([0.9, 5.6, 18.6], ["No", "Informasi", "Isian"], [
 ["1", "Nama & tautan dataset", "ExAn-MTM (Expert Annotated Mandibular Third Molar), Mendeley Data — halaman unduhan kelompok; arsip lokal: Datasets/Expert Annotated Mandibular Third Molar/ (train 875 / valid 98 citra)"],
 ["2", "Lisensi & batasan", "CC BY-NC-ND 4.0 (non-komersial, tanpa karya turunan yang didistribusikan). Dataset pembanding m-TM: CC BY-NC-SA 4.0. Dataset Khurshid (A1): CC BY 4.0. Wajib sitasi pada laporan dan repositori."],
 ["3", "Jumlah citra & kelas", "973 citra JPG grayscale 1.991×1.127 px (144,2 MB), 1.784 objek beranotasi YOLO: i-MTM 1.097 objek (61,5%) dan e-MTM 687 objek (38,5%); sebagian citra memuat lebih dari satu gigi sehingga jumlah citra per kelas tidak dijumlahkan; 0 citra rusak, 0 label tidak valid."],
 ["4", "Kualitas & duplikasi", "970 hash MD5 unik dari 973 citra (3 duplikat persis); analisis dHash (hamming ≤2) tidak menemukan pasangan near-duplicate tambahan. Tidak ada ID pasien -> split dilakukan per citra dan diakui sebagai limitasi."],
 ["5", "Hubungan dengan dataset lain", "ExAn-MTM adalah subset m-TM: 973/973 citra identik MD5. Karena itu ExAn-MTM dipakai untuk train/validasi dan m-TM hanya untuk uji eksternal setelah 973 citra tersebut dikeluarkan (sisa 344 citra unik)."],
 ["6", "Kecukupan untuk Colab", "973 citra memadai untuk YOLOv8n input 1.024 px, batch 8, 100 epoch pada GPU T4 (perkiraan 2–3 GB VRAM, <60 menit/run). Untuk Winter 4 kelas, data Khurshid (5.796 citra) lebih memadai."],
 ["7", "Bukti pengunduhan", "Audit lokal Analysis/06_Audit_Dataset.py (read-only) + run.log rc=0; grafik distribusi kelas pada Lampiran 2. Tangkapan layar Colab dilampirkan terpisah setelah notebook dijalankan (kode pada Lampiran 3)."],
 ["8", "Rencana Tahap 2", "Kelas target: Winter 4 kelas (mesioangular, distoangular, horizontal, vertical). Sumber label: (a) Khurshid 5.796 citra dengan label sudut, atau (b) anotasi manual 300–500 citra ExAn-MTM oleh 2 anotator dengan uji κ (target ≥0,80). Kelas Inverted dan Buccolingual tidak dipaksakan ke skema Winter."],
 ["9", "Etika & tata kelola", "Radiograf sudah teranonimisasi pada sumber publik; tidak ada data pasien yang diunggah ulang; dataset tidak didistribusikan ulang karena lisensi ND; sistem dinyatakan sebagai prototipe penelitian dan alat bantu edukasi, bukan alat diagnosis medis."],
], fs=7.2)

# ---------------------------------------------------------------- diagram
_h6 = h("6. Diagram Alur Sistem", 1)
_h6.paragraph_format.page_break_before = True
_h6.paragraph_format.keep_with_next = True
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.keep_with_next = True
p.paragraph_format.space_after = Pt(2)
p.add_run().add_picture(BUILD + r"\diagram_alur.png", width=Cm(20.4))
caption("Gambar 1. Arsitektur usulan: deteksi ROI dua tahap dengan dua jalur ekstraksi fitur (deep sebagai pembanding, handcrafted sebagai model utama).")

# ---------------------------------------------------------------- narasi
_h7 = h("7. Narasi Alasan Pemilihan Metode (1–2 halaman)", 1)
_h7.paragraph_format.page_break_before = True
narasi = [
 ("Pola metodologis empat artikel. Keempat artikel dapat dipetakan ke dua kubu. Kubu pertama menyerahkan seluruh proses "
  "pada jaringan dalam: A1 memakai YOLO untuk menemukan gigi lalu ResNet50/InceptionNetV3 untuk mengklasifikasi, dan A3 "
  "melatih VGG16 sebagai detektor serta ResNet50 sebagai pengklasifikasi Winter. Kubu kedua mengekstraksi fitur yang dapat "
  "dihitung ulang: A2 merumuskan enam indikator radiografis kontak M3M–IAC, sedangkan A4 menghitung matriks kookurensi "
  "keabuan (GLCM) lalu menyeleksinya dengan optimasi hybrid. Perbedaan ini penting bagi proyek PCVK karena kompetensi mata "
  "kuliah berada pada pengolahan citra klasik — praproses, segmentasi, ekstraksi ciri, seleksi ciri, dan pengklasifikasi — "
  "bukan semata pada penyetelan arsitektur CNN."),
 ("Bukti bahwa fitur handcrafted masih kompetitif. A2 memberi bukti paling kuat: dengan hanya enam fitur, ANN 6-35-1 mencapai "
  "accuracy 85,45%, F1 90,76%, sensitivity 86,36%, dan specificity 81,92%, mengungguli tujuh CNN pretrained (accuracy terbaik "
  "80,50%) dan tiga radiolog (76,65–82,40%). A4 menguatkan pola serupa pada skala kecil: GLCM 20 fitur yang diseleksi HGWO-PSO "
  "mencapai 73,15% berbanding 68,52% pada CNN kustom, dengan selisih signifikan (p<0,05). Sebaliknya, A1 dan A3 memperlihatkan "
  "bahwa deep learning memang unggul ketika data besar dan label rapi tersedia: A1 mencapai F1 96,10% pada 5.796 citra dengan "
  "κ=0,92, dan A3 mencapai accuracy 92,17% pada 1.200 gigi. Kesimpulannya bukan 'CNN buruk', melainkan bahwa nilai deep learning "
  "bergantung pada volume data dan kualitas label — dua hal yang justru menjadi batas proyek ini."),
 ("Pelajaran dari sisi data. Audit lokal menunjukkan dataset yang tersedia untuk proyek hanya 973 citra beranotasi biner "
  "(i-MTM/e-MTM). Pada volume itu, mengejar arsitektur end-to-end seperti A1 berisiko overfitting dan sulit dipertanggungjawabkan. "
  "A2 dan A4 menunjukkan jalur yang lebih hemat: fitur sedikit, terukur, dan diseleksi. Audit juga menemukan dua hal yang tidak "
  "boleh diabaikan. Pertama, ExAn-MTM adalah subset m-TM — 973 dari 973 citra identik secara MD5 — sehingga memakai keduanya "
  "sebagai train dan test akan menghasilkan kebocoran 100% dan angka evaluasi palsu. Kedua, tidak ada ID pasien pada kedua "
  "dataset, sehingga split hanya dapat dilakukan per citra; ini harus dinyatakan sebagai limitasi, bukan disembunyikan."),
 ("Kesenjangan yang diisi proyek. Tiga kesenjangan terlihat dari sintesis. (i) A1 dan A3 melaporkan angka tinggi tetapi tanpa "
  "interpretabilitas; A2 dan A4 menjelaskan fitur tetapi tidak meneliti skema Winter 4 kelas. Proyek ini menggabungkan keduanya: "
  "ROI ditemukan otomatis (seperti A1/A3) lalu diputuskan dengan fitur terukur (seperti A2/A4). (ii) A3 tidak melaporkan hasil "
  "per kelas dan tidak melaporkan kesepakatan antar-anotator, sehingga klaim akurasinya tidak dapat diperiksa; proyek ini akan "
  "melaporkan F1 per kelas, confusion matrix, dan interval kepercayaan bootstrap. (iii) Tidak satu pun artikel melakukan validasi "
  "eksternal; proyek ini menyiapkan uji eksternal dari sisa unik m-TM (344 citra) agar generalisasi diuji, bukan diasumsikan."),
 ("Konsekuensi rancangan. Berdasarkan keputusan pada Tabel 7, pipeline dibangun dua tahap. Tahap 1: deteksi bbox M3 dan M2 dengan "
  "YOLOv8n/YOLOv11n pada input 1.024 px, dengan augmentasi ringan dan mosaic dimatikan pada 10 epoch terakhir; target realistis "
  "adalah mAP@0.5 pada kisaran 80–89% mengacu A1 dan A3, bukan menyalin angka 97,56% A1 yang dihasilkan dari 5.796 citra. "
  "Tahap 2: dua jalur fitur pada ROI hasil deteksi — jalur handcrafted (sudut Winter, rasio geometri, GLCM, intensitas akar) dengan "
  "seleksi chi-square/ANOVA dan pembanding HGWO-PSO, serta jalur deep (embedding ResNet50) sebagai pembanding setara. Pengklasifikasi "
  "utama SVM-RBF dan Random Forest, dengan ANN-MLP sebagai pembanding mengikuti A2. Metrik utama accuracy, macro-F1, F1 per kelas, "
  "confusion matrix, dan 95% CI; untuk deteksi mAP@0.5 dan mAP@0.5:0.95."),
 ("Batas klaim dan etika. Semua angka pada laporan akhir akan disajikan sebagai hasil prototipe pada dataset terbatas, bukan sebagai "
  "klaim klinis. Radiograf berasal dari sumber publik teranonimisasi dan tidak akan didistribusikan ulang karena lisensi CC BY-NC-ND. "
  "Sistem tidak digunakan untuk keputusan terapi; keluarannya adalah kelas posisi, confidence score, dan bounding box yang harus "
  "diverifikasi pembaca manusia. Dengan pembatasan ini, proyek tetap memenuhi tuntutan akademik — metode dapat direplikasi, hasil "
  "dapat diaudit, dan klaim sepadan dengan bukti."),
]
for n, t_ in enumerate(narasi, 1):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(5)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run(t_).font.size = Pt(9)

# ---------------------------------------------------------------- lampiran
doc.add_page_break()
h("Lampiran 1. Daftar Pustaka (APA 7)", 1)
refs = [
 "Ateş, G., Türk, F., Akçın, E. T., & Güngör, M. (2025). Decision-support for restorative dentistry: Hybrid optimization enhances detection on panoramic radiographs. Healthcare, 13(22), 2904. https://doi.org/10.3390/healthcare13222904",
 "Kandagal Veerabhadrappa, S., Vengusamy, S., Padarha, S., Iyer, K., & Yadav, S. (2025). Fully automated deep learning framework for detection and classification of impacted mandibular third molars in panoramic radiographs. Journal of Oral Medicine and Oral Surgery, 31(1), 7. https://doi.org/10.1051/mbcb/2025008",
 "Khurshid, Z., Alsleem, M. H., Aljubairah, F. A., Alghafli, H. A., Alasafirah, A. O., Alibrahim, B. A., Alshamrani, A. A., & Alsuhaymi, A. N. (2026). Dual framework for classification and detection of third molar impaction in panoramic radiographs. International Dental Journal, 76(2), 109430. https://doi.org/10.1016/j.identj.2026.109430",
 "Ulusoy, A. C., Toprak, T., Selver, M. A., Güneri, P., & İlhan, B. (2025). Panoramic radiographic features for machine learning based detection of mandibular third molar root and inferior alveolar canal contact. Scientific Reports, 15, 4178. https://doi.org/10.1038/s41598-024-82915-5",
 "Khurshid, Z., et al. (2026). Impacted Mandibular Third Molar Dataset [Data set]. Mendeley Data, V1. https://doi.org/10.17632/ckt876jzr6.1",
]
for r_ in refs:
    p = doc.add_paragraph(r_)
    p.paragraph_format.left_indent = Cm(0.8)
    p.paragraph_format.first_line_indent = Cm(-0.8)
    p.paragraph_format.space_after = Pt(4)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.runs[0].font.size = Pt(8.5)

h("Lampiran 2. Bukti Audit Dataset (hitung ulang lokal)", 1)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run().add_picture(CHART, width=Cm(12.5))
caption("Gambar 2. Distribusi kelas ExAn-MTM hasil audit lokal (Analysis/06_Audit_Dataset.py, read-only): "
        "973 citra, 1.784 objek, 0 label tidak valid, 3 duplikat MD5.")

h("Lampiran 3. Kode Pemeriksaan Jumlah Citra per Kelas di Colab", 1)
kode = ("!pip -q install ultralytics\n"
        "import glob, collections, yaml\n"
        "root = '/content/ExAn-MTM'\n"
        "names = yaml.safe_load(open(f'{root}/data.yaml'))['names']\n"
        "cnt = collections.Counter()\n"
        "for sp in ('train', 'valid'):\n"
        "    for f in glob.glob(f'{root}/{sp}/labels/*.txt'):\n"
        "        for ln in open(f):\n"
        "            if ln.strip():\n"
        "                cnt[int(ln.split()[0])] += 1\n"
        "print('citra  :', {sp: len(glob.glob(f'{root}/{sp}/images/*')) for sp in ('train','valid')})\n"
        "print('objek  :', {names.get(k, k): v for k, v in sorted(cnt.items())})")
p = doc.add_paragraph()
r = p.add_run(kode); r.font.name = "Consolas"; r.font.size = Pt(8)
p.paragraph_format.left_indent = Cm(0.4)
p.paragraph_format.space_after = Pt(6)

h("Lampiran 4. Checklist Luaran", 1)
table([0.9, 8.6, 2.2, 13.4], ["No", "Luaran", "Status", "Bukti / catatan"], [
 ["1", "Dokumen studi literatur lengkap (Tabel A + Tabel 1–8 + diagram + narasi + daftar pustaka)",
  "Selesai", "Dokumen ini; 4 artikel dengan DOI terverifikasi via Crossref"],
 ["2", "Dataset terpilih sudah diunduh", "Selesai", "ExAn-MTM 973 citra (144,2 MB) + m-TM 1.317 citra; auditor: Analysis/06_Audit_Dataset.py"],
 ["3", "Tabel jumlah citra per kelas + bukti tangkapan layar", "Sebagian", "Tabel 8 dan Lampiran 2 sudah berisi angka nyata; tangkapan layar Colab dilampirkan setelah notebook dijalankan (kode Lampiran 3)"],
 ["4", "Diagram alur sistem", "Selesai", "Gambar 1 (Analysis/build/diagram_alur.png)"],
 ["5", "Narasi alasan pemilihan metode 1–2 halaman", "Selesai", "Bagian 7, enam paragraf dengan rujukan A1–A4"],
], fs=7.6)

doc.save(OUT)
print("saved", OUT)