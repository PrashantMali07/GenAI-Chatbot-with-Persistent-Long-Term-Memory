from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

wikipedia_wrapper = WikipediaAPIWrapper(top_k_results=3, doc_content_chars_max=250)    
wikipedia_tool = WikipediaQueryRun(api_wrapper=wikipedia_wrapper)