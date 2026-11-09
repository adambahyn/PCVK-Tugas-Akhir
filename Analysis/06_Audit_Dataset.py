#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
06_Audit_Dataset.py — audit langsung dataset PCVK (gigi molar ketiga impaksi).

Menghitung, tanpa mengubah file asli:
  * jumlah citra / citra terbuka / citra rusak, format, resolusi (min/median/max/rata2), ukuran total
  * jumlah objek & anotasi, validitas bounding box YOLO, distribusi kelas (objek & citra)
  * duplikasi exact (MD5) dan near-duplicate (dHash 8x8) + tumpang-tindih antar dataset
  * ringkasan masker segmentasi (dataset `archive`) dan tabel fitur (xlsx)

Keluaran: 03_Audit_Dataset.csv, 04_Distribusi_Kelas.csv, audit_raw.json (di folder Analysis).

Pemakaian (Windows, python 3.13 + Pillow; openpyxl opsional):
    python 06_Audit_Dataset.py
    python 06_Audit_Dataset.py --root "C:/Kuliah/Tingkat 3/PCVK/Project/Datasets" \
        --out  "C:/Kuliah/Tingkat 3/PCVK/Project/Analysis" --extract

Arsip .rar/.zip dibaca dengan mengekstrak SATU KALI ke cache (%LOCALAPPDATA%\\hermes\\cache\\pcvk-audit)
kalau --extract dipakai; tanpa --extract arsip yang belum pernah diekstrak hanya dihitung jumlah entrinya.
"""
import argparse
import csv
import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:                      # audit tetap jalan tanpa Pillow (resolusi dilewati)
    Image = None
try:
    import openpyxl
except ImportError:
    openpyxl = None

IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
UNRAR = r"C:/Program Files/WinRAR/UnRAR.exe"

# ---------------------------------------------------------------- utilitas

def human(n):
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024 or u == "GB":
            return f"{n:.1f}{u}"
        n /= 1024


def md5(path, chunk=1 << 20):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def dhash(path, size=8):
    """Perceptual hash 64-bit; jarak Hamming <= 4 dianggap near-duplicate.
    draft() memaksa JPEG decode langsung ke skala kecil (>> lebih cepat)."""
    img = Image.open(path)
    img.draft("L", (size + 1, size))
    img = img.convert("L").resize((size + 1, size), Image.LANCZOS)
    px = list(img.getdata())
    img.close()
    bits = 0
    for r in range(size):
        row = px[r * (size + 1):(r + 1) * (size + 1)]
        for c in range(size):
            bits = (bits << 1) | (row[c] < row[c + 1])
    return bits


def hamming(a, b):
    return bin(a ^ b).count("1")


def collect(root):
    return sorted(p for p in Path(root).rglob("*") if p.suffix.lower() in IMG_EXT and p.is_file())


def image_stats(files):
    ok, bad, fmts, w, h, total = 0, [], Counter(), [], [], 0
    for p in files:
        total += p.stat().st_size
        if Image is None:
            continue
        try:
            with Image.open(p) as im:
                im.verify()
            with Image.open(p) as im:
                fmts[im.format] += 1
                w.append(im.width)
                h.append(im.height)
            ok += 1
        except Exception as e:                       # noqa: BLE001
            bad.append((str(p), f"{type(e).__name__}: {e}"))
    st = {"n_file": len(files), "n_openable": ok, "n_corrupt": len(bad),
          "formats": dict(fmts), "bytes": total, "bytes_human": human(total)}
    if w:
        w.sort(); h.sort()
        st.update(w_min=w[0], w_med=w[len(w) // 2], w_max=w[-1], h_min=h[0], h_med=h[len(h) // 2], h_max=h[-1],
                  w_mean=round(sum(w) / len(w), 1), h_mean=round(sum(h) / len(h), 1))
    if bad:
        st["corrupt_examples"] = bad[:5]
    return st


def read_data_yaml(path):
    """Parser data.yaml minimal (tanpa PyYAML): names + train/val."""
    names, path_key, train, val = {}, None, None, None
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if s.startswith("path:"):
            path_key = s.split(":", 1)[1].strip()
        elif s.startswith("train:"):
            train = s.split(":", 1)[1].strip()
        elif s.startswith("val:"):
            val = s.split(":", 1)[1].strip()
        elif s and s[0].isdigit() and ":" in s:
            names[int(s.split(":", 1)[0])] = s.split(":", 1)[1].strip()
    return {"names": names, "path": path_key, "train": train, "val": val}


def audit_yolo(root):
    """Audit label YOLO (cls cx cy w h) + validitas box."""
    root = Path(root)
    classes = {}
    for y in root.rglob("data.yaml"):
        classes = read_data_yaml(y)["names"]
    out = {"classes": classes, "by_split": {}, "obj_per_class": Counter(), "img_per_class": Counter(),
           "invalid": [], "empty_label_files": 0, "n_label_files": 0, "n_objects": 0, "rows": []}
    for lab_dir in root.rglob("labels"):
        if not lab_dir.is_dir():
            continue
        split = lab_dir.parent.name
        n_img = len(collect(lab_dir.parent / "images")) if (lab_dir.parent / "images").is_dir() else 0
        n_lab = n_obj = 0
        for f in sorted(lab_dir.rglob("*.txt")):
            n_lab += 1
            lines = [l for l in f.read_text(errors="replace").splitlines() if l.strip()]
            if not lines:
                out["empty_label_files"] += 1
            present = set()
            for ln in lines:
                parts = ln.split()
                if len(parts) != 5:
                    out["invalid"].append((str(f), "bukan 5 kolom", ln))
                    continue
                try:
                    c = int(float(parts[0])); x, y, w, h = map(float, parts[1:])
                except ValueError:
                    out["invalid"].append((str(f), "nilai bukan angka", ln))
                    continue
                if not (0 <= x <= 1 and 0 <= y <= 1) or w <= 0 or h <= 0 or w > 1 or h > 1:
                    out["invalid"].append((str(f), "koordinat/ukuran di luar batas", ln))
                    continue
                if x - w / 2 < -1e-6 or y - h / 2 < -1e-6 or x + w / 2 > 1 + 1e-6 or y + h / 2 > 1 + 1e-6:
                    out["invalid"].append((str(f), "box keluar kanvas", ln))
                    continue
                if classes and c not in classes:
                    out["invalid"].append((str(f), f"class id {c} tidak ada di data.yaml", ln))
                    continue
                n_obj += 1
                out["obj_per_class"][c] += 1
                present.add(c)
            for c in present:
                out["img_per_class"][c] += 1
        out["by_split"][split] = {"n_images": n_img, "n_label_files": n_lab, "n_objects": n_obj}
        out["n_label_files"] += n_lab
        out["n_objects"] += n_obj
    return out


def audit_mask_pairs(img_dir, mask_dir):
    """Dataset archive: images + labels berupa masker JPG. Hitung rasio piksel objek."""
    imgs = collect(img_dir)
    masks = collect(mask_dir)
    stems_i = {p.stem: p for p in imgs}
    stems_m = {p.stem: p for p in masks}
    paired = sorted(set(stems_i) & set(stems_m))
    res = {"n_images": len(imgs), "n_masks": len(masks), "n_paired": len(paired),
           "images_without_mask": len(set(stems_i) - set(stems_m)),
           "masks_without_image": len(set(stems_m) - set(stems_i)), "mask_area_ratio": None}
    if Image and paired:
        ratios, sizes = [], Counter()
        for s in paired[:400]:                       # sampel maks 400 (cukup, hindari I/O besar)
            with Image.open(stems_m[s]) as m:
                sizes[m.size] += 1
                px = m.convert("L").getdata()
                ratios.append(sum(1 for v in px if v > 127) / max(1, len(px)))
        res["mask_area_ratio"] = {"n_sampled": len(ratios), "min": round(min(ratios), 4),
                                  "mean": round(sum(ratios) / len(ratios), 4), "max": round(max(ratios), 4),
                                  "mask_sizes": {f"{k[0]}x{k[1]}": v for k, v in sizes.items()}}
    return res


def xlsx_headers(path):
    if not openpyxl:
        return None
    wb = openpyxl.load_workbook(path, read_only=True)
    ws = wb[wb.sheetnames[0]]
    hdr = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    nrow = ws.max_row
    wb.close()
    return {"sheet": wb.sheetnames[0], "n_rows": nrow - 1, "n_cols": len(hdr), "columns": hdr}


# ---------------------------------------------------------------- ekstraksi arsip

def ensure_extracted(archive, cache, do_extract):
    """Ekstrak .rar/.zip sekali ke cache; kembalikan (dir, info) atau (None, info)."""
    archive = Path(archive)
    target = Path(cache) / archive.stem.replace(" ", "_")
    if target.is_dir() and any(target.iterdir()):
        return target, {"status": "cached"}
    if not do_extract:
        info = {"status": "not_extracted"}
        if archive.suffix.lower() == ".rar" and Path(UNRAR).exists():
            r = subprocess.run([UNRAR, "lb", str(archive)], capture_output=True, text=True, errors="replace")
            info["n_entries"] = len([l for l in r.stdout.splitlines() if l.strip()])
        return None, info
    target.mkdir(parents=True, exist_ok=True)
    if archive.suffix.lower() == ".rar":
        subprocess.run([UNRAR, "x", "-ibck", "-y", str(archive), str(target)], check=True,
                       capture_output=True)
    else:
        with zipfile.ZipFile(archive) as z:
            z.extractall(target)
    return target, {"status": "extracted"}


# ---------------------------------------------------------------- audit per dataset

def summarize(root, name):
    files = collect(root)
    st = image_stats(files)
    st.update(dataset=name, root=str(root), hashes=None)
    return files, st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=r"C:/Kuliah/Tingkat 3/PCVK/Project/Datasets")
    ap.add_argument("--out", default=r"C:/Kuliah/Tingkat 3/PCVK/Project/Analysis")
    ap.add_argument("--cache", default=os.path.join(os.environ.get("LOCALAPPDATA", "."), "hermes", "cache", "pcvk-audit"))
    ap.add_argument("--extract", action="store_true", help="ekstrak .rar/.zip ke cache bila belum ada")
    args = ap.parse_args()

    root, out = Path(args.root), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rep = {"generated_by": Path(__file__).name, "root": str(root), "datasets": {}}
    if Image is None:
        rep["warning"] = "Pillow tidak tersedia: resolusi/validitas gambar dilewati"

    # ---------- 1. archive: 1478 citra + 1478 masker (dataset publik Ulusoy et al.)
    arc = root / "archive"
    if arc.is_dir():
        files, st = summarize(arc, "archive (public PR dataset, segmentation masks)")
        st["masks"] = {}
        for split in ("Train", "Test"):
            img_d = arc / split / f"{split} Images v2"
            msk_d = arc / split / f"{split} Labels v2"
            if img_d.is_dir():
                st["masks"][split] = audit_mask_pairs(img_d, msk_d)
        feat = {}
        for x in arc.glob("*.xlsx"):
            h = xlsx_headers(x)
            if h:
                feat[x.name] = h
        st["feature_tables"] = feat
        st["hashes"] = None
        rep["datasets"]["archive"] = st

    # ---------- 2. ExAn-MTM (rar, YOLO)
    ex = root / "Expert Annotated Mandibular Third Molar (ExAn-MTM)"
    if ex.is_dir():
        st = {"dataset": "ExAn-MTM (expert annotated)"}
        d = ex if collect(ex) else ensure_extracted(next(ex.rglob("*.rar"), None), args.cache, args.extract)[0]
        if d:
            files = collect(d)
            st.update(image_stats(files))
            st["yolo"] = audit_yolo(d)
            rep["datasets"]["exan_mtm"] = st
            _hash_dataset(files, rep, "exan_mtm", st)
        else:
            rep["datasets"]["exan_mtm"] = st

    # ---------- 3. m-TM (rar, folder = kategori sisi L/R x impacted +/-, nama file cateN-)
    mt = root / "Mandibular Third Molar (m-TM) Dataset"
    if mt.is_dir():
        st = {"dataset": "m-TM"}
        d = mt if collect(mt) else ensure_extracted(next(mt.rglob("*.rar"), None), args.cache, args.extract)[0]
        if d:
            files = collect(d)
            st.update(image_stats(files))
            by_folder, by_cate = Counter(), Counter()
            for p in files:
                by_folder[p.parent.name] += 1
                stem = p.stem
                by_cate[stem.split("-")[0] if "-" in stem else "?"] += 1
            st["by_folder"] = dict(by_folder)
            st["by_cate_prefix"] = dict(sorted(by_cate.items(), key=lambda kv: (len(kv[0]), kv[0])))
            rep["datasets"]["mtm"] = st
            _hash_dataset(files, rep, "mtm", st)
        else:
            rep["datasets"]["mtm"] = st

    # ---------- 4. Multi-Label (label YOLO saja; citra tidak disertakan di dalam arsip)
    ml = root / "Multi-Label Classification and Detection of Third"
    if ml.is_dir():
        st = {"dataset": "Multi-Label Classification and Detection of Third Molar Impaction",
              "n_images_local": len(collect(ml)), "subsets": {}}
        for subset in sorted({p.parent for p in ml.rglob("train.txt")}):
            names = read_data_yaml(subset / "data.yaml")["names"] if (subset / "data.yaml").exists() else {}
            listed, obj, img = 0, Counter(), Counter()
            lab_dir = subset / "labels" / "train"
            for ln in (subset / "train.txt").read_text(errors="replace").splitlines():
                if not ln.strip():
                    continue
                listed += 1
                lf = lab_dir / (Path(ln.strip()).stem + ".txt")
                if not lf.exists():
                    continue
                present = set()
                for row in lf.read_text(errors="replace").splitlines():
                    parts = row.split()
                    if len(parts) == 5:
                        c = int(float(parts[0]))
                        obj[c] += 1
                        present.add(c)
                for c in present:
                    img[c] += 1
            st["subsets"][subset.name] = {
                "classes": names, "listed_images": listed,
                "label_files": len(list(lab_dir.glob("*.txt"))) if lab_dir.is_dir() else 0,
                "n_objects": sum(obj.values()),
                "obj_per_class": {names.get(c, str(c)): n for c, n in sorted(obj.items())},
                "img_per_class": {names.get(c, str(c)): n for c, n in sorted(img.items())},
                "images_present": len(collect(subset)),
            }
        st["yolo"] = {
            "classes": next(iter(st["subsets"].values()))["classes"] if st["subsets"] else {},
            "obj_per_class": Counter(), "img_per_class": Counter(), "invalid": [],
            "n_objects": sum(s["n_objects"] for s in st["subsets"].values()),
            "n_label_files": sum(s["label_files"] for s in st["subsets"].values()),
            "by_split": "labels train-only (gambar tidak disertakan)",
        }
        for s in st["subsets"].values():
            for k_, v_ in s["obj_per_class"].items():
                st["yolo"]["obj_per_class"][k_] += v_
            for k_, v_ in s["img_per_class"].items():
                st["yolo"]["img_per_class"][k_] += v_
        rep["datasets"]["multilabel"] = st

    # ---------- 5. duplikasi exact & near (antar dataset)
    rep["duplicates"] = _dup_report(root, rep)

    (out / "audit_raw.json").write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_csv(rep, out)
    _print_summary(rep)
    print(f"\n[saved] {out/'audit_raw.json'}\n[saved] {out/'03_Audit_Dataset.csv'}\n[saved] {out/'04_Distribusi_Kelas.csv'}")


_HASH_CACHE = {}


def _hash_dataset(files, rep, key, st):
    """MD5 seluruh file + dHash untuk deteksi duplikasi.""" 
    md5s, dhs = {}, {}
    for p in files:
        try:
            m = md5(p)
            md5s.setdefault(m, []).append(str(p))
            if Image:
                dhs[str(p)] = dhash(p)
        except Exception:                             # noqa: BLE001
            continue
    st["n_unique_md5"] = len(md5s)
    st["n_duplicate_files"] = sum(len(v) - 1 for v in md5s.values())
    _HASH_CACHE[key] = {"md5": md5s, "dhash": dhs, "files": [str(p) for p in files]}


def _dup_report(root, rep):
    keys = [k for k in ("exan_mtm", "mtm") if k in _HASH_CACHE]
    out = {"exact_md5_shared_between": {}, "near_dup_within": {}, "near_dup_between": {}}
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            shared = set(_HASH_CACHE[a]["md5"]) & set(_HASH_CACHE[b]["md5"])
            out["exact_md5_shared_between"][f"{a}~{b}"] = {
                "n_shared_files": sum(len(_HASH_CACHE[a]["md5"][h]) for h in shared),
                "n_shared_names": len({Path(_HASH_CACHE[a]["md5"][h][0]).name for h in shared}),
                "examples": [Path(_HASH_CACHE[a]["md5"][h][0]).name for h in list(shared)[:5]],
            }
    for k in keys:
        groups = defaultdict(list)
        for p, h in _HASH_CACHE[k]["dhash"].items():
            groups[h].append(p)
        uniq = sorted(groups)
        near = 0
        for i, h1 in enumerate(uniq):
            for h2 in uniq[i + 1:]:
                if hamming(h1, h2) <= 2:
                    near += len(groups[h1]) * len(groups[h2])
        out["near_dup_within"][k] = {"n_files": sum(len(v) for v in groups.values()),
                                     "n_unique_dhash": len(uniq), "n_near_dup_pairs": near}
    return out


KNOWN_CLASSES = {"exan_mtm": {0: "e-MTM (erupted)", 1: "i-MTM (impacted)"}}


def _write_csv(rep, out):
    rows = []
    for k, d in rep["datasets"].items():
        cls = ""
        if "yolo" in d:
            names = dict(d["yolo"]["classes"]) or KNOWN_CLASSES.get(k, {})
            cls = "; ".join(f"{i}:{n.strip()}" for i, n in sorted(names.items()))
        n_img = d.get("n_file", d.get("n_images_local", ""))
        if k == "multilabel":
            n_img = f"0 (hanya label; {d.get('n_images_local', 0)} gambar contoh di folder Code)"
        rows.append({
            "dataset": d.get("dataset", k), "n_images": n_img,
            "n_openable": d.get("n_openable", ""), "n_corrupt": d.get("n_corrupt", ""),
            "n_objects": d.get("yolo", {}).get("n_objects", ""),
            "n_label_files": d.get("yolo", {}).get("n_label_files", ""),
            "resolusi_min": f"{d.get('w_min','')}x{d.get('h_min','')}", "resolusi_maks": f"{d.get('w_max','')}x{d.get('h_max','')}",
            "ukuran": d.get("bytes_human", ""), "format": ";".join(d.get("formats", {}) or {}),
            "kelas": cls, "bbox_valid": d.get("yolo", {}).get("n_objects", ""),
            "bbox_invalid": len(d.get("yolo", {}).get("invalid", [])) if "yolo" in d else "",
        })
    with open(out / "03_Audit_Dataset.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

    # distribusi kelas
    d_rows = []
    for k, d in rep["datasets"].items():
        if "yolo" in d:
            names = dict(d["yolo"]["classes"]) or KNOWN_CLASSES.get(k, {})
            obj, img = d["yolo"]["obj_per_class"], d["yolo"]["img_per_class"]
            tot_o, tot_i = sum(obj.values()), sum(img.values())
            for c in sorted(set(list(obj) + list(img))):
                ne = obj.get(c, 0)
                ni = img.get(c, 0)
                d_rows.append({"dataset": d.get("dataset", k), "class_id": c,
                               "class_name": names.get(c) or (c if isinstance(c, str) else "?"), "n_objek": ne, "n_citra": ni,
                               "pct_objek": round(100 * ne / tot_o, 2) if tot_o else "",
                               "pct_citra": round(100 * ni / tot_i, 2) if tot_i else ""})
        if k == "mtm":
            names = {"m-M3(L+, R+)": "impacted both sides", "m-M3(L-, R+)": "impacted right only",
                     "m-M3(L+, R-)": "impacted left only", "m-M3(L-, R-)": "no impaction"}
            tot = sum(d["by_folder"].values())
            for f_, n in sorted(d["by_folder"].items(), key=lambda kv: -kv[1]):
                d_rows.append({"dataset": d["dataset"], "class_id": f_, "class_name": names.get(f_, f_),
                               "n_objek": "", "n_citra": n, "pct_objek": "",
                               "pct_citra": round(100 * n / tot, 2)})
        if k == "archive" and d.get("masks"):
            for split, m in d["masks"].items():
                d_rows.append({"dataset": f"archive/{split}", "class_id": "", "class_name": "M3M & IAC (masker semantik)",
                               "n_objek": m["n_masks"], "n_citra": m["n_images"], "pct_objek": "", "pct_citra": ""})
    if d_rows:
        with open(out / "04_Distribusi_Kelas.csv", "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(d_rows[0]))
            w.writeheader(); w.writerows(d_rows)


def _print_summary(rep):
    print("=" * 78)
    for k, d in rep["datasets"].items():
        print(f"\n## {d.get('dataset', k)}")
        for kk in ("n_file", "n_openable", "n_corrupt", "bytes_human", "w_min", "w_med", "w_max",
                   "h_min", "h_med", "h_max", "n_unique_md5", "n_duplicate_files",
                   "by_folder", "by_cate_prefix", "masks", "feature_tables", "archive", "n_images_local"):
            if kk in d and d[kk] not in ("", None, {}):
                print(f"   {kk}: {d[kk]}")
        if "yolo" in d:
            y = d["yolo"]
            print(f"   yolo: files={y.get('n_label_files')} objects={y.get('n_objects')} "
                  f"invalid={len(y.get('invalid', []))} empty={y.get('empty_label_files', '-')} splits={y.get('by_split')}")
            print(f"   kelas: {y.get('classes')}")
            print(f"   objek/kelas: {dict(y.get('obj_per_class', {}))}")
        if "subsets" in d:
            for s, v in d["subsets"].items():
                print(f"   subset {s}: img={v['images_present']} listed={v['listed_images']} "
                      f"labelfiles={v['label_files']} obj={v['n_objects']}")
                print(f"      kelas: {v['classes']}")
                print(f"      objek/kelas: {v['obj_per_class']}")
                print(f"      citra/kelas: {v['img_per_class']}")
    print("\n## Duplikasi")
    print(json.dumps(rep["duplicates"], indent=2, ensure_ascii=False)[:2000])


if __name__ == "__main__":
    sys.exit(main())