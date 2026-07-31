from .calculator_tool import calculator
from .wikipedia_tool import wikipedia_tool
from .arxiv_tool import arxiv_tool
from .url_tool import get_url_content
from .stock_tool import get_stock_price
from .web_search_tool import web_search_tool
from .memory_tool import recall_memory
from .google_search_tool import google_search

all_tools = [calculator, wikipedia_tool, arxiv_tool, get_url_content, get_stock_price, web_search_tool, recall_memory, google_search]