# Laporan Santai: Pipeline Deteksi & Klasifikasi Impaksi Gigi Bungsu

Dokumen ini untuk dibaca anggota kelompok sendiri. Bahasa dibuat sederhana, tanpa istilah rumit. Semua angka di sini diambil dari `Pipeline/outputs/metrics.json` dan `Pipeline/outputs/confusion_matrix.json`, jadi tidak ada angka karangan.

---

## 1. Singkatnya, kita bikin apa?

Kita bikin program yang kerjanya seperti asisten radiolog:

1. Lihat foto rontgen gigi (foto panoramik seluruh rahang).
2. Tunjuk lokasi gigi bungsu yang tumbuh miring (impaksi) — pakai kotak.
3. Lihat potongan gambar di dalam kotak, lalu tebak jenisnya: **e-MTM** atau **i-MTM**.

Ibaratnya begini. Detektor itu seperti orang pakai kacamata lalu menunjuk: "giginya di sini". Klasifikasi itu seperti orang mengamati lebih dekat lalu bilang: "ini jenis A atau jenis B".

Kalau satu langkah saja, komputer harus menjawab dua hal sekaligus dan sering salah. Kalau dipecah dua langkah, masing-masing lebih mudah dan lebih gampang dicek.

---

## 2. Data yang kita pakai

- 973 foto rontgen panoramik.
- Di dalamnya ada 1.784 gigi bungsu.
- 687 gigi kelas **e-MTM**, 1.097 gigi kelas **i-MTM**.
- Dibagi jadi dua bagian: **875 foto untuk belajar** (1.604 gigi), **98 foto untuk ujian** (180 gigi).
- Datanya bukan dari pasien kita. Ini dataset publik ExAn-MTM dari Mendeley Data. Lisensinya hanya boleh untuk riset dan pembelajaran, tidak boleh dijual atau disebar ulang.

Satu foto bisa berisi lebih dari satu gigi. Rata-rata 1,8 gigi per foto.

---

## 3. Cara kerjanya

**Langkah 1 — Detektor (YOLO11n).** Komputer melihat foto utuh dan mengeluarkan kotak untuk setiap gigi bungsu, plus angka keyakinan (0 sampai 1).

**Langkah 2 — Potong.** Setiap kotak dipotong jadi gambar kecil, lalu dirapikan ke ukuran 96×96 piksel.

**Langkah 3 — Penebak jenis.** Ada dua cara yang kita coba:

- Cara A: gambar kecil dimasukkan ke jaringan ResNet-18 yang sudah pintar (hasil latihan jutaan foto biasa), lalu diambil "ringkasannya" berupa 512 angka. Dari 512 angka itu, dua penebak sederhana menebak kelasnya: **Logistic Regression** dan **KNN**.
- Cara B: CNN kecil (jaringan saraf sederhana) dilatih dari nol khusus untuk tugas ini.

Cara A seperti meminjam mata orang yang sudah berpengalaman, lalu kita cuma belajar membedakan dua jenis. Cara B seperti mengajari anak dari nol dengan contoh yang sedikit.

---

## 4. Hasil detektor, dan artinya dalam bahasa sehari-hari

| Angka | Nilainya | Artinya kalau diomongin ke orang awam |
|---|---|---|
| mAP@0.5 | 0,985 | Dari 100 gigi, sekitar 98–99 kotaknya kena. Kotak boleh sedikit bergeser. |
| mAP@0.5:0.95 | 0,602 | Kalau kotaknya harus rapi sekali, baru sekitar 60%. Jadi lokasi sudah ketemu, tapi kotaknya masih agak longgar. |
| Precision | 0,946 | Dari 100 kali komputer bilang "ada gigi", sekitar 95 benar-benar ada gigi. |
| Recall | 0,961 | Dari 100 gigi yang benar-benar ada, sekitar 96 berhasil ditemukan. Sisanya kelewat. |

Angka per kelas (dari sumber yang sama):

| Kelas | Precision | Recall | F1 | mAP@0.5 |
|---|---|---|---|---|
| e-MTM | 0,895 | 0,948 | 0,921 | 0,975 |
| i-MTM | 0,996 | 0,974 | 0,985 | 0,995 |

Bacanya: **i-MTM jauh lebih gampang dikenali** (precision hampir sempurna). **e-MTM lebih sering salah** — wajar, karena gigi yang sebagian sudah keluar kadang mirip gigi biasa, dan batas kotaknya tidak jelas.

---

## 5. Kotak benar dan salah (confusion matrix), dibaca pelan

Baris = jawaban asli (ground truth). Kolom = tebakan komputer. Ini dihitung dengan aturan: kotak dianggap benar kalau tumpang tindihnya (IoU) minimal 0,5, dan hanya kotak dengan keyakinan ≥ 0,25 yang dihitung.

| Asli ＼ Tebakan | e-MTM | i-MTM | tidak ada |
|---|---|---|---|
| **e-MTM (63)** | 61 | 3 | 2 |
| **i-MTM (117)** | 0 | 114 | 2 |
| **tidak ada** | 8 | 2 | 0 |

Cara baca satu per satu:

- **61** → gigi e-MTM, ditebak e-MTM. Benar.
- **3** → gigi e-MTM, ditebak i-MTM. Salah kelas.
- **2** → gigi e-MTM, komputer tidak menemukan kotaknya. Kelewat.
- **114** → gigi i-MTM, ditebak i-MTM. Benar.
- **2** → gigi i-MTM, komputer tidak menemukan kotaknya. Kelewat.
- **8 + 2** → di situ tidak ada gigi, tapi komputer membuat kotak. Ini "kotak hantu", biasanya karena bayangan, akar gigi lain, atau tepi rahang.
- **0** → tidak ada gigi i-MTM yang ditebak e-MTM.

Ringkasnya: **5 gigi kelewat** dari 180, dan **10 kotak hantu**. Sisanya benar.

Kalau angkanya terasa beda tipis dengan tabel di bagian 4, itu bukan salah hitung. Bagian 4 memakai aturan resmi penilaian deteksi (banyak ambang sekaligus), sedangkan tabel ini memakai satu aturan tetap (keyakinan 0,25, tumpang tindih 0,5) supaya bisa dihitung manual dan dicek ulang.

---

## 6. Hasil penebak jenis

| Model | Akurasi | Artinya |
|---|---|---|
| ResNet-18 + Logistic Regression | 0,939 | Dari 10 potongan gambar, sekitar 9,4 ditebak benar. |
| ResNet-18 + KNN (k=5) | 0,867 | Sekitar 8,7 dari 10. |
| CNN kecil dari nol | 0,865 | Sekitar 8,6 dari 10 (rata-rata 3 kali latihan ulang). |

Jadi **yang paling bagus: ResNet-18 + Logistic Regression** (macro-F1 0,933, AUC 0,974). CNN dari nol paling lemah, dan itu wajar: kita cuma punya 1.604 contoh latihan, sedangkan CNN biasanya butuh puluhan ribu.

Yang menarik: penebak jenis sederhana (Logistic Regression) mengalahkan jaringan saraf yang dilatih sendiri. Sebabnya, ResNet-18 sudah "melihat" jutaan gambar sebelumnya, jadi ringkasannya sudah bagus. Kita tinggal memakai ringkasan itu.

---

## 7. Kenapa angka kita beda dengan jurnal

- Jurnal acuan memakai 5.796 foto dan 5–6 kelas sudut. Kita 973 foto dan 2 kelas.
- Jurnal memakai GPU. Kita laptop CPU (Intel Core i3-1005G1, 1,20 GHz).
- Latihan kita 20 epoch dan butuh 98,8 menit. Jurnal biasanya 100 epoch ke atas.

Jadi **jangan bilang "hasil kita lebih bagus" atau "lebih buruk" dari jurnal**. Ujiannya beda. Yang boleh dikatakan: "dengan data jauh lebih sedikit dan komputer biasa, hasilnya masih masuk akal".

---

## 8. Yang masih lemah (jujur saja)

1. Ujian cuma 98 foto / 180 gigi. Angka bisa bergeser beberapa persen kalau datanya diganti.
2. Latihan cuma 20 epoch. Belum dicoba lebih lama.
3. Ukuran gambar 448 piksel, bukan 1.024 piksel seperti rencana awal — biar muat di CPU.
4. Label dibuat satu tim anotator. Belum ada pengecekan silang dua orang (kappa).
5. Ini prototipe penelitian dan alat bantu belajar. **Bukan alat diagnosis medis.**

Kalau ditanya "kok cuma segitu?", jawab saja: batasannya di komputer dan waktu, bukan di metode. Semua langkahnya sudah benar dan bisa diulang.

---

## 9. Kalau ditanya dosen, jawab begini

**Tanya: kenapa dua tahap, bukan satu model saja?**
Karena tugasnya beda. Deteksi menjawab "di mana", klasifikasi menjawab "jenis apa". Dipisah, tiap bagian bisa diperiksa dan diperbaiki sendiri.

**Tanya: kenapa YOLO11n?**
Model terkecil di keluarganya (2,6 juta parameter). Cukup akurat, dan satu-satunya yang realistis dijalankan di CPU laptop.

**Tanya: kenapa mAP@0.5 tinggi tapi mAP@0.5:0.95 rendah?**
Karena lokasi gigi sudah ketemu, tapi kotaknya belum rapi benar. Untuk sekadar menunjuk gigi, kotak longgar masih berguna. Untuk mengukur sudut gigi, belum cukup.

**Tanya: kenapa CNN kalah dari Logistic Regression?**
Data latihnya sedikit. CNN butuh banyak contoh untuk belajar dari nol. ResNet-18 sudah belajar dari jutaan gambar, jadi kita tinggal memakai hasilnya.

**Tanya: kenapa confusion matrix-nya beda dari tabel metrik?**
Beda aturan hitung. Tabel metrik memakai penilaian resmi deteksi; confusion matrix memakai satu ambang tetap supaya bisa dicek manual. Selain itu, matriks bawaan library ultralytics versi 8.4.218 keliru (jumlah barisnya tidak sama dengan jumlah gigi asli), jadi kita hitung ulang sendiri di `Pipeline/scripts/make_cm.py` dan hasilnya bisa diaudit.

**Tanya: batasannya apa?**
Jawab lima poin di bagian 8.

---

## 10. Filenya di mana

| File | Isinya |
|---|---|
| `Laporan/Laporan_Pipeline_Deteksi_Klasifikasi_Impaksi.docx` | laporan resmi (versi yang dikumpulkan) |
| `Laporan/Laporan_Pipeline_Deteksi_Klasifikasi_Impaksi.pdf` | laporan resmi versi PDF |
| `Laporan/Prompt_PPT_AI.md` | bahan untuk menyusun slide |
| `Pipeline/PCVK_Pipeline_Deteksi_Klasifikasi_Impaksi.ipynb` | notebook yang sudah dijalankan, semua hasil terlihat di dalamnya |
| `Pipeline/outputs/metrics.json` | semua angka mentah (sumber tunggal) |
| `Pipeline/outputs/confusion_matrix.json` | matriks benar/salah yang dipakai di bagian 5 |
| `Pipeline/outputs/figures/` | gambar-gambar untuk slide |
| `Pipeline/scripts/` | skrip: `make_cm.py` (hitung matriks), `build_laporan.py` (buat laporan) |

Cara buka notebook: kalau belum ada Jupyter, cukup lihat versi PDF laporan. Notebook butuh Python 3.12 dan beberapa pustaka; langkah pemasangannya ada di laporan resmi bagian metode.

---

## 11. Versi pendek untuk dikirim ke grup WA

> Kita bikin program dua tahap: (1) detektor YOLO11n menunjuk lokasi gigi bungsu di foto rontgen, (2) penebak jenis menentukan e-MTM atau i-MTM dari potongan gambarnya.
>
> Datanya 973 foto, 1.784 gigi, dibagi 875 foto untuk belajar dan 98 untuk ujian. Hasil deteksi: mAP@0.5 = 0,985 (kotak hampir selalu kena), tapi mAP@0.5:0.95 = 0,602 (kotaknya masih longgar kalau harus presisi). Dari 180 gigi ujian, 5 kelewat dan 10 kotak hantu.
>
> Penebak jenis terbaik: ResNet-18 + Logistic Regression, akurasi 0,939 (9,4 dari 10 benar). Yang paling lemah: CNN dari nol, 0,865, karena data latihnya sedikit.
>
> Semua dijalankan di laptop CPU, latihan 20 epoch, 98,8 menit. Jangan bandingkan langsung dengan jurnal (data dan komputernya beda). Ini prototipe riset, bukan alat medis.
