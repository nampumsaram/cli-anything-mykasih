"""Backend untuk MyKasih API - wrapper untuk wms.dialogasia.com"""
import json
import csv
from pathlib import Path
import requests

API_BASE = "https://wms.dialogasia.com/api/mobile-svc"
PROGRAM_ID = "34baa040-b9c5-4ebc-ae8b-8c9e6b6f623f"
DEFAULT_MERCHANT = "7cdd66d1-7d21-43b0-8179-ce429499b134"  # Rawang Mutiara Kundang

def _find_data_dir():
    candidates = [
        Path(__file__).parent / "data",  # packaged: cli_anything/mykasih/data
        Path(__file__).parent.parent / "data",
        Path("/home/user/mykasih-sara/semakan-2026-10-25"),
        Path("/home/user/mykasih-sara"),
        Path("./mykasih-sara"),
        Path("./semakan-2026-10-25"),
    ]
    for c in candidates:
        if c.exists() and any((c / f).exists() for f in [
            "sara_product_categories.json", "sara_eligible_lotuss.csv", "sara_eligible_baru_5989.csv", "ringkasan.json"
        ]):
            return c
    return None

DATA_DIR = _find_data_dir()
# Cari juga old data dir untuk fallback kategori
OLD_DATA_DIR = Path("/home/user/mykasih-sara")
if not OLD_DATA_DIR.exists():
    OLD_DATA_DIR = None

def check_product(barcode: str, merchant_id: str = DEFAULT_MERCHANT, program_id: str = PROGRAM_ID, offline: bool = False):
    """Semak kelayakan produk - live API, fallback offline jika gagal"""
    barcode = barcode.strip()
    if offline:
        off = _check_offline(barcode)
        if off:
            return off
        return {"barcode": barcode, "isEligible": False, "productName": None, "category": None, "source": "offline: not found", "raw": None}
    try:
        url = f"{API_BASE}/product/saraforall-GetProductEligible"
        payload = {"productBarcode": barcode, "merchantID": merchant_id, "programId": program_id}
        r = requests.post(url, json=payload, timeout=10, headers={"Content-Type": "application/json"})
        r.raise_for_status()
        data = r.json()
        return {
            "barcode": barcode,
            "isEligible": data.get("isEligible", False),
            "productName": data.get("data", {}).get("productName") if data.get("data") else None,
            "category": data.get("data", {}).get("productCategoryName") if data.get("data") else None,
            "raw": data,
            "source": "live: saraforall-GetProductEligible"
        }
    except Exception as e:
        off = _check_offline(barcode)
        if off:
            off["fallback_reason"] = str(e)
            return off
        return {"barcode": barcode, "isEligible": False, "productName": None, "category": None, "error": str(e), "source": "live-error"}

def _check_offline(barcode: str):
    # Prioriti: data segar Lotuss (14,571 rekod) -> sara_scan_lotuss.csv
    # kemudian sara_eligible_lotuss.csv / baru_5989.csv
    # kemudian data lama 7,984
    search_order = [
        ("sara_scan_lotuss.csv", _scan_csv_lookup),
        ("sara_eligible_lotuss.csv", _eligible_lotuss_lookup),
        ("sara_eligible_baru_5989.csv", _eligible_baru_lookup),
        ("sara_products_checked.json", _old_json_lookup),
        ("sara_products_checked.csv", _old_csv_lookup),
    ]
    # cek DATA_DIR dulu (packaged fresh)
    for fname, func in search_order:
        if DATA_DIR and (DATA_DIR / fname).exists():
            res = func(DATA_DIR / fname, barcode)
            if res:
                return res
    # fallback OLD_DATA_DIR
    if OLD_DATA_DIR:
        for fname, func in search_order:
            if (OLD_DATA_DIR / fname).exists():
                res = func(OLD_DATA_DIR / fname, barcode)
                if res:
                    return res
        # old json di semakan lama? cuba semakan-2026-10-25 fallback juga
        semakan = OLD_DATA_DIR / "semakan-2026-10-25"
        if semakan.exists():
            for fname, func in search_order:
                if (semakan / fname).exists():
                    res = func(semakan / fname, barcode)
                    if res:
                        return res
    return None

def _scan_csv_lookup(path: Path, barcode: str):
    # sara_scan_lotuss.csv: barcode,produk_lotuss,jenama,harga_rm,layak,kategori_sara,nama_api,status
    try:
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("barcode") == barcode:
                    layak = row.get("layak") in ("True", "true", "1") or row.get("isEligible") in ("True", "true")
                    return {
                        "barcode": barcode,
                        "isEligible": layak,
                        "productName": row.get("produk_lotuss") or row.get("productName"),
                        "category": row.get("kategori_sara") or row.get("category"),
                        "raw": row,
                        "source": f"offline: {path.name}"
                    }
    except: pass
    return None

def _eligible_lotuss_lookup(path: Path, barcode: str):
    try:
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("barcode") == barcode:
                    return {
                        "barcode": barcode,
                        "isEligible": True,
                        "productName": row.get("produk_lotuss") or row.get("product_name"),
                        "category": row.get("kategori_sara") or row.get("category"),
                        "raw": row,
                        "source": f"offline: {path.name}"
                    }
    except: pass
    return None

def _eligible_baru_lookup(path: Path, barcode: str):
    return _eligible_lotuss_lookup(path, barcode)

def _old_json_lookup(path: Path, barcode: str):
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        for item in data:
            if str(item.get("code") or item.get("barcode") or item.get("productBarcode")) == barcode:
                return {
                    "barcode": barcode,
                    "isEligible": item.get("isEligible", False),
                    "productName": (item.get("data") or {}).get("productName") or item.get("product_name") or item.get("productName"),
                    "category": (item.get("data") or {}).get("productCategoryName") or item.get("category"),
                    "raw": item,
                    "source": f"offline: {path.name}"
                }
    except: pass
    return None

def _old_csv_lookup(path: Path, barcode: str):
    try:
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("barcode") == barcode or row.get("code") == barcode:
                    layak = row.get("isEligible") in ("True", "true", "1") or row.get("layak") in ("True", "true")
                    return {
                        "barcode": barcode,
                        "isEligible": layak,
                        "productName": row.get("productName") or row.get("product_name") or row.get("produk_lotuss"),
                        "category": row.get("category") or row.get("productCategoryName") or row.get("kategori_sara"),
                        "raw": row,
                        "source": f"offline: {path.name}"
                    }
    except: pass
    return None

def get_categories():
    """Dapat 15 kategori - live jika boleh, else offline"""
    try:
        url = f"{API_BASE}/product/saraforall-GetEligibleProductCategory"
        r = requests.post(url, json={}, timeout=10, headers={"Content-Type": "application/json"})
        r.raise_for_status()
        data = r.json()
        if data.get("data"):
            return data["data"]
    except: pass
    # fallback ke old data
    for base in [DATA_DIR, OLD_DATA_DIR]:
        if base and (base / "sara_product_categories.json").exists():
            return json.loads((base / "sara_product_categories.json").read_text(encoding='utf-8'))
        if base and (base / "semakan-2026-10-25" / "sara_product_categories.json").exists():
            return json.loads((base / "semakan-2026-10-25" / "sara_product_categories.json").read_text(encoding='utf-8'))
    return []

def list_merchants(program: str = "saraforall", state: str = None):
    """Senarai kedai - live jika boleh, else offline json"""
    try:
        if program in ("saraforall", "all"):
            url = f"{API_BASE}/merchant/saraforall-list"
            payload = {"programId": PROGRAM_ID}
            r = requests.post(url, json=payload, timeout=15)
            r.raise_for_status()
            data = r.json()
            merchants = data.get("data", [])
            if state:
                merchants = [m for m in merchants if m.get("state", "").lower() == state.lower()]
            return merchants
    except: pass
    for base in [DATA_DIR, OLD_DATA_DIR]:
        if not base: continue
        fname = "mykasih_merchants_saraforall.json" if program == "saraforall" else "mykasih_merchants_portal.json"
        p = base / fname
        if p.exists():
            merchants = json.loads(p.read_text(encoding='utf-8'))
            if state:
                merchants = [m for m in merchants if m.get("state", "").lower() == state.lower()]
            return merchants
        # cuba di semakan lama? merchants masih di old dir
        if OLD_DATA_DIR and (OLD_DATA_DIR / fname).exists():
            merchants = json.loads((OLD_DATA_DIR / fname).read_text(encoding='utf-8'))
            if state:
                merchants = [m for m in merchants if m.get("state", "").lower() == state.lower()]
            return merchants
    return []

def search_eligible(query: str, limit: int = 20):
    """Cari dalam produk layak - utamakan data segar Lotuss (6,114), fallback lama"""
    q = query.lower()
    results = []
    # cuba fresh dulu
    fresh_files = []
    if DATA_DIR:
        if (DATA_DIR / "sara_eligible_lotuss.csv").exists():
            fresh_files.append(DATA_DIR / "sara_eligible_lotuss.csv")
        if (DATA_DIR / "sara_eligible_baru_5989.csv").exists():
            fresh_files.append(DATA_DIR / "sara_eligible_baru_5989.csv")
    if OLD_DATA_DIR:
        if (OLD_DATA_DIR / "semakan-2026-10-25" / "sara_eligible_lotuss.csv").exists():
            fresh_files.append(OLD_DATA_DIR / "semakan-2026-10-25" / "sara_eligible_lotuss.csv")
        if (OLD_DATA_DIR / "sara_eligible_products.json").exists() and not fresh_files:
            # fallback lama sahaja jika tiada fresh
            fresh_files.append(OLD_DATA_DIR / "sara_eligible_products.json")

    # jika fresh berupa CSV
    for p in fresh_files:
        if p.suffix == ".csv":
            try:
                with open(p, newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        name = (row.get("produk_lotuss") or row.get("productName") or row.get("product_name") or "").lower()
                        cat = (row.get("kategori_sara") or row.get("category") or "").lower()
                        brand = (row.get("jenama") or row.get("brand") or "").lower()
                        if q in name or q in cat or q in brand:
                            # normalisasi untuk konsisten dengan format lama
                            row["productName"] = row.get("produk_lotuss") or row.get("productName")
                            row["category"] = row.get("kategori_sara") or row.get("category")
                            row["brand"] = row.get("jenama") or row.get("brand")
                            results.append(row)
                            if len(results) >= limit:
                                return results
            except: pass
        else:
            # json
            try:
                data = json.loads(p.read_text(encoding='utf-8'))
                for item in data:
                    name = (item.get("productName") or item.get("product_name") or "").lower()
                    cat = (item.get("productCategoryName") or item.get("category") or "").lower()
                    brand = (item.get("brand") or "").lower()
                    if q in name or q in cat or q in brand:
                        results.append(item)
                        if len(results) >= limit:
                            return results
            except: pass
    return results

def get_fresh_summary():
    """Ringkasan terkini dari ringkasan.json"""
    for base in [DATA_DIR, OLD_DATA_DIR]:
        if not base: continue
        p = base / "ringkasan.json"
        if p.exists():
            return json.loads(p.read_text(encoding='utf-8'))
        p2 = base / "semakan-2026-10-25" / "ringkasan.json"
        if p2.exists():
            return json.loads(p2.read_text(encoding='utf-8'))
    return None

def get_perbandingan():
    """Perbandingan kategori lama vs baru"""
    for base in [DATA_DIR, OLD_DATA_DIR]:
        if not base: continue
        for cand in ["perbandingan_kategori.csv", "semakan-2026-10-25/perbandingan_kategori.csv"]:
            p = base / cand
            if p.exists():
                with open(p, newline='', encoding='utf-8') as f:
                    return list(csv.DictReader(f))
    return []
