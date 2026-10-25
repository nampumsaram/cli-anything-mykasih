# Semakan Data Barcode Terkini — MyKasih / SARA

**Tarikh semakan:** 25 Oktober 2026
**Sumber barcode terkini:** Lotuss Malaysia (katalog online, stok tersedia)
**Sumber kelayakan:** API MyKasih `saraforall-GetProductEligible`
**Sumber harga pembanding:** Mydin (Magento GraphQL)

---

## 1. Ringkasan eksekutif

| Item | Nilai |
|---|---|
| Produk Lotuss disemak | **13,391** |
| Barcode unik Lotuss | **15,852** |
| Barcode 13-digit | **14,866** |
| Barcode diuji melalui API MyKasih | **14,571** (13,728 × 13-digit + 843 × 8/12/14-digit) |
| Barcode **LAYAK** daripada imbasan baharu | **6,114** (5,903 × 13-digit) |
| Daripada itu, benar-benar baharu (tidak ada dalam data lama) | **5,989** |
| Jumlah barcode layak yang diketahui sekarang | **8,384** |
| Barcode layak dalam katalog Lotuss | **6,892 / 15,852 = 43.5%** |

**Penemuan utama:** korpus lama (Open Food Facts / Open Beauty Facts / Open Products Facts) hanya menguji 7,984 barcode dan menemui 2,395 layak. Katalog Lotuss yang terkini mengandungi **15,852 barcode**, dan selepas imbasan penuh, **6,892 barcode dalam katalog Lotuss sahaja disahkan layak** — hampir **3 kali ganda** angka lama. Ini bukan kerana peraturan SARA berubah, tetapi kerana korpus lama terlalu banyak makanan dan kurang produk kebersihan diri/rumah serta alat tulis.

---

## 2. Apa yang disemak

Fail zip `hcKM.zip` mengandungi 35 fail laporan MyKasih/SARA. Antaranya:

- `LAPORAN.md` — laporan versi 5, mendakwa 7,984 barcode diuji → 2,395 layak.
- `sara_products_checked.json` — **7,984** rekod (lengkap).
- `sara_products_checked.csv` — hanya **6,314** rekod (tidak lengkap; lihat §5.2).
- `sara_eligible_products.json` — 2,395 produk layak.
- `lookup_item.csv` — 798 item PriceCatcher (KPDN), **tiada lajur barcode**.

API MyKasih masih hidup dan responsnya sepadan dengan laporan lama. Contoh yang disahkan semula pada 25 Okt 2026:

```json
{"isEligible":true,
 "data":{"productName":"HARPIC PWR PLUS CITRUS 450ML",
         "productCategoryName":"Toilet Cleaner"},
 "success":true}
```

Ujian dengan lima `merchantID` berbeza memberi nama dan keputusan yang sama — jadi `merchantID` memang tidak mempengaruhi keputusan.

---

## 3. Sumber Malaysia: apa yang sebenarnya ada

| Laman | Data barcode? | Catatan |
|---|---|---|
| **Lotuss** (`shopping.lotuss.com.my`) | **Ya** | API carian produk mendedahkan array `barcodes`, harga, stok. **Sumber utama semakan ini.** |
| **FAMA** (`fama.gov.my`) | Tidak | “Harga Pasaran Terkini” ialah dashboard Power BI harga komoditi (per kg). Tiada katalog barcode. AgroBazaar pula jual hasil segar, bukan produk berbarcode. |
| **99 Speedmart** (`99speedmart.com.my`) | Tidak | Laman korporat; tiada katalog produk online. |
| **Mydin** (`mydin.my`) | Tidak | Ada katalog produk, tetapi `sku` ialah kod dalaman Mydin, bukan barcode GS1. Digunakan untuk semakan harga sahaja. |
| **PriceCatcher / MYIPM** (KPDN) | Tidak | 798 item harga harian di premis. `lookup_item.csv` dalam zip ialah senarai item ini — **tiada lajur barcode**. |
| **GS1** | Sebahagian | Hanya untuk semakan digit checksum, bukan paparan produk. |

**Kesimpulan:** daripada laman yang disebut, hanya **Lotuss** menyediakan data barcode produk yang boleh disahkan secara langsung. FAMA tidak boleh digunakan untuk semakan barcode.

### 3.1 Cara data Lotuss diambil

Carian produk Lotuss menggunakan API awam:

```
POST https://lotus-my-search.my-prod.siammakro.cloud/search/api/v1/indexes/products/search
{
  "q": "", "page": 1, "size": 100,
  "filters": {"countryCode":"MY","storeCodes":["5001"],"availability":true}
}
```

Setiap dokumen produk mengandungi `title`, `brand`, `barcodes[]`, `price`, `specialPrice`, `inStock`, `internalCategories`. Sebanyak 134 halaman (13,391 produk) diambil pada 25 Okt 2026.

---

## 4. Hasil imbasan kelayakan

### 4.1 Angka utama

| Kumpulan | Diuji | Layak | Kadar |
|---|---:|---:|---:|
| Barcode 13-digit Lotuss (baharu) | 13,728 | **5,903** | 43.0% |
| Barcode 8/12/14-digit Lotuss | 843 | **211** | 25.0% |
| **Jumlah imbasan baharu** | **14,571** | **6,114** | **42.0%** |
| Data lama (rujukan) | 7,984 | 2,395 | 30.0% |
| **Jumlah unik diketahui** | **22,348** | **8,384** | **37.5%** |

- **5,989** barcode layak adalah penemuan baharu (6,114 tolak 125 yang sudah ada dalam data lama).
- Dalam katalog Lotuss, **6,892 / 15,852 (43.5%)** barcode disahkan layak.
- **903** barcode layak lama masih ada dalam katalog Lotuss; **1,492** barcode layak lama tidak lagi disenaraikan (mungkin dijual di kedai lain atau tidak lagi dalam assortmen Lotuss).

### 4.2 Perbandingan kategori (data lama vs penemuan baharu)

| Kategori SARA | Data lama | Penemuan baharu (Lotuss) |
|---|---:|---:|
| Seasoning | 479 | 947 |
| Beverage | 573 | 829 |
| Body Wash | 49 | 761 |
| Frozen Food | 280 | 425 |
| **Detergent** | **1** | **380** |
| **Stationery** | **4** | **357** |
| **Oral Care** | **7** | **342** |
| **Sanitary Pad** | **4** | **292** |
| Noodles | 188 | 271 |
| Biscuit | 284 | 251 |
| Bread | 170 | 218 |
| **Shampoo** | **36** | **232** |
| Canned Food | 136 | 132 |
| Rice | 29 | 146 |
| Flour | 37 | 94 |
| **Dishwasher** | **2** | **127** |
| Medicine | 40 | 68 |
| Eggs | 52 | 45 |
| Cooking Oil | 22 | 58 |
| **Toilet Cleaner** | **4** | **69** |
| **Floor Cleaner** | **1** | **62** |
| Books | 0 | 7 |
| Uniform | 1 | 1 |

> Nota: angka “data lama” bagi Toilet Cleaner (4) datang daripada ujian probe berasingan dalam laporan lama, bukan daripada korpus 7,984. Sebab itu ia tidak muncul dalam `sara_products_checked.json`.

![Perbandingan kategori SARA](carta_kategori.png)

### 4.3 Jenama terbanyak (penemuan baharu)

| Jenama | Bilangan |
|---|---:|
| LOTUSS (house brand) | 342 |
| FABER CASTELL | 129 |
| NIVEA | 102 |
| ADABI | 94 |
| COLGATE | 82 |
| KOTEX | 64 |
| DETTOL | 63 |
| SAFI | 62 |
| DARLIE | 58 |
| STABILO | 54 |
| REXONA | 52 |
| TOP | 47 |
| SUNSILK | 46 |
| VALUE | 46 |
| PILOT | 46 |
| BREEZE | 44 |
| DAIA | 43 |
| NESTLE | 42 |
| ORAL B | 42 |

### 4.4 Contoh produk layak (harga Lotuss, 25 Okt 2026)

| Barcode | Produk | Kategori SARA | Harga |
|---|---|---|---:|
| 9556111997575 | Harpic Liq Powerplus Lavender 2×450ml | Toilet Cleaner | RM 8.89 |
| 8885010239457 | Fab Powder Cotton 2kg | Detergent | RM 12.99 |
| 9556126652964 | Sunlight Dishwash Lime 800ml | Dishwasher | RM 5.49 |
| 9555216584741 | Value Floor Cleaner 4L | Floor Cleaner | RM 9.25 |
| 9556111621203 | Dettol Body Wash Fresh 800–950g | Body Wash | RM 19.45 |
| 8851932354905 | Sunsilk Smooth Manageable 625ml | Shampoo | RM 16.75 |
| 8850006930250 | Colgate Triple Action 175g×2 | Oral Care | RM 15.70 |
| 8888336024929 | Kotex Comfort+Protection Maxi 32cm 12s×3 | Sanitary Pad | RM 13.60 |
| 9556001317636 | Milo Softpack 1.8kg (FOC 200g) | Beverage | RM 33.49 |
| 9556046111060 | Buruh Cooking Oil 5kg | Cooking Oil | RM 29.85 |
| 9555216581627 | Lotuss Fresh Chicken Eggs Grade A 30s | Eggs | RM 14.79 |
| 9556091177455 | Stabilo Liner F Blue 2s | Stationery | RM 2.70 |

Senarai penuh 6,114 barcode ada dalam `sara_eligible_lotuss.csv`.

---

## 5. Masalah kualiti data yang ditemui

### 5.1 Banyak barcode lama tidak sah

- **211 daripada 7,984** barcode dalam data lama gagal semakan digit GS1.
- **8** barcode mempunyai panjang tidak standard (15–37 digit).
- Contoh: `65010294`, `9551331626211`, `2000000058174`.
- Katalog Lotuss pula hanya **3 daripada 15,852** yang gagal checksum — jauh lebih bersih.

Kesan: sebahagian keputusan “tidak layak” dalam data lama mungkin disebabkan barcode itu sendiri tidak sah, bukan kerana produk tiada dalam senarai SARA.

### 5.2 CSV lama tidak lengkap

| Fail | Bilangan rekod |
|---|---:|
| `sara_products_checked.json` | **7,984** |
| `sara_products_checked.csv` | **6,314** |
| Beza | **1,670** |

Rekod yang hilang ialah hampir keseluruhan korpus “full”: `off_malaysia_full.json` (1,417), `obf_full.json` (180), `opf_full.json` (73). Jadi CSV itu adalah versi lama/stale, bukan versi 5 yang lengkap. Sesiapa yang menggunakan CSV akan mendapat angka berbeza daripada laporan.

### 5.3 Nama produk yang dipaparkan API tidak boleh dipercayai

Ujian tiga hala: bandingkan nama sumber (OFF) dengan tajuk Lotuss; jika kedua-duanya sepakat (similarity ≥ 0.7), semak nama yang dipulangkan API.

- **239** barcode memenuhi syarat “OFF ≈ Lotuss”.
- **78 (32.6%)** daripadanya mempunyai nama API yang berbeza (similarity < 0.5).

Contoh jelas:

| Barcode | OFF + Lotuss sepakat | Nama yang dipulangkan API |
|---|---|---|
| 9556231110045 | Gardenia Original Classic Jumbo 600g | Gardenia Toastem Roat Meal |
| 6917878029252 | Maggi Seasoning No.3 200ml | Knorr Chic Stock 500g |
| 9557305002327 | Marigold HL Milk Chocolate 946ml | Fernleaf 900g |
| 9556755000334 | Seri Murni Cooking Oil 2kg | Neptune Blended Cooking Oil |
| 9556001254054 | Nescafé Classic 220g | Milo Plusfibre |
| 9415007033202 | Anlene Gold 5X 550g | Es Choice Coconut Cream Powder |

Ini bukan sekadar perbezaan ejaan; ada yang **jenama dan kategori berbeza sama sekali**.

### 5.4 Kategori API juga tidak konsisten

Contoh daripada imbasan baharu:

| Produk sebenar (Lotuss) | Kategori yang dipulangkan API |
|---|---|
| Tina Powder Detergent Lavender 5kg | **Sanitary Pad** |
| Aliv Body Wash Peach+Honey 900ml | **Dishwasher** |
| Value Toilet Cleaner 500ml Lemon | **Floor Cleaner** |
| Harpic Liq Power Lavender 2×500ml (satu barcode) | **Dishwasher** |
| Clorox Bleach Regular 2L | **Detergent** |
| Magiclean Toilet Bleach 500ml | **Dishwasher** |

### 5.5 Implikasi

1. **Jangan percaya nama/kategori yang dipaparkan** sebagai bukti produk. Ia boleh salah walaupun `isEligible=true`.
2. **Kunci utama mesti barcode**, bukan nama.
3. `isEligible` masih boleh digunakan sebagai isyarat, tetapi pengesahan di rak (label SARA/MyKasih) tetap perlu.
4. Untuk ketepatan sebenar, minta **senarai induk rasmi SARA** daripada MyKasih; API awam ini bukan senarai rasmi.

---

## 6. Semakan harga silang: Lotuss vs Mydin

Empat produk yang sama, 25 Okt 2026:

| Produk | Barcode | Lotuss | Mydin | Catatan |
|---|---|---:|---:|---|
| Milo Softpack 1.8kg (FOC 200g) | 9556001317636 | RM 33.49 | RM 38.50 | Promo Lotuss |
| Buruh Cooking Oil 5kg | 9556046111060 | RM 29.85 | RM 30.90 | |
| Maggi Chilli Sauce 500g | 9556001601001 | RM 5.45 | RM 5.40 | Hampir sama |
| Dettol Body Wash Fresh 800–950g | 9556111621203 | RM 19.45 | RM 23.20 | Botol vs botol |

Harga kedua-dua laman berada dalam julat yang munasabah; perbezaan besar kebanyakannya kerana promosi. Ini mengesahkan data Lotuss bukan rekaan dan sepadan dengan pasaran.

---

## 7. FAMA: kenapa ia tidak dapat mengesahkan barcode

FAMA (`fama.gov.my`) mempunyai:

- **Harga Pasaran Terkini** — dashboard Power BI, harga komoditi per kg (sayur, buah, ikan, daging).
- **AgroBazaar Online** — marketplace hasil pertanian segar.
- **Analisis Harga Komoditi Terpilih** — dashboard Power BI.

Tiada satu pun mendedahkan **barcode produk runcit**. Jadi FAMA tidak boleh digunakan untuk semakan `isEligible`. Ia hanya berguna untuk membandingkan harga barang segar (yang kebanyakannya tidak berbarcode).

---

## 8. Kaveat

1. **Assortmen kedai:** data Lotuss diambil dengan `storeCodes:["5001"]` dan `availability:true`. Assortmen dan stok boleh berbeza mengikut cawangan.
2. **Harga promosi:** `specialPrice` digunakan jika ada; harga boleh berubah selepas 25 Okt 2026.
3. **Bukan senarai rasmi:** API MyKasih ialah sistem dalaman aplikasi, bukan senarai induk SARA yang diterbitkan. Keputusan `isEligible` boleh berubah bila MyKasih mengemas kini data.
4. **Barcode 8/12/14-digit:** 211 barcode layak tambahan termasuk kod 8-digit (sebahagiannya kod dalaman/PLU) dan 12/14-digit (UPC/GTIN). Untuk analisis ketat, gunakan 13-digit sahaja (5,903).
5. **API sempat pulangkan 503** selepas imbasan besar; ia pulih dalam ~1 minit. Semua 14,571 rekod imbasan disimpan dengan HTTP 200 dan 0 ralat.
6. **Nama/kategori API** tidak boleh dipercayai (lihat §5.3–5.4).

---

## 9. Fail yang dihasilkan

| Fail | Kandungan |
|---|---|
| `sara_eligible_lotuss.csv` | **6,114** barcode layak (barcode, nama Lotuss, jenama, harga, stok, kategori SARA, `status`) |
| `sara_eligible_baru_5989.csv` | **5,989** barcode layak yang benar-benar baharu (tidak ada dalam data lama) |
| `sara_scan_lotuss.csv` | **14,571** baris keputusan imbasan penuh |
| `perbandingan_kategori.csv` | Kiraan lama vs baharu mengikut kategori |
| `harga_lotuss_vs_mydin.csv` | Empat perbandingan harga |
| `ringkasan.json` | Ringkasan angka dalam format mesin |
| `carta_kategori.png` | Carta perbandingan kategori |
| `LAPORAN_SEMAKAN.md` | Laporan ini |

Dalam `sara_eligible_lotuss.csv`, lajur `status` bernilai `baharu` (5,989) atau `semakan_semula` (125, sudah ada dalam data lama).

Fail mentah katalog Lotuss juga disertakan dalam `data/lotuss_catalog.json` (13,391 produk) dan `data/lotuss_barcodes.csv` (15,852 barcode). Salinan kerja: `/content/kerja/`.

---

## 10. Cadangan

1. **Guna `sara_eligible_lotuss.csv`** sebagai senarai semakan terkini; ia mengandungi 5,989 penemuan baharu yang tiada dalam zip asal.
2. **Jangan guna CSV lama** (`sara_products_checked.csv`) sebagai rujukan lengkap — ia hanya 6,314 daripada 7,984 rekod.
3. **Tambah semakan digit GS1** dalam pipeline; 211 barcode lama tidak sah.
4. **Kunci pada barcode**, bukan nama produk. Nama API boleh salah untuk ~1 dalam 3 barcode.
5. **Semak di rak** sebelum membuat keputusan pembelian; `isEligible` hanyalah isyarat, bukan jaminan.
6. Untuk data rasmi, hubungi MyKasih (03-7720 1800) atau KPDN/HASiL untuk senarai induk SARA.
7. Untuk penyegaran berkala, API carian Lotuss boleh dijalankan semula (134 halaman, ~3–5 minit) dan diuji melalui API MyKasih.

---

*Laporan ini dihasilkan secara automatik daripada data awam pada 25 Oktober 2026. Ia bukan nasihat rasmi dan bukan pengesahan daripada MyKasih, SARA, FAMA, Lotuss atau Mydin.*
