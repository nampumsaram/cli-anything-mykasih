# cli-anything-mykasih

Agent-native CLI for MyKasih / SARA — semak kelayakan produk & senarai kedai tanpa buka app.

Dibina dari hasil bedahan APK MyKasih v1.0.30 (Flutter) — guna endpoint terbuka `wms.dialogasia.com` yang sama app guna.

## Features
- `mykasih check <barcode>` — semak `isEligible` live atau offline
- `mykasih categories` — 15 kategori, 158 subkategori
- `mykasih merchants --state Selangor` — 12k/14k kedai
- `mykasih search "maggie"` — cari dalam 2,395 produk layak
- `mykasih bulk-check --file barcodes.txt`

## Install
```bash
pip install -e .
mykasih --help
# atau via cli-hub
cli-hub install mykasih
```

## Data sources
- APK MyKasih v1.0.30 SHA256 `535ba455814e44034ef935d31c5e3ba8032f2fa7197fe5651d4a367d8789690f`
- API: `https://wms.dialogasia.com/api/mobile-svc/product/saraforall-GetProductEligible`
- Offline corpus: 7,984 kod bar diuji → 2,395 layak (30%)

## Registry untuk CLI-Hub
Lihat `registry-entry.json`

