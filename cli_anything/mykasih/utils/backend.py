"""Backend untuk MyKasih API - wrapper untuk wms.dialogasia.com"""
import json
import os
from pathlib import Path
import requests

API_BASE = "https://wms.dialogasia.com/api/mobile-svc"
PROGRAM_ID = "34baa040-b9c5-4ebc-ae8b-8c9e6b6f623f"
DEFAULT_MERCHANT = "7cdd66d1-7d21-43b0-8179-ce429499b134"  # Rawang Mutiara Kundang

# Data dir - cari offline data dari mykasih-sara jika ada
def _find_data_dir():
    candidates = [
        Path(__file__).parent.parent / "data",
        Path("/home/user/mykasih-sara"),
        Path("./mykasih-sara"),
    ]
    for c in candidates:
        if c.exists() and (c / "sara_product_categories.json").exists():
            return c
    return None

DATA_DIR = _find_data_dir()

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
        # Normalisasi
        return {
            "barcode": barcode,
            "isEligible": data.get("isEligible", False),
            "productName": data.get("data", {}).get("productName") if data.get("data") else None,
            "category": data.get("data", {}).get("productCategoryName") if data.get("data") else None,
            "raw": data,
            "source": "live: saraforall-GetProductEligible"
        }
    except Exception as e:
        # fallback offline
        off = _check_offline(barcode)
        if off:
            off["fallback_reason"] = str(e)
            return off
        return {"barcode": barcode, "isEligible": False, "productName": None, "category": None, "error": str(e), "source": "live-error"}

def _check_offline(barcode: str):
    if not DATA_DIR:
        return None
    # cari dalam sara_products_checked
    for fname in ["sara_products_checked.json", "sara_eligible_products.json"]:
        p = DATA_DIR / fname
        if not p.exists():
            continue
        try:
            import json as j
            data = j.loads(p.read_text())
            # sara_products_checked.json adalah list of {code, isEligible, data}
            for item in data:
                if str(item.get("code") or item.get("barcode") or item.get("productBarcode")) == barcode:
                    return {
                        "barcode": barcode,
                        "isEligible": item.get("isEligible", False),
                        "productName": (item.get("data") or {}).get("productName") or item.get("product_name") or item.get("productName"),
                        "category": (item.get("data") or {}).get("productCategoryName") or item.get("category"),
                        "raw": item,
                        "source": f"offline: {fname}"
                    }
            # juga cuba cari dalam csv
        except: pass
    # cari dalam csv
    csv_path = DATA_DIR / "sara_products_checked.csv"
    if csv_path.exists():
        import csv
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("barcode") == barcode or row.get("code") == barcode:
                    return {
                        "barcode": barcode,
                        "isEligible": row.get("isEligible") == "True" or row.get("isEligible") == "true",
                        "productName": row.get("productName") or row.get("product_name"),
                        "category": row.get("category") or row.get("productCategoryName"),
                        "raw": row,
                        "source": "offline: sara_products_checked.csv"
                    }
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
    # fallback offline
    if DATA_DIR and (DATA_DIR / "sara_product_categories.json").exists():
        return json.loads((DATA_DIR / "sara_product_categories.json").read_text())
    return []

def list_merchants(program: str = "saraforall", state: str = None):
    """Senarai kedai - live jika boleh, else offline json"""
    # cuba live dulu
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
    # offline
    if DATA_DIR:
        # saraforall
        fname = "mykasih_merchants_saraforall.json" if program == "saraforall" else "mykasih_merchants_portal.json"
        p = DATA_DIR / fname
        if p.exists():
            merchants = json.loads(p.read_text())
            if state:
                merchants = [m for m in merchants if m.get("state", "").lower() == state.lower()]
            return merchants
    return []

def search_eligible(query: str, limit: int = 20):
    """Cari dalam produk layak offline"""
    if not DATA_DIR:
        return []
    p = DATA_DIR / "sara_eligible_products.json"
    if not p.exists():
        p = DATA_DIR / "sara_products_eligible.json"
    if not p.exists():
        return []
    data = json.loads(p.read_text())
    q = query.lower()
    results = []
    for item in data:
        name = (item.get("productName") or item.get("product_name") or "").lower()
        cat = (item.get("productCategoryName") or item.get("category") or "").lower()
        brand = (item.get("brand") or "").lower()
        if q in name or q in cat or q in brand:
            results.append(item)
            if len(results) >= limit:
                break
    return results
