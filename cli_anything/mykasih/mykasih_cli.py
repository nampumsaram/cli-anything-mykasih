"""MyKasih/SARA CLI — entry point"""
import json
import csv
import sys
from pathlib import Path
import click
from cli_anything.mykasih.utils.backend import check_product, get_categories, list_merchants, search_eligible, DATA_DIR

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version="1.0.0", prog_name="mykasih")
def cli():
    """MyKasih / SARA — semak produk, kategori & kedai."""
    pass

@cli.command("check")
@click.argument("barcode")
@click.option("--merchant-id", default=None, help="Merchant ID (default Rawang)")
@click.option("--offline", is_flag=True, help="Guna data offline sahaja")
@click.option("--json", "as_json", is_flag=True, help="Output JSON")
def check_cmd(barcode, merchant_id, offline, as_json):
    """Semak kelayakan 1 barcode. Contoh: mykasih check 8993560033064"""
    from cli_anything.mykasih.utils.backend import DEFAULT_MERCHANT
    mid = merchant_id or DEFAULT_MERCHANT
    result = check_product(barcode, merchant_id=mid, offline=offline)
    if as_json:
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        status = "✅ LAYAK" if result.get("isEligible") else "❌ TIDAK LAYAK"
        name = result.get("productName") or "-"
        cat = result.get("category") or "-"
        click.echo(f"{status} | {barcode}")
        click.echo(f"Produk: {name}")
        click.echo(f"Kategori: {cat}")
        click.echo(f"Sumber: {result.get('source')}")
        if result.get("error"):
            click.echo(f"Ralat: {result['error']}", err=True)

@cli.command("bulk-check")
@click.option("--file", "filepath", required=True, type=click.Path(exists=True), help="Fail txt/csv senarai barcode")
@click.option("--json", "as_json", is_flag=True)
@click.option("--offline", is_flag=True)
def bulk_check(filepath, as_json, offline):
    """Semak banyak barcode dari fail. Satu barcode per baris atau CSV dengan lajur barcode."""
    from cli_anything.mykasih.utils.backend import DEFAULT_MERCHANT
    barcodes = []
    p = Path(filepath)
    if p.suffix.lower() == ".csv":
        import csv
        with open(p) as f:
            reader = csv.DictReader(f)
            # cari lajur barcode
            field = None
            for cand in ["barcode", "code", "productBarcode", "kod"]:
                if cand in reader.fieldnames:
                    field = cand
                    break
            if field:
                for row in reader:
                    barcodes.append(row[field])
            else:
                # fallback baris pertama
                f.seek(0)
                for row in f:
                    barcodes.append(row.strip().split(",")[0])
    else:
        barcodes = [l.strip() for l in p.read_text().splitlines() if l.strip()]

    results = []
    for bc in barcodes:
        if not bc or bc.startswith("#"):
            continue
        r = check_product(bc, offline=offline)
        results.append(r)
        if not as_json:
            icon = "✅" if r.get("isEligible") else "❌"
            click.echo(f"{icon} {bc} → {r.get('productName') or '-'} ({r.get('category') or '-'})")

    if as_json:
        click.echo(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        layak = sum(1 for r in results if r.get("isEligible"))
        click.echo(f"\nRingkasan: {layak}/{len(results)} LAYAK")

@cli.command("categories")
@click.option("--json", "as_json", is_flag=True)
def categories_cmd(as_json):
    """Senarai 15 kategori SARA"""
    cats = get_categories()
    if as_json:
        click.echo(json.dumps(cats, indent=2, ensure_ascii=False))
    else:
        click.echo(f"Jumlah kategori: {len(cats)}")
        for c in cats:
            name = c.get("categoryName")
            ms = c.get("categoryNameMS")
            subs = len(c.get("subCategories", []))
            click.echo(f"- {name} / {ms} — {subs} subkategori")

@cli.command("merchants")
@click.option("--state", default=None, help="Tapis negeri, cth --state Selangor")
@click.option("--program", default="saraforall", type=click.Choice(["saraforall", "all"]), help="Program")
@click.option("--limit", default=20, show_default=True)
@click.option("--json", "as_json", is_flag=True)
def merchants_cmd(state, program, limit, as_json):
    """Senarai kedai. Contoh: mykasih merchants --state Selangor"""
    ms = list_merchants(program=program, state=state)
    if as_json:
        click.echo(json.dumps(ms[:limit] if limit else ms, indent=2, ensure_ascii=False))
    else:
        click.echo(f"Jumlah kedai ({program}{', '+state if state else ''}): {len(ms)}")
        for m in ms[:limit]:
            click.echo(f"- {m.get('tradingName')} | {m.get('address1')} | {m.get('city')}, {m.get('state')} {m.get('postalCode')}")
        if len(ms) > limit:
            click.echo(f"... dan {len(ms)-limit} lagi (guna --limit 0 untuk semua, atau --json)")

@cli.command("search")
@click.argument("query")
@click.option("--limit", default=20, show_default=True)
@click.option("--json", "as_json", is_flag=True)
def search_cmd(query, limit, as_json):
    """Cari produk layak. Contoh: mykasih search harpic"""
    results = search_eligible(query, limit=limit)
    if as_json:
        click.echo(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        if not results:
            click.echo(f"Tiada hasil untuk '{query}' dalam 2,395 produk layak.")
            return
        click.echo(f"Hasil '{query}' ({len(results)}):")
        for r in results:
            name = r.get("productName") or r.get("product_name") or r.get("productName")
            cat = r.get("productCategoryName") or r.get("category")
            bc = r.get("barcode") or r.get("code") or r.get("productBarcode") or "-"
            click.echo(f"- {name} | {cat} | {bc}")

@cli.command("info")
def info_cmd():
    """Info data & API"""
    click.echo("MyKasih CLI v1.0.0")
    click.echo(f"DATA_DIR: {DATA_DIR or 'tiada offline data (hanya live API)'}")
    click.echo("API: https://wms.dialogasia.com/api/mobile-svc/product/saraforall-GetProductEligible")
    click.echo("APK SHA256: 535ba455814e44034ef935d31c5e3ba8032f2fa7197fe5651d4a367d8789690f")
    if DATA_DIR:
        cats = DATA_DIR / "sara_product_categories.json"
        if cats.exists():
            import json as j
            d = j.loads(cats.read_text())
            click.echo(f"Kategori offline: {len(d)}")
        elig = DATA_DIR / "sara_eligible_products.json"
        if elig.exists():
            click.echo(f"Produk layak offline: {len(j.loads(elig.read_text()))}")

def main():
    cli()

if __name__ == "__main__":
    main()
