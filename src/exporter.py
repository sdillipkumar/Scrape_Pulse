"""
Exporter functions for saving scraped data.
"""

import pandas as pd
from typing import List, Dict


def save_to_csv(data: List[Dict[str, str]], output: str) -> None:
    """
    Save scraped data to a CSV file.

    Args:
        data (List[Dict[str, str]]): Extracted product data.
        output (str): Path to save CSV file.
    """
    df = pd.DataFrame(data)
    df.to_csv(output, index=False)
    print(f"Data saved to {output}")
