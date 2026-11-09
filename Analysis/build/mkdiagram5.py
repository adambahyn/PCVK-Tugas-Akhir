"""Diagram alur PCVK v5 — 1 satuan = 1 poin cetak; lebar 15,5 cm, font 1:1 dengan hasil cetak.

Dijalankan dengan self-check: setiap teks harus berada di dalam kotaknya,
tidak ada dua kotak yang bertumpuk.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

CM = 28.3465
WIDTH_CM = 15.5
W = WIDTH_CM * CM / 72.0          # inci, sehingga 1 pt gambar = 1 pt cetak
H = 6.45
PT = 72.0
fig, ax = plt.subplots(figsize=(W, H), dpi=400)
fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
ax.set_xlim(0, W * PT); ax.set_ylim(0, H * PT); ax.axis("off")

C = dict(inp="#dbeafe", prep="#e0f2fe", roi="#d1fae5", ft="#fef3c7",
         clf="#ede9fe", out="#fee2e2", edge="#334155")
FS = 8.4
LH = FS * 1.5             # jarak baris aktual (pt)
TFS = FS + 1.4            # judul kotak

boxes, texts = [], []


def box(cx, top, w, title, lines, color, fs=FS):
    th = (fs + 1.4) * 1.5
    h = 5 + th + LH * len(lines) + 5
    cy = top - h / 2
    p = FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                       boxstyle="round,pad=0.4,rounding_size=5",
                       linewidth=1.1, edgecolor=C["edge"], facecolor=color)
    ax.add_patch(p)
    t1 = ax.text(cx, top - 5, title, ha="center", va="top",
                 fontsize=fs + 1.4, fontweight="bold", color="#0f172a")
    t2 = ax.text(cx, top - 5 - th, "\n".join(lines), ha="center", va="top",
                 fontsize=fs, color="#1e293b", linespacing=1.5)
    boxes.append((p, title))
    texts.extend([(t1, p, title), (t2, p, title)])
    return top - h, cy


def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=10, linewidth=1.0,
                                 color=C["edge"], shrinkA=0, shrinkB=0))


CX = W * PT / 2
GAP = 14
y = H * PT - 2
y, _ = box(CX, y, 380, "INPUT — Radiograf panoramik (OPG)",
           ["JPG/DICOM · grayscale · ExAn-MTM (973 citra)"], C["inp"])
arrow(CX, y, CX, y - GAP); y -= GAP
y, _ = box(CX, y, 400, "PRAPROSES",
           ["redaksi identitas (OCR+mask) · resize 1.024 px",
            "CLAHE clip 2,0 grid 8x8 · normalisasi [0,1]"], C["prep"])
arrow(CX, y, CX, y - GAP); y -= GAP
y, _ = box(CX, y, 410, "DETEKSI & ROI — YOLOv8n / YOLOv11n",
           ["bbox molar ketiga (M3) + molar kedua (M2)",
            "keluaran: koordinat + confidence · mAP@0.5"], C["roi"])
arrow(CX, y, CX, y - GAP); y -= GAP
y, _crop_c = box(CX, y, 400, "CROP ROI",
                 ["bbox M2+M3 -> jalur A (resize 224x224)",
                  "citra ROI penuh -> jalur B"], "#dcfce7")

L, R = CX - 105, CX + 105
arrow(CX - 34, y, L, y - GAP)
arrow(CX + 34, y, R, y - GAP)
y = y - GAP

yA, _ = box(L, y, 190, "A. DEEP FEATURES",
            ["ResNet50 / InceptionNetV3", "embedding deep",
             "classifier: Fine KNN k=1, SVM"], C["ft"], fs=7.9)
yB, _ = box(R, y, 190, "B. HANDCRAFTED",
            ["geometri: sudut Winter, rasio bbox",
             "GLCM: contrast, energy, entropy",
             "(d=1; 0/45/90/135 derajat)"], C["ft"], fs=7.9)
arrow(L, yA, L, yA - GAP)
arrow(R, yB, R, yB - GAP)

CS = 190
yS, _ = box(L, yA - GAP, CS, "SELEKSI FITUR",
            ["chi-square / ANOVA · HGWO-PSO"], C["clf"], fs=7.9)
_, _ = box(R, yA - GAP, CS, "KLASIFIKASI",
           ["SVM RBF · RF · KNN"], C["clf"], fs=7.9)
arrow(L + CS / 2, yS - 1, R - CS / 2, yS - 1)

arrow(L, yS, L, yS - GAP)
arrow(R, yS, R, yS - GAP)
y = yS - GAP
y, _ = box(CX, y, 420, "OUTPUT",
           ["kelas Winter 4 kelas · confidence score · bbox",
            "prototipe penelitian & alat bantu edukasi,",
            "bukan alat diagnosis medis"], C["out"], fs=7.9)

ax.text(CX, y - 8,
        "Evaluasi: accuracy · macro-F1 · F1 per kelas · confusion matrix · 95% CI · mAP@0.5",
        ha="center", va="top", fontsize=7.4, color="#475569")

# ------------------------------------------------------------------ self-check
fig.canvas.draw()
r = fig.canvas.get_renderer()
inv = ax.transData.inverted()
bad = []
for t, p, name in texts:
    tb = t.get_window_extent(r)
    pb = p.get_window_extent(r)
    if tb.x0 < pb.x0 - 0.5 or tb.x1 > pb.x1 + 0.5 or tb.y0 < pb.y0 - 0.5 or tb.y1 > pb.y1 + 0.5:
        bad.append("teks keluar kotak: " + name + " " + str([round(v) for v in (tb.x0 - pb.x0, pb.x1 - tb.x1, tb.y0 - pb.y0, pb.y1 - tb.y1)]))
ext = [(p.get_window_extent(r), n) for p, n in boxes]
for i in range(len(ext)):
    for j in range(i + 1, len(ext)):
        a, na = ext[i]; b, nb = ext[j]
        if a.overlaps(b):
            bad.append("kotak bertumpuk: " + na + " / " + nb)
alloc_top = H * PT - 2
alloc_bot = y - 14
print("tinggi total (pt):", round(alloc_top - alloc_bot, 1), "dari", round(H * PT, 1))
print("SELF-CHECK:", "OK" if not bad else bad)

fig.savefig(r"C:\Kuliah\Tingkat 3\PCVK\Project\Analysis\build\diagram_alur5.png",
            bbox_inches="tight", pad_inches=0.06, facecolor="white")
print("saved diagram_alur5.png")