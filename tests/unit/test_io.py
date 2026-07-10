"""
Unit tests for the IO module.
"""
import pytest
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.model.enums import GeographicScaleClip, MeteoFranceDataType


class TestDownloadHubeau:
    """Tests for download_Hubeau.py"""
    
    @patch('src.io.download_Hubeau.utils.get_path_mensuel_raw_csv')
    @patch('src.io.download_Hubeau.utils_file.is_file_need_download')
    @patch('src.io.download_Hubeau.download_hubeau_AURA_mois')
    def test_ensure_grandeur_mensuel_downloaded(self, mock_download, mock_need_download, mock_get_path):
        """Test ensure_grandeur_mensuel_downloaded function."""
        mock_get_path.return_value = Path("mock/observations-QmnJ-AURA-2023-06.csv")
        mock_need_download.return_value = False
        mock_download.return_value = None
        
        # Import here to avoid import-time side effects
        import src.io.download_Hubeau as download_Hubeau
        
        download_Hubeau.ensure_grandeur_mensuel_downloaded("2023-06", "QmnJ")
        
        # Should not call download if file doesn't need download
        mock_download.assert_not_called()
    
    @patch('src.io.download_Hubeau.utils.get_path_mensuel_raw_csv')
    @patch('src.io.download_Hubeau.utils_file.is_file_need_download')
    @patch('src.io.download_Hubeau.download_hubeau_AURA_mois')
    def test_ensure_grandeur_mensuel_downloaded_needs_download(self, mock_download, mock_need_download, mock_get_path):
        """Test ensure_grandeur_mensuel_downloaded when file needs download."""
        mock_get_path.return_value = Path("mock/observations-QmnJ-AURA-2023-06.csv")
        mock_need_download.return_value = True
        mock_download.return_value = None
        
        import src.io.download_Hubeau as download_Hubeau
        
        download_Hubeau.ensure_grandeur_mensuel_downloaded("2023-06", "QmnJ")
        
        # Should call download since file needs download
        mock_download.assert_called_once_with("2023-06", "QmnJ")
    
    def test_download_hubeau_AURA_mois_path_construction(self, temp_dir):
        """Test download_hubeau_AURA_mois path construction."""
        import src.io.download_Hubeau as download_Hubeau
        
        with patch('src.io.download_Hubeau.utils.get_path_mensuel_raw_csv') as mock_get_path:
            with patch('src.io.download_Hubeau.hydrometry.get_observations') as mock_get_obs:
                with patch('src.io.download_Hubeau.utils_proxy.set_up_working_proxy'):
                    mock_get_path.return_value = temp_dir / "test.csv"
                    mock_get_obs.return_value = pd.DataFrame({"col1": [1, 2, 3]})
                    
                    download_Hubeau.download_hubeau_AURA_mois("2023-06", "QmnJ")
                    
                    # Check that DataFrame was saved
                    saved_file = temp_dir / "test.csv"
                    assert saved_file.exists()
    
    def test_get_path_meteofrance_correspondance_departement_id_datagouv_mens_historique(self):
        """Test get_path_meteofrance_correspondance_departement_id_datagouv_mens_historique function."""
        import src.io.download_Hubeau as download_Hubeau
        
        result = download_Hubeau.get_path_meteofrance_correspondance_departement_id_datagouv_mens_historique()
        expected = Path("output/meteoFrance/departement_id_datagouv/MENS_departement_id_datagouv_historique.csv")
        
        # Note: This test might fail if OUTPUT_DIR is different
        # The function uses OUTPUT_DIR from paths.py
        assert isinstance(result, Path)
        assert "MENS_departement_id_datagouv_historique.csv" in str(result)


class TestDownloadMeteoFrance:
    """Tests for download_meteoFrance.py"""
    
    def test_get_geographic_list(self, temp_dir):
        """Test get_geographic_list function."""
        import src.io.download_meteoFrance as download_meteo
        
        # Create mock data files
        basin_file = temp_dir / "liste_bassin.csv"
        basin_file.write_text("code\nB01\nB02\nB03\n")
        
        with patch('src.io.download_meteoFrance.DATA_DIR', temp_dir):
            result = download_meteo.get_geographic_list(GeographicScaleClip.BASSIN)
            
            assert isinstance(result, list)
            assert len(result) == 3
    
    def test_convert_chaine_to_date_year(self):
        """Test convert_chaine_to_date with year format."""
        import src.io.download_meteoFrance as download_meteo
        
        result = download_meteo.convert_chaine_to_date("2023", is_start=True)
        assert result == datetime(2023, 1, 1)
        
        result = download_meteo.convert_chaine_to_date("2023", is_start=False)
        assert result == datetime(2023, 12, 31)
    
    def test_convert_chaine_to_date_month(self):
        """Test convert_chaine_to_date with month format."""
        import src.io.download_meteoFrance as download_meteo
        
        result = download_meteo.convert_chaine_to_date("202306", is_start=True)
        assert result == datetime(2023, 6, 1)
        
        result = download_meteo.convert_chaine_to_date("202306", is_start=False)
        assert result == datetime(2023, 6, 30)
    
    def test_convert_chaine_to_date_full(self):
        """Test convert_chaine_to_date with full date format."""
        import src.io.download_meteoFrance as download_meteo
        
        result = download_meteo.convert_chaine_to_date("20230615", is_start=True)
        assert result == datetime(2023, 6, 15)
    
    def test_get_path_decennie_to_id_datagouv(self):
        """Test get_path_decennie_to_id_datagouv function."""
        import src.io.download_meteoFrance as download_meteo
        
        result = download_meteo.get_path_decennie_to_id_datagouv(MeteoFranceDataType.SIM2_QUOT)
        assert isinstance(result, Path)
        assert "QUOT_SIM2_decennie_to_id_datagouv.csv" in str(result)
        
        result = download_meteo.get_path_decennie_to_id_datagouv(MeteoFranceDataType.SIM2_MENS)
        assert isinstance(result, Path)
        assert "MENS_SIM2_decennie_to_id_datagouv.csv" in str(result)
    
    def test_is_date_overlapping(self):
        """Test is_date_overlapping function."""
        import src.io.download_meteoFrance as download_meteo
        
        # Overlapping dates
        assert download_meteo.is_date_overlapping(
            datetime(2023, 1, 1), datetime(2023, 6, 30),
            datetime(2023, 3, 1), datetime(2023, 9, 30)
        ) == True
        
        # Non-overlapping dates
        assert download_meteo.is_date_overlapping(
            datetime(2023, 1, 1), datetime(2023, 6, 30),
            datetime(2023, 7, 1), datetime(2023, 12, 31)
        ) == False
        
        # Fully contained dates
        assert download_meteo.is_date_overlapping(
            datetime(2023, 1, 1), datetime(2023, 12, 31),
            datetime(2023, 3, 1), datetime(2023, 9, 30)
        ) == True


class TestProxyUtils:
    """Tests for utils_proxy.py"""
    
    @patch('src.utils.utils_proxy.requests.get')
    def test_test_connection_success(self, mock_get):
        """Test test_connection with successful connection."""
        import src.utils.utils_proxy as utils_proxy
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = utils_proxy.test_connection("https://example.com")
        assert result == True
    
    @patch('src.utils.utils_proxy.requests.get')
    def test_test_connection_failure(self, mock_get):
        """Test test_connection with failed connection."""
        import src.utils.utils_proxy as utils_proxy
        
        mock_get.side_effect = Exception("Connection failed")
        
        result = utils_proxy.test_connection("https://example.com")
        assert result == False
    
    @patch('src.utils.utils_proxy.test_connection')
    @patch('src.utils.utils_proxy.load_dotenv')
    @patch('src.utils.utils_proxy.os.unsetenv')
    def test_set_up_working_proxy(self, mock_unsetenv, mock_load_dotenv, mock_test_connection):
        """Test set_up_working_proxy function."""
        import src.utils.utils_proxy as utils_proxy
        
        # Mock test_connection to return False, then True
        mock_test_connection.side_effect = [False, True]
        
        # Should not raise an exception
        utils_proxy.set_up_working_proxy()
        
        # Should have called test_connection twice
        assert mock_test_connection.call_count == 2


class TestFileUtils:
    """Additional tests for utils_file.py"""
    
    @patch('src.utils.utils_file.is_path_valid_age')
    def test_is_file_need_download_new_file(self, mock_valid_age):
        """Test is_file_need_download for new file."""
        import src.utils.utils_file as utils_file
        from pathlib import Path
        
        mock_path = Path("mock/new_file.csv")
        mock_valid_age.return_value = True
        
        with patch.object(Path, 'exists', return_value=True):
            result = utils_file.is_file_need_download(mock_path)
            assert result == False
    
    @patch('src.utils.utils_file.is_path_valid_age')
    def test_is_file_need_download_old_file_renew(self, mock_valid_age, monkeypatch):
        """Test is_file_need_download for old file with renewal."""
        import src.utils.utils_file as utils_file
        from pathlib import Path
        
        mock_path = Path("mock/old_file.csv")
        mock_valid_age.return_value = False
        
        # Mock the prompt to return True (renew)
        monkeypatch.setattr('src.utils.utils_file.prompt_renew_old_data', lambda x: True)
        
        with patch.object(Path, 'exists', return_value=True):
            result = utils_file.is_file_need_download(mock_path)
            assert result == True
    
    @patch('src.utils.utils_file.is_path_valid_age')
    def test_is_file_need_download_old_file_no_renew(self, mock_valid_age, monkeypatch):
        """Test is_file_need_download for old file without renewal."""
        import src.utils.utils_file as utils_file
        from pathlib import Path
        
        mock_path = Path("mock/old_file.csv")
        mock_valid_age.return_value = False
        
        # Mock the prompt to return False (don't renew)
        monkeypatch.setattr('src.utils.utils_file.prompt_renew_old_data', lambda x: False)
        
        with patch.object(Path, 'exists', return_value=True):
            result = utils_file.is_file_need_download(mock_path)
            assert result == False
    
    def test_is_file_need_download_nonexistent_file(self, temp_dir):
        """Test is_file_need_download for non-existent file."""
        import src.utils.utils_file as utils_file
        
        mock_path = temp_dir / "nonexistent.csv"
        
        result = utils_file.is_file_need_download(mock_path)
        assert result == True
    
    def test_is_res_updated_with_source(self, temp_dir):
        """Test is_res_updated_with_source function."""
        import src.utils.utils_file as utils_file
        from datetime import datetime, timedelta
        
        # Create source and result files
        source1 = temp_dir / "source1.csv"
        source2 = temp_dir / "source2.csv"
        result_file = temp_dir / "result.csv"
        
        # Create files
        source1.write_text("test")
        source2.write_text("test")
        result_file.write_text("test")
        
        # Mock file modification times
        old_time = datetime.now() - timedelta(hours=2)
        new_time = datetime.now() - timedelta(hours=1)
        
        with patch.object(source1, 'stat') as mock_source1_stat:
            with patch.object(source2, 'stat') as mock_source2_stat:
                with patch.object(result_file, 'stat') as mock_result_stat:
                    
                    # Result is newer than sources
                    mock_source1_stat.return_value.st_mtime = old_time.timestamp()
                    mock_source2_stat.return_value.st_mtime = old_time.timestamp()
                    mock_result_stat.return_value.st_mtime = new_time.timestamp()
                    
                    result = utils_file.is_res_updated_with_source(
                        [source1, source2],
                        result_file
                    )
                    
                    assert result == True
        
        with patch.object(source1, 'stat') as mock_source1_stat:
            with patch.object(source2, 'stat') as mock_source2_stat:
                with patch.object(result_file, 'stat') as mock_result_stat:
                    
                    # Result is older than sources
                    mock_source1_stat.return_value.st_mtime = new_time.timestamp()
                    mock_source2_stat.return_value.st_mtime = new_time.timestamp()
                    mock_result_stat.return_value.st_mtime = old_time.timestamp()
                    
                    result = utils_file.is_res_updated_with_source(
                        [source1, source2],
                        result_file
                    )
                    
                    assert result == False
