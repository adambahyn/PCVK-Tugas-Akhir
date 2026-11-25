"""Diagram alur PCVK v4 — koordinat dalam poin agar tinggi kotak pas dengan jumlah baris."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

W, H = 9.2, 7.4            # inci
PT = 72.0                  # 1 satuan = 1 poin
fig, ax = plt.subplots(figsize=(W, H), dpi=300)
ax.set_xlim(0, W * PT); ax.set_ylim(0, H * PT); ax.axis("off")

C = dict(inp="#dbeafe", prep="#e0f2fe", roi="#d1fae5", ft="#fef3c7",
         clf="#ede9fe", out="#fee2e2", edge="#334155")
FS = 10.5
LH = FS * 1.45             # tinggi baris (pt)


def box(cx, cy_top, w, title, lines, color, fs=FS):
    h = 8 + (fs + 1.8) * 1.45 + LH * len(lines) + 6
    cy = cy_top - h / 2
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                                boxstyle="round,pad=0.6,rounding_size=8",
                                linewidth=1.3, edgecolor=C["edge"], facecolor=color))
    ax.text(cx, cy_top - 8, title, ha="center", va="top",
            fontsize=fs + 1.8, fontweight="bold", color="#0f172a")
    ax.text(cx, cy_top - 8 - (fs + 1.8) * 1.45, "\n".join(lines), ha="center", va="top",
            fontsize=fs, color="#1e293b", linespacing=1.45)
    return cy_top - h, cy            # (bawah kotak, pusat)


def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=15, linewidth=1.4, color=C["edge"]))


y = H * PT - 4
y, _ = box(W * PT / 2, y, 520, "INPUT — Radiograf panoramik (OPG)",
           ["JPG/DICOM · grayscale · dataset ExAn-MTM (973 citra)"], C["inp"])
arrow(W * PT / 2, y, W * PT / 2, y - 18)
y -= 18
y, _ = box(W * PT / 2, y, 540, "PRAPROSES",
           ["redaksi identitas (OCR+mask) · resize 1.024 px",
            "CLAHE clip 2,0 grid 8x8 · normalisasi [0,1]"], C["prep"])
arrow(W * PT / 2, y, W * PT / 2, y - 18)
y -= 18
y, _ = box(W * PT / 2, y, 560, "DETEKSI & ROI — YOLOv8n / YOLOv11n",
           ["bbox molar ketiga (M3) + molar kedua (M2)",
            "keluaran: koordinat + confidence · mAP@0.5"], C["roi"])
arrow(W * PT / 2, y, W * PT / 2, y - 18)
y -= 18
y, crop_bot = box(W * PT / 2, y, 520, "CROP ROI",
                  ["potong bbox M2+M3 · resize 224x224 (jalur A)",
                   "citra ROI penuh (jalur B)"], "#dcfce7")

# percabangan dua jalur
L, R = W * PT * 0.27, W * PT * 0.73
arrow(W * PT / 2 - 40, crop_bot, L, crop_bot - 26)
arrow(W * PT / 2 + 40, crop_bot, R, crop_bot - 26)
ax.text(W * PT / 2 - 55, crop_bot - 13, "jalur A", fontsize=9.5, style="italic",
        ha="right", va="center", color="#1e293b")
ax.text(W * PT / 2 + 55, crop_bot - 13, "jalur B", fontsize=9.5, style="italic",
        ha="left", va="center", color="#1e293b")
y = crop_bot - 26

yA, _ = box(L, y, 300, "A. DEEP FEATURES",
            ["ResNet50 / InceptionNetV3", "embedding deep", "classifier: Fine KNN k=1, SVM"],
            C["ft"], fs=9.6)
yB, _ = box(R, y, 300, "B. HANDCRAFTED",
            ["geometri: sudut Winter, rasio bbox", "GLCM: contrast, energy, entropy",
             "(d=1; 0/45/90/135 derajat)"], C["ft"], fs=9.6)
arrow(L, yA, L, yA - 18)
arrow(R, yB, R, yB - 18)

_, _ = box(L, yA - 18, 300, "SELEKSI FITUR",
           ["chi-square / ANOVA · HGWO-PSO"], C["clf"], fs=9.6)
yS, _ = box(R, yA - 18, 300, "KLASIFIKASI",
            ["SVM RBF · RF · KNN"], C["clf"], fs=9.6)
arrow(L + 150, yS + 14, R - 150, yS + 14)

arrow(L, yS, L, yS - 18)
arrow(R, yS, R, yS - 18)
y = yS - 18
y, _ = box(W * PT / 2, y, 600, "OUTPUT",
           ["kelas Winter 4 kelas · confidence score · bbox pada citra",
            "prototipe penelitian & alat bantu edukasi, bukan alat diagnosis medis"], C["out"], fs=9.6)

ax.text(W * PT / 2, y - 12,
        "Evaluasi: accuracy · macro-F1 · F1 per kelas · confusion matrix · 95% CI · mAP@0.5",
        ha="center", va="top", fontsize=9.0, color="#475569")
print("sisa ruang bawah (pt):", round(y - 34, 1))

fig.savefig(r"C:\Kuliah\Tingkat 3\PCVK\Project\Analysis\build\diagram_alur4.png",
            bbox_inches="tight", pad_inches=0.15, facecolor="white")
print("ok")