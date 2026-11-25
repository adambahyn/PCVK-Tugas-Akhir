# PCVK — Tugas Akhir

Deteksi dan klasifikasi posisi impaksi molar ketiga mandibula pada radiograf panoramik.
Mata kuliah Pengolahan Citra dan Visi Komputer (PCVK), JTI Polinema.

**Prototipe penelitian dan alat bantu edukasi — bukan alat diagnosis medis.**

## Isi repo

```
Analysis/
  01_Laporan_Audit.md          audit 7 artikel + audit dataset (6 fase)
  02_Matriks_Artikel.csv       matriks artikel + verdict fitur + lolos 4 besar
  03_Audit_Dataset.csv         hitung ulang per dataset (citra, objek, duplikat, lisensi)
  04_Distribusi_Kelas.csv      distribusi objek per kelas
  05_Rencana_Pipeline.md       rencana pipeline Tahap 1 & 2
  06_Audit_Dataset.py          skrip audit read-only (jalankan ulang kapan saja)
  07_Sumber_Terverifikasi.md   7 DOI + status lisensi + yang belum terverifikasi
  audit_raw.json               keluaran mentah audit
  run.log                      log run final (rc=0)
  Studi_Literatur_PCVK_Terisi.docx  dokumen studi literatur lengkap (Tabel A + Tabel 1–8 + diagram + narasi)
  build/                       skrip pembuat diagram & dokumen (mkdiagram2.py, mkdocx.py)
Journal/                       PDF artikel terpilih (4 dipakai, 3 di _tidak_dipakai/)
```

## Artikel acuan

| Kode | Artikel | DOI |
|---|---|---|
| A1 | Khurshid dkk. 2026, Int Dent J 76:109430 | 10.1016/j.identj.2026.109430 |
| A2 | Ulusoy dkk. 2025, Sci Rep 15:4178 | 10.1038/s41598-024-82915-5 |
| A3 | Kandagal dkk. 2025, JOMOS 31:7 | 10.1051/mbcb/2025008 |
| A4 | Ateş dkk. 2025, Healthcare 13:2904 | 10.3390/healthcare13222904 |

## Dataset

**Tidak disertakan di repo.** Total 899 MB, dua arsip >95 MB (batas GitHub 100 MB/file), dan lisensi
CC BY-NC-ND / CC BY-NC-SA melarang redistribusi.

| Dataset | Isi | Lisensi | Sumber |
|---|---|---|---|
| ExAn-MTM | 973 citra, 1.784 objek, label YOLO 2 kelas (i-MTM/e-MTM) | CC BY-NC-ND | Mendeley Data |
| m-TM | 1.317 citra; ExAn-MTM adalah subset-nya (973/973 identik MD5) | CC BY-NC-SA | Mendeley Data |
| Khurshid (rencana Tahap 2) | 5.796 OPG, 6 kelas sudut Winter | CC BY 4.0 | 10.17632/ckt876jzr6.1 |

Letakkan hasil unduhan di `Datasets/` (sudah masuk `.gitignore`), lalu:

```bash
python Analysis/06_Audit_Dataset.py
```

## Angka kunci hasil audit

- ExAn-MTM: 973 citra, 1.991×1.127 px, 0 rusak, 3 duplikat MD5, 0 label tidak valid
- Objek: i-MTM 1.097 (61,5%), e-MTM 687 (38,5%)
- **Kebocoran:** ExAn-MTM ⊂ m-TM (973 citra identik MD5) → tidak boleh dipakai sebagai train dan test sekaligus;
  uji eksternal hanya 344 citra unik
- Tahap 2 Winter 4 kelas belum tersedia di data lokal → pakai dataset Khurshid atau anotasi manual 300–500 citra (2 anotator + κ)

## Rencana pipeline

1. **Tahap 1 — deteksi ROI:** YOLOv8n/YOLOv11n, input 1.024 px, augmentasi ringan (mosaic off 10 epoch akhir)
2. **Tahap 2 — klasifikasi:** dua jalur fitur pada ROI hasil deteksi
   - handcrafted: sudut Winter M3–M2, rasio geometri, GLCM, intensitas akar → seleksi chi-square/ANOVA
   - deep: embedding ResNet50 (pembanding)
   - pengklasifikasi: SVM-RBF, Random Forest, ANN-MLP (pembanding)
3. **Evaluasi:** accuracy, macro-F1, F1 per kelas, confusion matrix, 95% CI bootstrap; mAP@0.5 & mAP@0.5:0.95 untuk deteksi

Detail: `Analysis/05_Rencana_Pipeline.md`.