from .analysis_1 import linear_regression_analysis
from .visualization_1 import get_visualization_1
from .visualization_2 import get_visualization_2
from .analysis_2 import sentiment_analysis
from .nvidia_fintimes_scrape import scrape_nvidia_ft
from .nvidia_stock_values_api import scrape_nvidia_stock
from .nvidia_news_api import get_nvidia_news_via_api
from .nvidia_originalsite_scrape import scrape_nvidia_news_site

# Exposing specific functions at the package level
__all__ = [
    'linear_regression_analysis',
    'get_visualization_1',
    'get_visualization_2',
    'sentiment_analysis',
    'scrape_nvidia_ft',
    'scrape_nvidia_stock',
    'get_nvidia_news_via_api',
    'scrape_nvidia_news_site'
]