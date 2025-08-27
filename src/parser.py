# src/parser.py
from typing import List, Dict
from bs4 import BeautifulSoup
from src.utils.currency import parse_gbp_text

def parse_page(html: str) -> List[Dict[str, str]]:
    """
    Parse a 'Books to Scrape' page and extract fields.
    Emits a numeric Price_GBP ready for conversion.
    """
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    rows: List[Dict[str, str]] = []

    for item in soup.select("article.product_pod"):
        text = item.select_one("span.text").get_text(strip=True)
        author = item.select_one("small.author").get_text(strip=True)
        tags = [tag.get_text(strip=True) for tag in item.select("div.tags a.tag")]
        about_rel = item.select_one("span > a")["href"]

        rows.append({
            "Quote": text,
            "Author": author,
            "Tags": ", ".join(tags),
            "Author_About": about_rel,
        })

    return rows
