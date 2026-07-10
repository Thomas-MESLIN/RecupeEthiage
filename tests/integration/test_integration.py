"""
Integration tests for the project.
"""
import pytest
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import src.processing.station as station
import src.processing.clean as clean
import src.plotting.plot_grandeur as plot_grandeur
from src.model.enums import GeographicScaleClip, MeteoFranceDataType


class TestStationIntegration:
    """Integration tests for station module"""
    
    @pytest.mark.integration
    @patch('src.processing.station.download_Hubeau.ensure_station_downloaded')
    @patch('src.processing.station.download_Hubeau.ensure_sites_downloaded')
    @patch('src.processing.station.utils.get_path_stations')
    @patch('src.processing.station.utils.get_path_sites')
    def test_get_stations_integration(self, mock_get_sites, mock_get_stations, mock_ensure_sites, mock_ensure_stations, temp_dir):
        """Integration test for get_stations function."""
        # Setup mocks
        stations_path = temp_dir / "stations.csv"
        sites_path = temp_dir / "sites.csv"
        
        mock_get_stations.return_value = stations_path
        mock_get_sites.return_value = sites_path
        mock_ensure_stations.return_value = None
        mock_ensure_sites.return_value = None
        
        # Create test data
        stations_data = pd.DataFrame({
            "code_station": ["S001", "S002", "S003"],
            "code_site": ["SiteA", "SiteB", "SiteC"],
            "code_sandre_reseau_station": ["BSH001", "BSH001", "BSH002"],
            "date_ouverture_station": ["1990-01-01", "1995-01-01", "2000-01-01"],
            "date_fermeture_station": [None, "2020-12-31", None],
            "geometry": ["POINT (1 1)", "POINT (2 2)", "POINT (3 3)"]
        })
        
        sites_data = pd.DataFrame({
            "code_site": ["SiteA", "SiteB", "SiteC"],
            "libelle_site": ["Alpha", "Beta", "Gamma"],
            "geometry": ["POINT (1 1)", "POINT (2 2)", "POINT (3 3)"]
        })
        
        stations_path.write_csv(stations_data, index=False)
        sites_path.write_csv(sites_data, index=False)
        
        with patch('pandas.read_csv') as mock_read:
            def read_side_effect(path, **kwargs):
                path_str = str(path)
                if "stations" in path_str:
                    return stations_data
                elif "sites" in path_str:
                    return sites_data
                return pd.DataFrame()
            
            mock_read.side_effect = read_side_effect
            
            result = station.get_stations("BSH001", "2023-06")
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 2  # Only BSH001 stations


class TestCleanIntegration:
    """Integration tests for clean module"""
    
    @pytest.mark.integration
    @patch('src.processing.clean.download_Hubeau.ensure_grandeur_mensuel_downloaded')
    @patch('src.processing.clean.station.get_stations')
    @patch('src.processing.clean.utils.get_path_mensuel_raw_csv')
    def test_clean_hubeau_data_integration(self, mock_get_path, mock_get_stations, mock_ensure_downloaded, temp_dir):
        """Integration test for clean_hubeau_data function."""
        # Setup mocks
        mock_get_path.return_value = temp_dir / "observations-QmnJ-AURA-2023-06.csv"
        mock_ensure_downloaded.return_value = None
        
        # Create test data
        stations_data = pd.DataFrame({
            "code_station": ["S001", "S002"],
            "code_site": ["SiteA", "SiteB"],
            "geometry": ["POINT (1 1)", "POINT (2 2)"]
        })
        
        observations_data = pd.DataFrame({
            "code_station": ["S001", "S002", "S003"],
            "code_site": ["SiteA", "SiteB", "SiteC"],
            "date_obs_elab": ["2023-06-01", "2023-06-02", "2023-06-03"],
            "resultat_obs_elab": [10.5, 20.3, 15.2]
        })
        
        mock_get_stations.return_value = stations_data
        
        with patch('pandas.read_csv', return_value=observations_data):
            result = clean.clean_hubeau_data(
                date_a_filtrer="2023-06",
                code_sandre="BSH001",
                path_file_to_clean=mock_get_path.return_value,
                grandeur_a_filtrer="QmnJ"
            )
            
            assert isinstance(result, pd.DataFrame)
            # Should filter to only stations in the stations list
            assert len(result) == 2


class TestPlottingIntegration:
    """Integration tests for plotting modules"""
    
    @pytest.mark.integration
    def test_create_geojson_from_path(self, temp_dir):
        """Integration test for create_geojson_from_path function."""
        # Create test data
        test_csv = temp_dir / "test_data.csv"
        test_data = pd.DataFrame({
            "code_station": ["S001", "S002"],
            "code_site": ["SiteA", "SiteB"],
            "hydraulicite": [0.8, 0.9],
            "geometry": ["POINT (1 1)", "POINT (2 2)"]
        })
        test_csv.write_csv(test_data, index=False)
        
        output_path = temp_dir / "test_output.geojson"
        
        with patch('src.processing.station.get_stations') as mock_get_stations:
            with patch('src.io.download_Hubeau.ensure_sites_downloaded'):
                with patch('src.utils.utils.get_path_sites') as mock_get_sites:
                    mock_get_stations.return_value = pd.DataFrame({
                        "code_station": ["S001", "S002"],
                        "code_site": ["SiteA", "SiteB"],
                        "geometry": ["POINT (1 1)", "POINT (2 2)"]
                    })
                    mock_get_sites.return_value = temp_dir / "sites.csv"
                    
                    with patch('pandas.read_csv') as mock_read:
                        def read_side_effect(path, **kwargs):
                            if "sites" in str(path):
                                return pd.DataFrame({
                                    "code_site": ["SiteA", "SiteB"],
                                    "libelle_site": ["Alpha", "Beta"],
                                    "geometry": ["POINT (1 1)", "POINT (2 2)"]
                                })
                            return pd.DataFrame()
                        
                        mock_read.side_effect = read_side_effect
                        
                        plot_grandeur.create_geojson_from_path(
                            test_csv,
                            output_path,
                            "2023-06",
                            "BSH001"
                        )
                        
                        # Check that output file was created
                        assert output_path.exists()


class TestEndToEndFlow:
    """End-to-end flow tests"""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_data_processing_flow(self):
        """Test a complete data processing flow."""
        # This test demonstrates how the modules work together
        
        # 1. Create test data
        stations_data = pd.DataFrame({
            "code_station": ["S001", "S002", "S003"],
            "code_site": ["SiteA", "SiteB", "SiteC"],
            "code_sandre_reseau_station": ["BSH001", "BSH001", "BSH002"],
            "date_ouverture_station": ["1990-01-01", "1995-01-01", "2000-01-01"],
            "date_fermeture_station": [None, "2020-12-31", None],
            "en_service": [True, False, True],
            "geometry": ["POINT (1 1)", "POINT (2 2)", "POINT (3 3)"]
        })
        
        # 2. Filter stations by code_sandre
        bsh001_stations = stations_data[
            stations_data["code_sandre_reseau_station"].astype(str).str.contains("BSH001")
        ]
        assert len(bsh001_stations) == 2
        
        # 3. Filter stations by date
        active_stations = bsh001_stations[
            ((bsh001_stations["date_fermeture_station"].isna()) | 
             ("2023-06" < bsh001_stations["date_fermeture_station"].astype(str))) &
            (bsh001_stations["date_ouverture_station"].astype(str) < "2023-06")
        ]
        assert len(active_stations) == 1  # S001 is active, S002 is closed
        
        # 4. Test observation data filtering
        observations_data = pd.DataFrame({
            "code_station": ["S001", "S002", "S003", "S001"],
            "code_site": ["SiteA", "SiteB", "SiteC", "SiteA"],
            "date_obs_elab": ["2023-06-01", "2023-06-01", "2023-06-01", "2023-06-02"],
            "resultat_obs_elab": [10.5, 20.3, 15.2, 12.8],
            "geometry": ["POINT (1 1)", "POINT (2 2)", "POINT (3 3)", "POINT (1 1)"]
        })
        
        # Filter by date and station
        filtered_obs = observations_data[
            observations_data["date_obs_elab"].astype(str).str.contains("2023-06") &
            observations_data["code_station"].isin(active_stations["code_station"])
        ]
        assert len(filtered_obs) == 2


class TestDataQualityChecks:
    """Tests for data quality and validation"""
    
    @pytest.mark.integration
    def test_data_completeness_check(self):
        """Test data completeness checks."""
        # Create a DataFrame with some missing data
        df = pd.DataFrame({
            "code_station": ["S001", "S002", "S003", "S004"],
            "date_obs_elab": ["2023-06-01", "2023-06-02", "2023-06-03", "2023-06-04"],
            "resultat_obs_elab": [10.5, None, 15.2, 12.8],
            "code_site": ["SiteA", "SiteB", None, "SiteD"]
        })
        
        # Check for missing values
        missing_values = df.isnull().sum()
        assert missing_values["resultat_obs_elab"] == 1
        assert missing_values["code_site"] == 1
        
        # Remove rows with missing essential data
        clean_df = df.dropna(subset=["resultat_obs_elab", "code_site"])
        assert len(clean_df) == 2
    
    @pytest.mark.integration
    def test_duplicate_removal(self):
        """Test duplicate removal."""
        df = pd.DataFrame({
            "code_station": ["S001", "S001", "S002", "S002"],
            "date_obs_elab": ["2023-06-01", "2023-06-01", "2023-06-02", "2023-06-02"],
            "resultat_obs_elab": [10.5, 10.5, 20.3, 20.3],
            "code_site": ["SiteA", "SiteA", "SiteB", "SiteB"]
        })
        
        # Remove duplicates
        clean_df = df.drop_duplicates(subset=["code_station", "date_obs_elab"])
        assert len(clean_df) == 2
    
    @pytest.mark.integration
    def test_data_type_validation(self):
        """Test data type validation."""
        df = pd.DataFrame({
            "code_station": ["S001", "S002", "S003"],
            "date_obs_elab": ["2023-06-01", "2023-06-02", "2023-06-03"],
            "resultat_obs_elab": ["10.5", "20.3", "15.2"]  # Strings instead of floats
        })
        
        # Convert to correct types
        df["resultat_obs_elab"] = pd.to_numeric(df["resultat_obs_elab"], errors='coerce')
        
        # Check types
        assert df["code_station"].dtype == object
        assert df["date_obs_elab"].dtype == object
        assert pd.api.types.is_float_dtype(df["resultat_obs_elab"])
