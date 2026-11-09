# 07 — Sumber Terverifikasi

Semua verifikasi dilakukan 9 November 2026 pada sumber primer (halaman DOI/penerbit atau API Mendeley), bukan dari nama file atau abstrak.

## Artikel
| # | DOI | Terverifikasi di | Status |
|---|---|---|---|
| 1 | 10.3390/app13179970 | MDPI Applied Sciences 13(15):9970 — https://doi.org/10.3390/app13179970 | Terbit, CC BY 4.0 |
| 2 | 10.1038/s41598-024-82915-5 | Scientific Reports 15:4178 — https://doi.org/10.1038/s41598-024-82915-5 | Terbit, CC BY-NC-ND 4.0 |
| 3 | 10.3390/healthcare13222904 | MDPI Healthcare 13(22):2904 — https://doi.org/10.3390/healthcare13222904 | Terbit, CC BY 4.0 |
| 4 | 10.1038/s41598-025-93783-y | Scientific Reports 15:23688 — https://doi.org/10.1038/s41598-025-93783-y | Terbit, CC BY-NC-ND 4.0 |
| 5 | 10.1016/j.identj.2026.109430 | International Dental Journal 76:109430 — https://doi.org/10.1016/j.identj.2026.109430 | Terbit, CC BY 4.0 |
| 6 | 10.1051/mbcb/2025008 | J Oral Med Oral Surg 31:7 — https://doi.org/10.1051/mbcb/2025008 | Terbit, CC BY 4.0 |
| 7 | — | IJPSAT 55(1):524–534, https://ijpsat.org/ (© 2026 Scholar AI LLC, ISSN 2509-0119) | **Tanpa DOI, tanpa bukti peer review** — tidak dipakai sebagai acuan utama |

## Dataset (metadata via `https://data.mendeley.com/public-api/datasets/<id>`)
| Dataset | DOI | Diterbitkan | Lisensi resmi (`data_licence`) | Berkas yang dirilis |
|---|---|---|---|---|
| ExAn-MTM | 10.17632/t8k59p35p6.1 | 2025-09-01 | **CC BY-NC-ND 4.0** | `ExAn-MTM dataset.rar` (148 MB) |
| m-TM | 10.17632/xn5bz6fdm6.1 | 2024-12-03 | **CC BY-NC-SA 4.0** | `m-TM dataset.rar` (201 MB) |
| Multi-Label | 10.17632/ckt876jzr6.1 | 2025-07-07 | **CC BY 4.0** | `Dataset (Labelled).zip` (45 KB), `Code and Features.zip` (71 MB), `Read Me.pdf` — **tanpa citra** |
| CONTACT (`archive`) | — | via artikel Sci Rep 15:4178 | CC BY-NC-ND 4.0 (artikel) | https://www.kaggle.com/datasets/tugcetoprak92/contact-dataset |

## Sumber turunan yang wajib disitasi bersama dataset
- Kayadibi İ., Köse U., Güraksın G.E. dkk. *E-MTMYOLO: an explainable YOLOv5-based architecture…* J Supercomput 81:1286 (2025). DOI 10.1007/s11227-025-07775-w — dataset ExAn-MTM.
- Kayadibi İ., Köse U., Güraksın G.E., Çetin B. *An AI-assisted explainable mTMCNN architecture…* Int J Med Inform 195:105724 (2025). DOI 10.1016/j.ijmedinf.2024.105724 — dataset m-TM & ExAn-MTM.
- Silva G., Oliveira L., Pithon M. *Automatic segmenting teeth in X-ray images…* Expert Systems with Applications 107:15–31 (2018) — asal data UESB (http://ivisionlab.ufba.br/).
- Khurshid Z. dkk. Int Dent J 76:109430 (2026) — dataset multi-label 10.17632/ckt876jzr6.1.
- Ulusoy A.C. dkk. Sci Rep 15:4178 (2025) — dataset CONTACT.

## Belum terverifikasi (harus diakui di laporan)
1. **Lisensi Kaggle CONTACT** — halaman Kaggle tidak dapat dibaca otomatis (butuh login/JS); yang terverifikasi hanya lisensi artikelnya (CC BY-NC-ND 4.0).
2. **Asal citra 5796 pada dataset multi-label** — artikel menyebut "publicly available… from the Mendeley dataset" dengan sitasi ref 22/23 yang tidak sesuai; tidak ada URL gambar. Jalur `data/images/train/*.png` tidak pernah dirilis.
3. **Arti prefix `cate1`–`cate10`** pada nama file m-TM — tidak ada dokumentasi; tidak berkorelasi bersih dengan folder sisi.
4. **`CD-1`…`CD-6`** pada `data.yaml` multi-label — akronim tidak dijelaskan di README/artikel; CD-6 tidak punya satu pun instance.
5. **Jumlah pasien** ExAn-MTM / m-TM — tidak dilaporkan pada deskripsi dataset.

## Perangkat audit (dapat dijalankan ulang)
```
cd "C:\Kuliah\Tingkat 3\PCVK\Project\Analysis"
"C:\Program Files\Python313\python.exe" -W ignore 06_Audit_Dataset.py
```
Output: `03_Audit_Dataset.csv`, `04_Distribusi_Kelas.csv`, `audit_raw.json`. Script read-only terhadap `Datasets/`.