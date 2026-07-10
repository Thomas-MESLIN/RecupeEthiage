"""
Unit tests for the CLI module.
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime
import argparse
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.cli.utils import (
    demander_ou_non,
    demander_avec_choix,
    demander_date,
    formater_date_vers_datetime
)
import src.cli.main_cli as main_cli


class TestCLIUtils:
    """Tests for cli/utils.py"""
    
    def test_demander_ou_non_yes(self, monkeypatch):
        """Test demander_ou_non with 'yes' response."""
        monkeypatch.setattr('builtins.input', lambda _: "yes")
        result = demander_ou_non("Test question?")
        assert result == True
    
    def test_demander_ou_non_no(self, monkeypatch):
        """Test demander_ou_non with 'no' response."""
        monkeypatch.setattr('builtins.input', lambda _: "no")
        result = demander_ou_non("Test question?")
        assert result == False
    
    def test_demander_ou_non_default_yes(self, monkeypatch):
        """Test demander_ou_non with empty response (default yes)."""
        monkeypatch.setattr('builtins.input', lambda _: "")
        result = demander_ou_non("Test question?", valeur_par_defaut=True)
        assert result == True
    
    def test_demander_ou_non_default_no(self, monkeypatch):
        """Test demander_ou_non with empty response (default no)."""
        monkeypatch.setattr('builtins.input', lambda _: "")
        result = demander_ou_non("Test question?", valeur_par_defaut=False)
        assert result == False
    
    def test_demander_avec_choix_valid(self, monkeypatch):
        """Test demander_avec_choix with valid choice."""
        options = {"1": "Option 1", "2": "Option 2"}
        monkeypatch.setattr('builtins.input', lambda _: "1")
        result = demander_avec_choix("Test question?", options)
        assert result == "1"
    
    def test_demander_avec_choix_default(self, monkeypatch):
        """Test demander_avec_choix with default choice."""
        options = {"1": "Option 1", "2": "Option 2"}
        monkeypatch.setattr('builtins.input', lambda _: "")
        result = demander_avec_choix("Test question?", options, valeur_par_defaut="2")
        assert result == "2"
    
    def test_demander_avec_choix_no_default(self, monkeypatch):
        """Test demander_avec_choix with no default (first option)."""
        options = {"1": "Option 1", "2": "Option 2"}
        monkeypatch.setattr('builtins.input', lambda _: "")
        result = demander_avec_choix("Test question?", options)
        assert result == "1"
    
    def test_demander_date_valid_yyyy_mm(self, monkeypatch):
        """Test demander_date with valid YYYY-MM format."""
        default_date = datetime(2023, 6, 1)
        monkeypatch.setattr('builtins.input', lambda _: "2023-07")
        result = demander_date("Test date?", "AAAA-MM", default_date)
        assert result == datetime(2023, 7, 1)
    
    def test_demander_date_valid_yyyy_mm_dd(self, monkeypatch):
        """Test demander_date with valid YYYY-MM-DD format."""
        default_date = datetime(2023, 6, 1)
        monkeypatch.setattr('builtins.input', lambda _: "2023-07-15")
        result = demander_date("Test date?", "AAAA-MM-JJ", default_date)
        assert result == datetime(2023, 7, 15)
    
    def test_demander_date_empty(self, monkeypatch):
        """Test demander_date with empty response (use default)."""
        default_date = datetime(2023, 6, 1)
        monkeypatch.setattr('builtins.input', lambda _: "")
        result = demander_date("Test date?", "AAAA-MM", default_date)
        assert result == default_date
    
    def test_demander_date_invalid(self, monkeypatch):
        """Test demander_date with invalid format."""
        default_date = datetime(2023, 6, 1)
        monkeypatch.setattr('builtins.input', lambda _: "invalid-date")
        result = demander_date("Test date?", "AAAA-MM", default_date)
        assert result == default_date
    
    def test_formater_date_vers_datetime_yyyy_mm_debut(self):
        """Test formater_date_vers_datetime with YYYY-MM for start date."""
        result = formater_date_vers_datetime("2023-06", est_debut=True)
        assert result == datetime(2023, 6, 1)
    
    def test_formater_date_vers_datetime_yyyy_mm_fin(self):
        """Test formater_date_vers_datetime with YYYY-MM for end date."""
        result = formater_date_vers_datetime("2023-06", est_debut=False)
        assert result == datetime(2023, 6, 30)
    
    def test_formater_date_vers_datetime_yyyy_mm_dd(self):
        """Test formater_date_vers_datetime with YYYY-MM-DD format."""
        result = formater_date_vers_datetime("2023-06-15", est_debut=True)
        assert result == datetime(2023, 6, 15)
    
    def test_formater_date_vers_datetime_invalid(self):
        """Test formater_date_vers_datetime with invalid format."""
        result = formater_date_vers_datetime("invalid", est_debut=True)
        assert result is None


class TestMainCLI:
    """Tests for main_cli.py"""
    
    @patch('src.cli.main_cli.mode_interactif')
    def test_run_no_type(self, mock_mode_interactif):
        """Test run() with no type specified (interactive mode)."""
        with patch('sys.argv', ['script.py']):
            with patch.object(main_cli, 'run') as mock_run:
                # Mock the argparse to return None for type
                with patch('argparse.ArgumentParser') as mock_parser:
                    mock_args = MagicMock()
                    mock_args.type = None
                    mock_parser.return_value.parse_args.return_value = mock_args
                    
                    main_cli.run()
                    
                    # Should call mode_interactif
                    mock_mode_interactif.assert_called_once()
    
    @patch('src.cli.main_cli.mode_cli')
    def test_run_with_type(self, mock_mode_cli):
        """Test run() with type specified (CLI mode)."""
        with patch('sys.argv', ['script.py', '--type', 'hydraulicite']):
            with patch('argparse.ArgumentParser') as mock_parser:
                mock_args = MagicMock()
                mock_args.type = 'hydraulicite'
                mock_parser.return_value.parse_args.return_value = mock_args
                
                main_cli.run()
                
                # Should call mode_cli
                mock_mode_cli.assert_called_once()
    
    @patch('src.cli.main_cli.formater_date_vers_datetime')
    def test_mode_cli_date_parsing(self, mock_formater):
        """Test mode_cli with date parsing."""
        # Setup mocks
        mock_formater.side_effect = [
            datetime(2023, 6, 1),  # start_date
            datetime(2023, 6, 30)   # end_date
        ]
        
        with patch('argparse.Namespace') as mock_namespace:
            mock_args = MagicMock()
            mock_args.type = 'hydraulicite'
            mock_args.start_date = '2023-06'
            mock_args.end_date = '2023-06'
            mock_args.reseau_sandre = 'BSH001'
            mock_args.vcn3_graphic = False
            mock_args.meteo_aggregate = False
            mock_args.meteo_no_index_update = False
            mock_args.meteo_no_update = False
            mock_args.geographic_scale = None
            mock_args.onde_zone_code = None
            
            with patch('src.cli.main_cli.main') as mock_main:
                main_cli.mode_cli(mock_args)
                
                # Check that main was called with correct arguments
                mock_main.assert_called_once()
                call_args = mock_main.call_args
                assert call_args[1]['type_carte'] == 'hydraulicite'
    
    def test_main_function_routing(self):
        """Test main function routing to correct handlers."""
        with patch('src.plotting.plot_grandeur.create_geojson_from_hydraulicite') as mock_hydro:
            with patch('src.plotting.plot_grandeur.create_geojson_from_periode_de_retour') as mock_vcn3:
                with patch('src.plotting.plot_meteoFrance.export_all_format_geojson_range') as mock_meteo:
                    with patch('src.plotting.plot_onde.plot_everything') as mock_onde:
                        with patch('src.cli.main_cli.clear_all_cache'):
                            
                            # Test hydraulicite
                            main_cli.main(
                                type_carte='hydraulicite',
                                start_date=datetime(2023, 6, 1),
                                end_date=datetime(2023, 6, 30),
                                reseau_sandre='BSH001'
                            )
                            mock_hydro.assert_called_once()
                            
                            # Test vcn3
                            main_cli.main(
                                type_carte='vcn3',
                                start_date=datetime(2023, 6, 1),
                                end_date=datetime(2023, 6, 30),
                                reseau_sandre='BSH001'
                            )
                            mock_vcn3.assert_called_once()
