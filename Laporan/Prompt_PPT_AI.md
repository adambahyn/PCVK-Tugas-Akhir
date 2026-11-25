# Prompt pembuatan PPT (AI) — Hasil Pipeline Deteksi & Klasifikasi Impaksi M3B

> Cara pakai: salin seluruh blok "PROMPT UTAMA" ke tool AI presentasi (Gamma, Microsoft Copilot
> PowerPoint, Canva Magic Design, atau ChatGPT dengan Slides). Lampirkan file gambar dari
> `Pipeline/outputs/figures/` dan `Pipeline/outputs/metrics.json`.

---

## PROMPT UTAMA

Buat presentasi akademik berbahasa Indonesia, 14 slide, untuk coursework PCVK (Praktikum Pemrosesan
Citra dan Visi Komputer) berjudul **"Deteksi Lokasi dan Klasifikasi Impacted/Erupted Molar III Bawah
pada Radiografi Panoramik"**. Audiens: dosen pengampu dan fellow student. Gaya: formal, bersih,
minimalis, tanpa animasi berlebihan, warna tema biru-putih, ukuran judul minimal 28 pt.

**Aturan keras (WAJIB dipatuhi):**
1. Gunakan **hanya** angka yang tertulis di bawah. Jangan mengarang, menebak, atau
   "mempercantik" angka. Jika sebuah angka tidak tersedia, tulis **"Tidak dijelaskan"**.
2. Setiap slide yang memuat angka harus mencantumkan sumber di kaki slide
   (contoh: *Sumber: `Pipeline/outputs/metrics.json`*).
3. Jangan menyajikan angka eksperimen sebagai klaim klinis. Tulis disclaimer sekali di slide 2:
   "Angka merupakan hasil eksperimen pada dataset publik; bukan performa alat diagnostik dan bukan klaim klinis."
4. Jangan menambah referensi yang tidak ada di daftar. Gunakan hanya 4 entri di bawah.
5. Masukkan file gambar lokal (disertakan) dengan keterangan singkat di bawah slide.

### Data yang boleh dipakai (satu-satunya sumber angka)

**Dataset**
- ExAn-MTM (Mendeley Data, DOI 10.17632/t8k59p35p6.1, lisensi CC BY-NC-ND 4.0)
- Total 973 citra OPG; 1784 bounding box; e-MTM (erupted) 687 box; i-MTM (impacted) 1097 box
- Split resmi: train 875 citra / valid 98 citra
- Kelas: 0 = e-MTM (erupted), 1 = i-MTM (impacted)

**Deteksi lokasi — YOLO11n, imgsz 448, batch 8, 20 epoch, seed 42, CPU**
- Precision 0.9458 · Recall 0.9611 · mAP@0.5 0.9847 · mAP@0.5:0.95 0.6020
- Epoch terbaik: 20 dari 20 · waktu training 98.8 menit
- e-MTM: P 0.8951 · R 0.9479 · F1 0.9207 · mAP50 0.9745
- i-MTM: P 0.9964 · R 0.9744 · F1 0.9853 · mAP50 0.9948
- Confusion matrix (baris GT, kolom prediksi; urutan e-MTM, i-MTM, background):
    61    0    2
   3  114    0
   8    2    0

**Klasifikasi crop (96×96 px)**
- ResNet-18 frozen + Logistic Regression: akurasi 0.9389, macro-F1 0.9326, ROC-AUC 0.9742, CI95 [0.9000, 0.9722]
- ResNet-18 frozen + KNN(k=5): akurasi 0.8667, macro-F1 0.8460, ROC-AUC 0.9267, CI95 [0.8167, 0.9111]
- CNN kecil, 3 seed [42, 1337, 2024]: akurasi 0.8648 ± 0.0189 (rentang 0.8389–0.8833), macro-F1 0.8543 ± 0.0149

**Perbandingan dengan baseline paper**
- Khurshid et al. (2026): 5.796 OPG; ResNet50+Fine KNN 97,56% (test); YOLOv11n mAP@0.5:0.95 85,7%; κ = 0,92; split 1.796/2.000/2.000
- Perbedaan setup: corpus 973 vs 5.796 OPG; kelas 2 vs 5+6; CPU vs GPU — **tidak boleh** disimpulkan lebih buruk secara langsung

### Struktur slide yang diminta

1. **Judul** — judul coursework, nama kelompok (isi sendiri), mata kuliah, tanggal.
2. **Disclaimer & tujuan** — disclaimer di atas + tujuan pipeline (deteksi lokasi + klasifikasi impacted/erupted).
3. **Latar belakang** — M3B impacted pada panoramik; importance untuk next step (angulasi Winter/Adams–Lunt).
4. **Tujuan & ruang lingkup** — 3 tujuan pipeline + batasan (CPU-only, dataset 973 OPG, angulasi belum dijalankan).
5. **Dataset** — tabel split & distribusi kelas + gambar `fig_audit_kelas.png`.
6. **Baseline paper** — tabel 3 paper + peran masing-masing + catatan angka E-MTMYOLO/mTMCNN "Tidak dijelaskan".
7. **Arsitektur pipeline** — diagram alur 5 tahap (audit → deteksi YOLO11n → crop → klasifikasi → ringkasan).
8. **Tahap deteksi: konfigurasi** — model, imgsz, epoch, batch, seed, device CPU; gambar `fig_kurva_training_deteksi.png`.
9. **Hasil deteksi** — tabel metrik overall + per kelas + `fig_pr_deteksi.png`.
10. **Confusion matrix deteksi** — gambar `fig_confusion_deteksi.png` + interpretasi singkat (tanpa klaim klinis).
11. **Tahap klasifikasi** — tabel 3 model + gambar `fig_klasifikasi_cnn.png`; tekankan variasi antar-seed.
12. **Demo end-to-end** — gambar `fig_end_to_end.png` + penjelasan warna kotak (hijau e-MTM, merah i-MTM).
13. **Pembahasan & batasan** — tabel batasan (7 baris) + posisi terhadap baseline paper.
14. **Kesimpulan & lanjutan** — 3 kesimpulan + rencana penyambungan klasifikasi angulasi 6 kelas (Winter) + daftar pustaka ringkas.

### Referensi (hanya yang ini boleh dipakai)
- Kayadibi, İ., Köse, U., Güraksın, G. E., & Çetin, B. (2025). E-MTMYOLO. *The Journal of Supercomputing*, 81(13), 1286. https://doi.org/10.1007/s11227-025-07775-w
- Kayadibi, İ., Köse, U., Güraksın, G. E., & Çetin, B. (2025). *Expert Annotated Mandibular Third Molar (ExAn-MTM) Dataset* [Data set]. Mendeley Data. https://doi.org/10.17632/t8k59p35p6.1
- Kayadibi, İ., Köse, U., Güraksın, G. E., & Çetin, B. (2025). An AI-assisted explainable mTMCNN architecture. *International Journal of Medical Informatics*, 195, 105724. https://doi.org/10.1016/j.ijmedinf.2024.105724
- Khurshid, Z., Alsleem, M. H., Aljubairah, F. A., Alghafli, H. A., Alasafirah, A. O., Alibrahim, B. A., Alshamrani, A. A., & Alsuhaymi, A. N. (2026). Dual framework for classification and detection of third molar impaction in panoramic radiographs. *International Dental Journal*, 76(2), 109430. https://doi.org/10.1016/j.identj.2026.109430

### File gambar yang dilampirkan (dari `Pipeline/outputs/figures/`)
- `fig_audit_kelas.png` — slide 5
- `fig_kurva_training_deteksi.png` — slide 8
- `fig_pr_deteksi.png` — slide 9
- `fig_confusion_deteksi.png` — slide 10
- `fig_klasifikasi_cnn.png` — slide 11
- `fig_end_to_end.png` — slide 12
- `fig_contoh_crop.png` — opsional slide 11

Output: file .pptx yang bisa diunduh, plus ringkasan singkat per slide (bullet) untuk disunting.

---

## CATATAN UNTUK PENGGUNA
- Angka di prompt ini diambil otomatis dari `Pipeline/outputs/metrics.json`; ubah pipeline → jalankan ulang
  `Pipeline/scripts/build_laporan.py` → prompt ikut ter-update.
- Kuartil jurnal (Q1/Q2) sengaja tidak dicantumkan: belum diverifikasi sumbernya.
