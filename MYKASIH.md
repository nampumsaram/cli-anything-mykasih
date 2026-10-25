# MyKasih / SARA - CLI Harness SOP

## Overview
MyKasih adalah platform e-wallet Sumbangan Asas Rahmah (SARA) di Malaysia. Backend `wms.dialogasia.com` mendedahkan endpoint terbuka untuk semak kelayakan produk.

Real software: API MyKasih `wms.dialogasia.com` (bukan binary)
CLI role: Generate structured commands → call API → verify response → fallback offline corpus (7,984 tested)

## Architecture
- API base: `https://wms.dialogasia.com/api/mobile-svc`
- Auth: NONE untuk `saraforall-*` endpoints (bug/feature)
- ProgramId: `34baa040-b9c5-4ebc-ae8b-8c9e6b6f623f` (SARA 2)
- Offline data: `mykasih-sara/` — 35 files, SHA256 `14566498...`

## API endpoints
| Endpoint | Auth | CLI command |
|----------|------|-------------|
| `product/saraforall-GetEligibleProductCategory` | No | `mykasih categories` |
| `product/saraforall-GetProductEligible` | No | `mykasih check <barcode>` |
| `merchant/saraforall-list` | No | `mykasih merchants` |
| `product/GetEligibleProductCategory` | Yes (401) | — |
| `merchant/list` | Yes | — |

## CLI Command Map
```
mykasih / cli-anything-mykasih
├── check <barcode> [--offline] [--json] [--merchant-id]
├── bulk-check --file <file> [--json]
├── categories [--json]
├── merchants --state < negeri> --program saraforall|all --limit N [--json]
├── search <query> [--limit N] [--json]
└── info
```

## Testing Strategy
- Unit: mock requests.post, no internet
- E2E: hit live wms.dialogasia.com, verify 4 toilet cleaners tetap layak
