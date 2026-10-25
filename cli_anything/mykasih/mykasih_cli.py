"""MyKasih/SARA CLI — entry point"""
import json
import sys
from pathlib import Path
import click
from cli_anything.mykasih.utils.backend import check_product, get_categories, list_merchants, search_eligible, DATA_DIR, get_fresh_summary, get_perbandingan

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version="1.1.0", prog_name="mykasih")
def cli():
    """MyKasih / SARA — semak produk, kategori & kedai (data segar Lotuss 25 Okt 2026)."""
    pass

@cli.command("check")
@click.argument("barcode")
@click.option("--merchant-id", default=None, help="Merchant ID (default Rawang)")
@click.option("--offline", is_flag=True, help="Guna data offline sahaja (Lotuss + lama)")
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
    barcodes = []
    p = Path(filepath)
    if p.suffix.lower() == ".csv":
        import csv
        with open(p, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            field = None
            for cand in ["barcode", "code", "productBarcode", "kod"]:
                if cand in (reader.fieldnames or []):
                    field = cand
                    break
            if field:
                for row in reader:
                    barcodes.append(row[field])
            else:
                f.seek(0)
                for row in f:
                    barcodes.append(row.strip().split(",")[0])
    else:
        barcodes = [l.strip() for l in p.read_text(encoding='utf-8').splitlines() if l.strip()]

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
    """Cari produk layak (data segar Lotuss 6,114). Contoh: mykasih search lotuss"""
    results = search_eligible(query, limit=limit)
    if as_json:
        click.echo(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        if not results:
            # cuba info ringkasan
            total = 8384
            click.echo(f"Tiada hasil untuk '{query}' (cari dalam {total} produk layak diketahui). Cuba kata kunci lain.")
            return
        click.echo(f"Hasil '{query}' ({len(results)}):")
        for r in results:
            name = r.get("productName") or r.get("produk_lotuss") or r.get("product_name") or "-"
            cat = r.get("category") or r.get("kategori_sara") or r.get("productCategoryName") or "-"
            bc = r.get("barcode") or r.get("code") or "-"
            harga = r.get("harga_rm") or r.get("price") or ""
            extra = f" RM{harga}" if harga else ""
            click.echo(f"- {name} | {cat} | {bc}{extra}")

@cli.command("fresh")
@click.option("--json", "as_json", is_flag=True)
def fresh_cmd(as_json):
    """Ringkasan data segar Lotuss 25 Okt 2026 (5,989 baru, 8,384 total)"""
    summary = get_fresh_summary()
    perbandingan = get_perbandingan()
    if not summary:
        click.echo("Tiada data segar (ringkasan.json tidak ditemui)")
        return
    if as_json:
        click.echo(json.dumps({"ringkasan": summary, "perbandingan": perbandingan}, indent=2, ensure_ascii=False))
    else:
        click.echo(f"=== Semakan Lotuss 25 Okt 2026 ===")
        click.echo(f"Produk Lotuss: {summary.get('lotuss_produk')} produk, {summary.get('lotuss_barcode_unik')} barcode")
        click.echo(f"Diuji baru: {summary.get('diuji_baharu')} → Layak: {summary.get('layak_baharu')} (43.5% dalam katalog)")
        click.echo(f"Baru tulen: {summary.get('layak_baharu_tulen')} | Total diketahui: {summary.get('jumlah_layak_diketahui')} (was 2,395)")
        click.echo("")
        if perbandingan:
            click.echo("Perbandingan lama vs baru (top):")
            # sort by baru
            perbandingan_sorted = sorted(perbandingan, key=lambda x: int(x.get("baharu_lotuss") or 0), reverse=True)
            for row in perbandingan_sorted[:10]:
                click.echo(f"  {row['kategori']}: {row['lama']} → {row['baharu_lotuss']}")

@cli.command("compare")
@click.option("--json", "as_json", is_flag=True)
def compare_cmd(as_json):
    """Banding kategori lama vs baru Lotuss"""
    perbandingan = get_perbandingan()
    if as_json:
        click.echo(json.dumps(perbandingan, indent=2, ensure_ascii=False))
    else:
        if not perbandingan:
            click.echo("Tiada perbandingan_kategori.csv")
            return
        click.echo(f"{'Kategori':<20} {'Lama':>6} {'Baru':>6} {'+':>6}")
        click.echo("-"*40)
        for row in sorted(perbandingan, key=lambda x: int(x.get("baharu_lotuss") or 0), reverse=True):
            lama = int(row["lama"] or 0)
            baru = int(row["baharu_lotuss"] or 0)
            diff = baru - lama
            click.echo(f"{row['kategori']:<20} {lama:>6} {baru:>6} {diff:>+6}")

@cli.command("info")
def info_cmd():
    """Info data & API (termasuk data segar)"""
    click.echo("MyKasih CLI v1.1.0 — data segar 25 Okt 2026")
    click.echo(f"DATA_DIR: {DATA_DIR or 'tiada offline data (hanya live API)'}")
    click.echo("API: https://wms.dialogasia.com/api/mobile-svc/product/saraforall-GetProductEligible")
    click.echo("APK SHA256: 535ba455814e44034ef935d31c5e3ba8032f2fa7197fe5651d4a367d8789690f")
    summary = get_fresh_summary()
    if summary:
        click.echo(f"Fresh: {summary.get('lotuss_produk')} produk Lotuss, {summary.get('layak_baharu')} layak baru, total {summary.get('jumlah_layak_diketahui')} diketahui")
    if DATA_DIR:
        cats = DATA_DIR / "sara_product_categories.json"
        if cats.exists():
            d = json.loads(cats.read_text(encoding='utf-8'))
            click.echo(f"Kategori offline: {len(d)}")
        # check old too
        from pathlib import Path as _P
        old = _P("/home/user/mykasih-sara/sara_eligible_products.json")
        if old.exists():
            click.echo(f"Produk layak lama: {len(json.loads(old.read_text(encoding='utf-8')))} (2,395)")
        fresh_file = DATA_DIR / "sara_eligible_lotuss.csv"
        if fresh_file.exists():
            import csv as _csv
            with open(fresh_file, encoding='utf-8') as f:
                click.echo(f"Produk layak segar Lotuss: {sum(1 for _ in f)-1} (6,114)")

def main():
    cli()

if __name__ == "__main__":
    main()
