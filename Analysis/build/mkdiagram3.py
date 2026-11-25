"""Diagram alur PCVK versi 3 — font besar agar terbaca saat dicetak selebar 15,5 cm."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

W, H = 9.2, 7.6
fig, ax = plt.subplots(figsize=(W, H), dpi=300)
ax.set_xlim(0, 100); ax.set_ylim(-6, 100); ax.axis("off")

C = dict(inp="#dbeafe", prep="#e0f2fe", roi="#d1fae5", ft="#fef3c7",
         clf="#ede9fe", out="#fee2e2", edge="#334155")
FS = 10.5


def box(cx, cy, w, h, title, body, color, fs=FS):
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                                boxstyle="round,pad=0.35,rounding_size=1.1",
                                linewidth=1.4, edgecolor=C["edge"], facecolor=color))
    ax.text(cx, cy + h / 2 - 2.0, title, ha="center", va="top",
            fontsize=fs + 1.8, fontweight="bold", color="#0f172a")
    ax.text(cx, cy + h / 2 - 6.2, body, ha="center", va="top", fontsize=fs,
            color="#1e293b", linespacing=1.45)


def arrow(x1, y1, x2, y2, lbl=None, rad=0.0):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=16, linewidth=1.5,
                                 color=C["edge"], connectionstyle=f"arc3,rad={rad}"))
    if lbl:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 - 0.3, lbl, fontsize=9.5,
                style="italic", color="#1e293b", ha="center", va="center",
                bbox=dict(fc="white", ec="none", pad=1.6))


box(50, 94.5, 84, 10.4, "INPUT — Radiograf panoramik (OPG)",
    "JPG/DICOM · grayscale · dataset ExAn-MTM (973 citra)", C["inp"])
arrow(50, 89.2, 50, 85.9)

box(50, 80, 86, 10.4, "PRAPROSES",
    "redaksi identitas (OCR+mask) · resize 1.024 px\n"
    "CLAHE clip 2,0 grid 8x8 · normalisasi [0,1]", C["prep"])
arrow(50, 74.7, 50, 71.4)

box(50, 65, 88, 12.2, "DETEKSI & ROI — YOLOv8n / YOLOv11n",
    "bbox molar ketiga (M3) + molar kedua (M2)\n"
    "keluaran: koordinat + confidence (mAP@0.5)", C["roi"])
arrow(50, 58.8, 50, 55.5)

box(50, 50, 84, 10.4, "CROP ROI",
    "potong bbox M2+M3 · resize 224x224 (A)\n"
    "citra ROI penuh (B)", "#dcfce7")
arrow(50, 44.7, 27, 41.6, "jalur A")
arrow(50, 44.7, 73, 41.6, "jalur B")

box(26.5, 33.4, 47, 15.4, "A. DEEP FEATURES",
    "ResNet50 / InceptionNetV3\n"
    "embedding deep\n"
    "classifier: Fine KNN k=1, SVM", C["ft"], fs=9.8)
box(73.5, 33.4, 47, 15.4, "B. HANDCRAFTED",
    "geometri: sudut Winter, rasio bbox\n"
    "GLCM: contrast, energy, entropy\n"
    "(d=1; 0/45/90/135 derajat)", C["ft"], fs=9.8)
arrow(26.5, 25.6, 26.5, 22.9)
arrow(73.5, 25.6, 73.5, 22.9)

box(26.5, 17.6, 47, 10.0, "SELEKSI FITUR",
    "chi-square / ANOVA · HGWO-PSO", C["clf"], fs=9.8)
box(73.5, 17.6, 47, 10.0, "KLASIFIKASI",
    "SVM RBF · RF · KNN", C["clf"], fs=9.8)
arrow(50.2, 17.6, 50.2, 17.6)
arrow(26.5, 12.5, 26.5, 9.9)
arrow(73.5, 12.5, 73.5, 9.9)

box(50, 4.4, 94, 10.6, "OUTPUT",
    "kelas Winter 4 kelas · confidence score · bbox pada citra\n"
    "prototipe penelitian & alat bantu edukasi, bukan alat diagnosis medis",
    C["out"], fs=9.8)

ax.text(50, -4.6,
        "Evaluasi: accuracy · macro-F1 · F1 per kelas · confusion matrix · 95% CI · mAP@0.5",
        ha="center", va="bottom", fontsize=9.2, color="#475569")

fig.savefig(r"C:\Kuliah\Tingkat 3\PCVK\Project\Analysis\build\diagram_alur3.png",
            bbox_inches="tight", pad_inches=0.18, facecolor="white")
print("ok")
