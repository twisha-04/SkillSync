# utils/dataset_search.py
import pandas as pd
from typing import Union, List

def dataset_search(dataset_path: str, query: str, columns: Union[str, List[str]] = None, top_k: int = 5):
    """
    Simple text-based dataset search.
    :param dataset_path: path to CSV/Excel dataset
    :param query: search query
    :param columns: columns to search in (default: all)
    :param top_k: number of results to return
    """
    if dataset_path.endswith(".csv"):
        df = pd.read_csv(dataset_path)
    elif dataset_path.endswith(".xlsx"):
        df = pd.read_excel(dataset_path)
    else:
        raise ValueError("Unsupported dataset format. Use CSV or XLSX.")

    if columns:
        df = df[columns]

    # Convert to text for fuzzy search
    query_lower = query.lower()
    df["combined_text"] = df.astype(str).agg(" ".join, axis=1)
    df["score"] = df["combined_text"].apply(lambda x: query_lower in x.lower())

    top_results = df[df["score"]].head(top_k)
    return top_results.drop(columns=["combined_text", "score"], errors="ignore")
