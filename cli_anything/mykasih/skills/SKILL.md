# MyKasih / SARA Skill

Use this skill to operate MyKasih/SARA eligibility data via `cli-anything-mykasih`.

## When to use
- User asks "layak ke SARA?", "boleh guna SARA?", "MyKasih", "check barcode"
- Need to verify toilet cleaner, Harpic, Clorox, Mr Muscle etc.
- List merchants or categories

## Commands

### Check one product
```bash
cli-anything-mykasih check 8993560033064
cli-anything-mykasih check 9555222606710 --json
mykasih check 0044600306193 --offline
```

### Bulk check
```bash
mykasih bulk-check --file barcodes.txt
mykasih bulk-check --file barcodes.csv --json
```

### Categories
```bash
mykasih categories
mykasih categories --json
```

### Merchants
```bash
mykasih merchants --state Selangor --limit 10
mykasih merchants --state Selangor --json | jq .
```

### Search eligible products
```bash
mykasih search harpic
mykasih search "toilet" --json
mykasih search maggi --limit 5
```

## API details
- Live: `POST https://wms.dialogasia.com/api/mobile-svc/product/saraforall-GetProductEligible`
  Body: `{"productBarcode":"<ean>","merchantID":"<uuid>","programId":"34baa040-b9c5-4ebc-ae8b-8c9e6b6f623f"}`
- Offline fallback: `mykasih-sara/sara_products_checked.json` (7,984 tested, 2,395 eligible)

## Known eligible toilet cleaners
- 8993560033064 HARPIC PWR PLUS CITRUS 450ML
- 8993560033057 HARPIC PWR PLUS 450ML
- 0044600306193 CLOROX T.BOWL CLEANER BLEACH GEL 709ML
- 0044600009384 CLOROX T.BOWL CLEANER RAIN CLEAN 709ML
- 9555222606710 MR MUSCLE TOILET BLOCK 6X40G
- 9555222603030 MR MUSCLE ADV TOI/CLEAN MARINE 2X500ML

## Rules
- Always support `--json` for agent parsing
- Prefer live API, fallback offline automatically

## Fresh data (25 Okt 2026)
- `mykasih fresh` — ringkasan Lotuss 13,391 produk, 15,852 barcode, 6,114 layak, 5,989 baru tulen
- `mykasih compare` — perbandingan kategori lama vs baru
- `mykasih search` kini cari dalam 6,114 produk Lotuss (bukan 2,395 lama sahaja)
- Offline fallback kini guna sara_scan_lotuss.csv (14,571 rekod) dahulu
