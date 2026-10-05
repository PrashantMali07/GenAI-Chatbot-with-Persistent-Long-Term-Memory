"""
Unit tests for the custom agent tools.

These tests do NOT require a running backend or database — they
exercise the tool logic with mocked external calls.
"""

from unittest.mock import MagicMock, AsyncMock, patch

import pytest
import httpx

from app.tools.calculator_tool import calculator
from app.tools.stock_tool import get_stock_price
from app.tools.url_tool import get_url_content

# ---------------------------------------------------------------------------
# Calculator
# ---------------------------------------------------------------------------


def test_calculator_add():
    assert calculator.invoke({"num1": 3, "num2": 4, "operation": "add"}) == 7.0


def test_calculator_subtract():
    assert calculator.invoke({"num1": 10, "num2": 3, "operation": "subtract"}) == 7.0


def test_calculator_multiply():
    assert calculator.invoke({"num1": 6, "num2": 7, "operation": "multiply"}) == 42.0


def test_calculator_divide():
    assert calculator.invoke({"num1": 10, "num2": 4, "operation": "divide"}) == 2.5


def test_calculator_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calculator.invoke({"num1": 5, "num2": 0, "operation": "divide"})


# ---------------------------------------------------------------------------
# Stock tool — mock the external HTTP call
# ---------------------------------------------------------------------------

MOCK_STOCK_RESPONSE = {
    "Global Quote": {
        "01. symbol": "AAPL",
        "02. open": "170.00",
        "05. price": "175.00",
        "09. change": "5.00",
        "10. change percent": "2.94%",
    }
}


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get", new_callable=AsyncMock)
async def test_get_stock_price_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.json.return_value = MOCK_STOCK_RESPONSE
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    result = await get_stock_price.ainvoke({"symbol": "AAPL"})
    assert result["symbol"] == "AAPL"
    assert result["today_price"] == "175.00"
    assert result["change"] == "5.00"


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get", new_callable=AsyncMock)
async def test_get_stock_price_bad_symbol(mock_get):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"Note": "API limit reached"}
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    with pytest.raises(ValueError, match="Could not fetch stock price"):
        await get_stock_price.ainvoke({"symbol": "INVALID"})


# ---------------------------------------------------------------------------
# URL tool — mock httpx
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get", new_callable=AsyncMock)
async def test_get_url_content_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = "<html><body><p>Hello World</p></body></html>"
    mock_get.return_value = mock_resp

    result = await get_url_content.ainvoke({"url": "https://example.com"})
    assert "Hello World" in result


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get", new_callable=AsyncMock)
async def test_get_url_content_http_error(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_get.return_value = mock_resp

    result = await get_url_content.ainvoke({"url": "https://example.com/notfound"})
    assert "404" in result
