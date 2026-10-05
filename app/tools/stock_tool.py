import httpx
from langchain_core.tools import tool
from tenacity import retry, wait_exponential, stop_after_attempt

from app.config import ALPHAVANTAGE_API_KEY


@tool
@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3), reraise=True)
async def get_stock_price(symbol: str) -> dict:
    """
    fetch the latest stock price for a given symbol (e.g. 'AAPL', 'TSLA')
    using Alpha vantage using the URL with API key.
    """
    api_key = ALPHAVANTAGE_API_KEY
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
    if "Global Quote" in data:
        return {
            "symbol": symbol,
            "today_price": data["Global Quote"]["05. price"],
            "last_price": data["Global Quote"]["02. open"],
            "change": data["Global Quote"]["09. change"],
            "change_percent": data["Global Quote"]["10. change percent"],
        }
    else:
        raise ValueError(f"Could not fetch stock price for symbol: {symbol}")