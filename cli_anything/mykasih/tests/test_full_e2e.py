"""E2E - perlukan internet live API"""
from click.testing import CliRunner
from cli_anything.mykasih.mykasih_cli import cli
import json

runner = CliRunner()

def test_e2e_harpic_live():
    result = runner.invoke(cli, ["check", "8993560033064", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["isEligible"] is True
    assert data["productName"] == "HARPIC PWR PLUS CITRUS 450ML"

def test_e2e_clorox_live():
    result = runner.invoke(cli, ["check", "0044600306193", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["isEligible"] is True

def test_e2e_mrmuscle_live():
    result = runner.invoke(cli, ["check", "9555222606710", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["isEligible"] is True
    assert "MUSCLE" in data["productName"]

def test_e2e_not_eligible():
    result = runner.invoke(cli, ["check", "9556001067316", "--json"])
    assert result.exit_code == 0
    # tak kisah layak atau tak, janji tak crash

def test_e2e_categories_live():
    result = runner.invoke(cli, ["categories", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == 15

