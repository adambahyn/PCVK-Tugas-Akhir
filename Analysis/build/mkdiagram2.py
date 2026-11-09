"""Diagram alur sistem proyek akhir PCVK -> PNG (matplotlib), versi 2 (tata letak lega)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(11.5, 8.2), dpi=200)
ax.set_xlim(0, 100); ax.set_ylim(-4.5, 100); ax.axis("off")

C = dict(inp="#dbeafe", prep="#e0f2fe", roi="#d1fae5", ft="#fef3c7",
         clf="#ede9fe", out="#fee2e2", edge="#334155")
FS = 8.0


def box(cx, cy, w, h, title, body, color, fs=FS):
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                                boxstyle="round,pad=0.3,rounding_size=1.2",
                                linewidth=1.3, edgecolor=C["edge"], facecolor=color))
    ax.text(cx, cy + h / 2 - 1.6, title, ha="center", va="top",
            fontsize=fs + 1.5, fontweight="bold", color="#0f172a")
    ax.text(cx, cy + 1.6, body, ha="center", va="top", fontsize=fs,
            color="#1e293b", linespacing=1.35)


def arrow(x1, y1, x2, y2, lbl=None, rad=0.0):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=13, linewidth=1.25,
                                 color=C["edge"], connectionstyle=f"arc3,rad={rad}"))
    if lbl:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 - 0.2, lbl, fontsize=7.4,
                style="italic", color="#1e293b", ha="center", va="center",
                bbox=dict(fc="white", ec="none", pad=1.4))


box(50, 95, 64, 9, "INPUT — Radiograf panoramik (OPG)",
    "JPG / DICOM · 1991x1127 px · grayscale · dataset ExAn-MTM (973 citra)", C["inp"])
arrow(50, 90.5, 50, 86.6)

box(50, 80.4, 68, 11.6, "PRAPROSES",
    "Redaksi identitas pasien (OCR + mask) · resize 1024 px\n"
    "CLAHE clip 2.0 grid 8x8 · normalisasi [0,1] · denoise median 3x3", C["prep"])
arrow(50, 74.6, 50, 71.1)

box(50, 65, 68, 11.6, "DETEKSI & PENENTUAN ROI — YOLOv8n / YOLOv11n",
    "bbox molar ketiga (M3) + molar kedua (M2) sebagai acuan angulasi\n"
    "keluaran: koordinat + confidence · metrik mAP@0.5 dan mAP@0.5:0.95", C["roi"])
arrow(50, 59.2, 50, 55.7)

box(50, 50, 74, 10.4, "CROP ROI",
    "potong bbox M2+M3 -> resize 224x224 (jalur A) · citra ROI penuh (jalur B)", "#dcfce7")
arrow(50, 44.8, 28, 40.4, "jalur A")
arrow(50, 44.8, 72, 40.4, "jalur B")

box(26, 34, 40, 13.6, "A. DEEP FEATURES",
    "ResNet50 / InceptionNetV3 (ImageNet)\n"
    "embedding deep\n"
    "classifier ML klasik (Fine KNN k=1, SVM)", C["ft"], fs=7.8)
box(74, 34, 40, 13.6, "B. HANDCRAFTED FEATURES",
    "Geometri: sudut Winter (M3 vs M2), rasio bbox\n"
    "GLCM: contrast, correlation, energy,\n"
    "homogeneity, entropy (d=1; 0/45/90/135)", C["ft"], fs=7.8)
arrow(26, 27.2, 26, 24.4)
arrow(74, 27.2, 74, 24.4)

box(26, 19.4, 40, 9.4, "SELEKSI FITUR", "chi-square / ANOVA · HGWO-PSO (pembanding)", C["clf"])
box(74, 19.4, 40, 9.4, "KLASIFIKASI", "SVM RBF (C=10, g=0.1) · RF · KNN", C["clf"])
arrow(46.2, 19.4, 53.8, 19.4, "fitur terpilih")
arrow(26, 14.7, 26, 11.2)
arrow(74, 14.7, 74, 11.2)

box(50, 5.6, 78, 10.6, "OUTPUT",
    "kelas posisi: mesioangular / distoangular / horizontal / vertical · confidence score · bbox pada citra\n"
    "disclaimer: prototipe penelitian & alat bantu edukasi, bukan alat diagnosis medis", C["out"])

ax.text(99, -4.0,
        "Evaluasi: accuracy · macro-F1 · F1 per kelas · confusion matrix · 95% CI bootstrap | deteksi: mAP@0.5 & mAP@0.5:0.95 | split terkunci + cek duplikasi MD5/dHash",
        ha="right", va="bottom", fontsize=6.9, color="#475569")

fig.savefig(r"C:\Kuliah\Tingkat 3\PCVK\Project\Analysis\build\diagram_alur.png",
            bbox_inches="tight", pad_inches=0.25, facecolor="white")
print("ok")