"""
Pytest configuration and fixtures for the entire test suite.
"""
import pytest
import os
import sys
from pathlib import Path
import tempfile
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def project_root():
    """Return the project root directory."""
    return PROJECT_ROOT


@pytest.fixture
def output_dir():
    """Return the output directory."""
    return PROJECT_ROOT / "output"


@pytest.fixture
def data_dir():
    """Return the data directory."""
    return PROJECT_ROOT / "data"


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for testing."""
    return tmp_path


@pytest.fixture
def temp_csv_file(temp_dir):
    """Create a temporary CSV file."""
    test_file = temp_dir / "test.csv"
    df = pd.DataFrame({
        "code_station": ["S1", "S2", "S3"],
        "date_obs_elab": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "resultat_obs_elab": [10.5, 20.3, 15.2],
        "code_site": ["Site1", "Site2", "Site3"]
    })
    df.to_csv(test_file, index=False)
    return test_file


@pytest.fixture
def sample_dataframe():
    """Create a sample pandas DataFrame for testing."""
    return pd.DataFrame({
        "code_station": ["S1", "S2", "S3", "S4"],
        "date_obs_elab": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04"],
        "resultat_obs_elab": [10.5, 20.3, 15.2, 12.8],
        "code_site": ["Site1", "Site2", "Site3", "Site4"],
        "longitude": [2.35, 2.36, 2.37, 2.38],
        "latitude": [48.85, 48.86, 48.87, 48.88],
        "geometry": ["POINT (2.35 48.85)", "POINT (2.36 48.86)", "POINT (2.37 48.87)", "POINT (2.38 48.88)"]
    })


@pytest.fixture
def empty_dataframe():
    """Create an empty pandas DataFrame."""
    return pd.DataFrame()


@pytest.fixture
def sample_stations_dataframe():
    """Create a sample stations DataFrame."""
    return pd.DataFrame({
        "code_station": ["S001", "S002", "S003"],
        "code_site": ["SiteA", "SiteB", "SiteC"],
        "code_sandre_reseau_station": ["BSH001", "BSH001", "BSH002"],
        "date_ouverture_station": ["1990-01-01", "1995-01-01", "2000-01-01"],
        "date_fermeture_station": [None, "2020-12-31", None],
        "en_service": [True, False, True],
        "geometry": ["POINT (1 1)", "POINT (2 2)", "POINT (3 3)"]
    })

@pytest.fixture
def sample_custom_site_dataframe():
    """Create a sample stations DataFrame."""
    return pd.DataFrame({
        "code_site": ["U0230010", "U0415010", "U0474010"]
    })

@pytest.fixture
def sample_custom_stations_dataframe():
    """Create a sample stations DataFrame."""
    return pd.DataFrame({
        "code_station": ["U023001001", "U041501001", "U044431001"]
    })

@pytest.fixture
def sample_sites_dataframe():
    """Create a sample sites DataFrame."""
    return pd.DataFrame({
        "code_site": ["SiteA", "SiteB", "SiteC"],
        "libelle_site": ["Site Alpha", "Site Beta", "Site Gamma"],
        "geometry": ["POINT (1 1)", "POINT (2 2)", "POINT (3 3)"]
    })


@pytest.fixture
def sample_vcn3_data():
    """Create sample VCN3 data for testing."""
    np.random.seed(42)
    return np.random.rand(30) * 10  # 30 random values between 0 and 10


@pytest.fixture
def mock_date():
    """Provide a sample date for testing."""
    return datetime(2023, 6, 15)


@pytest.fixture
def mock_annee_mois():
    """Provide a sample year-month string."""
    return "2023-06"


@pytest.fixture
def mock_code_sandre():
    """Provide a sample code sandre."""
    return "BSH001"


# Mock environment variables
@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch, temp_dir):
    """Setup test environment with mocked directories."""
    # Mock OUTPUT_DIR and DATA_DIR to use temp directory
    with monkeypatch.context() as m:
        m.setenv("OUTPUT_DIR", str(temp_dir / "output"))
        m.setenv("DATA_DIR", str(temp_dir / "data"))
        yield
