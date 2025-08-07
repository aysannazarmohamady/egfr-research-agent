import requests
from bs4 import BeautifulSoup
import time
import random
from typing import List, Optional
from .interfaces import ISearchEngine, SearchResult, SearchResultType
from .ai_implementations import GeminiKeywordExtractor
import os
