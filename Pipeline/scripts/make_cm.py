"""Confusion matrix deteksi yang bisa diaudit sendiri.

Ultralytics menghitung `confusion_matrix.matrix` dengan akumulasi yang, pada
versi ini, menghasilkan jumlah baris/kolom yang tidak sama dengan jumlah GT
(diverifikasi: kolom = [63, 117, 237] sementara GT = [63, 117]). Skrip ini
membangun matriks sendiri dengan pencocokan greedy class-agnostic pada IoU 0.5
(kebijakan yang sama dengan validator ultralytics) dan memverifikasi bahwa
jumlah baris = jumlah GT per kelas.

Output: Pipeline/outputs/confusion_matrix.json + figures/fig_confusion_deteksi.png
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "Pipeline" / "outputs"
WEIGHTS = OUT / "runs" / "yolo11n_exanmtm" / "weights" / "best.pt"
CONF, IOU_MATCH, IMGSZ = 0.25, 0.5, 448
NAMES = ["e-MTM", "i-MTM"]
NC = len(NAMES)


def iou_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """IoU antara box xyxy (N,4) dan (M,4)."""
    if len(a) == 0 or len(b) == 0:
        return np.zeros((len(a), len(b)))
    lt = np.maximum(a[:, None, :2], b[None, :, :2])
    rb = np.minimum(a[:, None, 2:], b[None, :, 2:])
    wh = np.clip(rb - lt, 0, None)
    inter = wh[..., 0] * wh[..., 1]
    area_a = np.prod(a[:, 2:] - a[:, :2], axis=1)
    area_b = np.prod(b[:, 2:] - b[:, :2], axis=1)
    return inter / (area_a[:, None] + area_b[None, :] - inter + 1e-9)


def load_gt(label_path: Path, w: int, h: int) -> tuple[np.ndarray, np.ndarray]:
    """Baca label YOLO (cls cx cy bw bh, ternormalisasi) -> (cls, xyxy piksel)."""
    rows = [ln.split() for ln in label_path.read_text().splitlines() if ln.strip()]
    if not rows:
        return np.zeros(0, int), np.zeros((0, 4))
    arr = np.array(rows, dtype=float)
    cls = arr[:, 0].astype(int)
    cx, cy, bw, bh = arr[:, 1] * w, arr[:, 2] * h, arr[:, 3] * w, arr[:, 4] * h
    xyxy = np.stack([cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2], axis=1)
    return cls, xyxy


def main() -> None:
    import yaml

    data = yaml.safe_load((ROOT / "Pipeline" / "data.yaml").read_text())
    val_dir = Path(data["path"]) / data["val"]
    if not val_dir.is_absolute():
        val_dir = (ROOT / "Pipeline" / val_dir).resolve()
    lab_dir = Path(str(val_dir).replace("images", "labels", 1))

    model = YOLO(str(WEIGHTS))
    cm = np.zeros((NC + 1, NC + 1), dtype=int)  # baris = GT, kolom = prediksi, indeks NC = background
    n_gt = np.zeros(NC, dtype=int)

    images = sorted(p for p in val_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
    for img in images:
        res = model.predict(str(img), imgsz=IMGSZ, conf=CONF, verbose=False, device="cpu")[0]
        h, w = res.orig_shape
        gt_cls, gt_box = load_gt(lab_dir / f"{img.stem}.txt", w, h)
        n_gt += np.bincount(gt_cls, minlength=NC)[:NC]
        pr_box = res.boxes.xyxy.cpu().numpy()
        pr_cls = res.boxes.cls.cpu().numpy().astype(int)
        pr_conf = res.boxes.conf.cpu().numpy()

        order = np.argsort(-pr_conf)
        pr_box, pr_cls = pr_box[order], pr_cls[order]
        ious = iou_matrix(pr_box, gt_box)
        claimed = np.zeros(len(gt_cls), bool)
        for i in range(len(pr_box)):
            cand = np.where(~claimed & (ious[i] >= IOU_MATCH))[0]
            if len(cand) == 0:
                cm[NC, pr_cls[i]] += 1  # false positive
                continue
            j = cand[np.argmax(ious[i, cand])]
            claimed[j] = True
            cm[gt_cls[j], pr_cls[i]] += 1
        for j in np.where(~claimed)[0]:
            cm[gt_cls[j], NC] += 1  # false negative

    row_sums = cm.sum(1)[:NC]
    assert np.array_equal(row_sums, n_gt), f"baris != jumlah GT: {row_sums} vs {n_gt}"

    tp = np.diag(cm)[:NC]
    precision = tp / np.maximum(cm.sum(0)[:NC], 1)
    recall = tp / np.maximum(n_gt, 1)
    payload = {
        "matrix": cm.tolist(),
        "labels": NAMES + ["background"],
        "rows": "ground truth",
        "cols": "prediksi",
        "conf": CONF,
        "iou_match": IOU_MATCH,
        "imgsz": IMGSZ,
        "n_gt": n_gt.tolist(),
        "per_class": {
            NAMES[i]: {
                "TP": int(tp[i]),
                "FP": int(cm[:, i].sum() - tp[i]),
                "FN": int(cm[i, :].sum() - tp[i]),
                "precision_at_conf": round(float(precision[i]), 4),
                "recall_at_conf": round(float(recall[i]), 4),
            }
            for i in range(NC)
        },
    }
    (OUT / "confusion_matrix.json").write_text(json.dumps(payload, indent=1), encoding="utf-8")

    fig, ax = plt.subplots(figsize=(5.6, 4.8))
    im = ax.imshow(cm, cmap="Blues")
    labels = NAMES + ["background"]
    ax.set_xticks(range(NC + 1), labels, rotation=20)
    ax.set_yticks(range(NC + 1), labels)
    ax.set_xlabel("Prediksi")
    ax.set_ylabel("Ground truth")
    ax.set_title(f"Confusion matrix deteksi (conf={CONF}, IoU={IOU_MATCH})")
    vmax = cm.max()
    for i in range(NC + 1):
        for j in range(NC + 1):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                    color="white" if cm[i, j] > vmax * 0.55 else "black", fontsize=11)
    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    fig.savefig(OUT / "figures" / "fig_confusion_deteksi.png", dpi=160)
    print("matrix", cm.tolist(), "| GT", n_gt.tolist())
    print("per_class", json.dumps(payload["per_class"]))


if __name__ == "__main__":
    main()
