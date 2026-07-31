from langchain_community.tools import DuckDuckGoSearchRun

web_search_tool = DuckDuckGoSearchRun(region="us-en", top_k_results=3, doc_content_chars_max=250)