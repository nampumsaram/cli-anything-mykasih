# cli-anything-mykasih

Agent-native CLI for MyKasih / SARA — semak kelayakan produk & senarai kedai tanpa buka app.

Dibina dari hasil bedahan APK MyKasih v1.0.30 (Flutter) — guna endpoint terbuka `wms.dialogasia.com` yang sama app guna.

## Fresh data 25 Okt 2026 (Lotuss)
- 13,391 produk Lotuss disemak → 15,852 barcode → **6,114 LAYAK** (43.5%)
- 5,989 baru tulen → **total diketahui 8,384** (was 2,395)
- Perbandingan kategori: Detergent 1→380, Stationery 4→357, Toilet Cleaner 0→69

## Features
- `mykasih check <barcode>` — semak `isEligible` live atau offline (Lotuss + lama)
- `mykasih fresh` — ringkasan Lotuss
- `mykasih compare` — lama vs baru
- `mykasih categories` — 15 kategori, 158 subkategori
- `mykasih merchants --state Selangor` — 12k/14k kedai
- `mykasih search "maggie"` — cari dalam 6,114 produk segar
- `mykasih bulk-check --file barcodes.txt`

## Install
```bash
pip install git+https://github.com/nampumsaram/cli-anything-mykasih.git
mykasih --help
# atau via cli-hub (selepas PR merge)
cli-hub install mykasih
```

## Data sources
- APK MyKasih v1.0.30 SHA256 `535ba455814e44034ef935d31c5e3ba8032f2fa7197fe5651d4a367d8789690f`
- API: `https://wms.dialogasia.com/api/mobile-svc/product/saraforall-GetProductEligible`
- Fresh: Lotuss 25 Okt 2026 (13,391 produk) + lama 7,984

## Registry untuk CLI-Hub
Lihat `registry-entry.json` (v1.1.0)
