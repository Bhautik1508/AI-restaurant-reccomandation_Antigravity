import os
import pytest
import pandas as pd
import faiss
from backend.ingest_data import DATA_DIR, METADATA_FILE, INDEX_FILE

def test_data_artifacts_exist():
    """Test if ingestion script created necessary files."""
    assert os.path.exists(DATA_DIR), "Data directory missing"
    assert os.path.exists(METADATA_FILE), "Metadata pickle file missing"
    assert os.path.exists(INDEX_FILE), "FAISS index file missing"

def test_metadata_integrity():
    """Test if metadata can be loaded and has correct columns."""
    df = pd.read_pickle(METADATA_FILE)
    assert not df.empty, "Metadata DataFrame is empty"
    
    expected_cols = ['name', 'url', 'combined_text']
    for col in expected_cols:
        assert col in df.columns, f"Missing column: {col}"

def test_faiss_index_integrity():
    """Test if FAISS index is readable and has correct dimensions."""
    index = faiss.read_index(INDEX_FILE)
    assert index.ntotal > 0, "Index is empty"
    # miniLM-L6-v2 has 384 dimensions
    assert index.d == 384, f"Unexpected index dimension: {index.d}"
