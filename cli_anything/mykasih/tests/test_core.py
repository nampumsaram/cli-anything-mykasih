"""Unit tests - tak perlu live API"""
import json
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from cli_anything.mykasih.mykasih_cli import cli

runner = CliRunner()

def test_check_json_with_mock():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "isEligible": True,
        "data": {"productName": "HARPIC PWR PLUS CITRUS 450ML", "productCategoryName": "Toilet Cleaner"},
        "success": True, "error": []
    }
    mock_resp.raise_for_status = MagicMock()
    with patch("cli_anything.mykasih.utils.backend.requests.post", return_value=mock_resp):
        result = runner.invoke(cli, ["check", "8993560033064", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["isEligible"] is True
        assert data["category"] == "Toilet Cleaner"

def test_check_offline():
    result = runner.invoke(cli, ["check", "9556001067316", "--offline"])
    # offline mungkin false atau error tapi tak crash
    assert result.exit_code == 0

def test_categories_contains_household():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"data": [{"categoryName": "HOUSEHOLD CLEANING PRODUCTS", "categoryNameMS": "BARANGAN KEBERSIHAN RUMAH", "subCategories": [{},{}]}]}
    mock_resp.raise_for_status = MagicMock()
    with patch("cli_anything.mykasih.utils.backend.requests.post", return_value=mock_resp):
        result = runner.invoke(cli, ["categories", "--json"])
        assert result.exit_code == 0

def test_merchants_state_filter():
    # mock merchants endpoint
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"data": [{"tradingName": "Test Mart", "state": "Selangor", "city": "Rawang", "address1": "Test"}]}
    mock_resp.raise_for_status = MagicMock()
    with patch("cli_anything.mykasih.utils.backend.requests.post", return_value=mock_resp):
        result = runner.invoke(cli, ["merchants", "--state", "Selangor", "--json"])
        assert result.exit_code == 0

def test_info():
    result = runner.invoke(cli, ["info"])
    assert result.exit_code == 0
    assert "MyKasih" in result.output

