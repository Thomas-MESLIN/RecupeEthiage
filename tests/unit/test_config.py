"""
Unit tests for the config module.
"""
import pytest
import os
import sys
from pathlib import Path
import logging
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.config.paths import ROOT_DIR, OUTPUT_DIR, DATA_DIR, SRC_DIR
from src.config.logging_config import setup_logger
from src.config.styles import COULEUR_MOYENNE, ANNEE_COULEURS
from src.model.enums import GeographicScaleClip, OndeCampagneType, MeteoFranceDataType


class TestPaths:
    """Tests for paths.py"""
    
    def test_root_dir_exists(self, project_root):
        """Test that ROOT_DIR exists."""
        assert ROOT_DIR.exists()
        assert ROOT_DIR.is_dir()
    
    def test_root_dir_is_project_root(self, project_root):
        """Test that ROOT_DIR is the project root."""
        assert ROOT_DIR == project_root
    
    def test_output_dir_path(self, project_root):
        """Test that OUTPUT_DIR path is correct."""
        expected = project_root / "output"
        assert OUTPUT_DIR == expected
    
    def test_data_dir_path(self, project_root):
        """Test that DATA_DIR path is correct."""
        expected = project_root / "data"
        assert DATA_DIR == expected
    
    def test_src_dir_path(self, project_root):
        """Test that SRC_DIR path is correct."""
        expected = project_root / "src"
        assert SRC_DIR == expected


class TestLoggingConfig:
    """Tests for logging_config.py"""
    
    def test_setup_logger_returns_logger(self, temp_dir):
        """Test that setup_logger returns a logger object."""
        log_file = temp_dir / "test.log"
        logger = setup_logger(name="test", log_file=log_file, level=logging.DEBUG)
        assert isinstance(logger, logging.Logger)
    
    def test_setup_logger_creates_log_file(self, temp_dir):
        """Test that setup_logger creates log files."""
        # Create the logs directory in temp_dir first
        log_dir = temp_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = temp_dir / "test_app.log"
        logger = setup_logger(name="test_create_file", log_file=log_file, level=logging.INFO)
        logger.info("Test message")
        
        # Check if log file was created
        assert log_file.exists()
        
        # Check if log directory was created
        assert log_dir.exists()
    
    def test_setup_logger_creates_error_file(self, temp_dir, monkeypatch):
        """Test that setup_logger creates error log file."""
        # Mock OUTPUT_DIR to use temp_dir
        with monkeypatch.context() as m:
            m.setattr('src.config.logging_config.OUTPUT_DIR', temp_dir)
            
            # Create the logs directory in temp_dir first
            log_dir = temp_dir / "logs"
            log_dir.mkdir(exist_ok=True)
            
            log_file = temp_dir / "test_error.log"
            logger = setup_logger(name="test_error", log_file=log_file, level=logging.ERROR)
            logger.error("Test error message")
            
            error_log = temp_dir / "logs" / "errors.log"
            assert error_log.exists()
    
    def test_setup_logger_no_duplicate_handlers(self, temp_dir):
        """Test that setup_logger doesn't add duplicate handlers."""
        log_file = temp_dir / "test_no_dup.log"
        
        # Call setup_logger twice with the same name
        logger1 = setup_logger(name="test_no_dup", log_file=log_file, level=logging.INFO)
        logger2 = setup_logger(name="test_no_dup", log_file=log_file, level=logging.INFO)
        
        # Should have the same number of handlers
        assert len(logger1.handlers) == len(logger2.handlers)
        
        # Should be the same logger
        assert logger1 is logger2


class TestStyles:
    """Tests for styles.py"""
    
    def test_couleur_moyenne_is_black(self):
        """Test that COULEUR_MOYENNE is black."""
        assert COULEUR_MOYENNE == "#000000"
    
    def test_annee_couleurs_has_correct_years(self):
        """Test that ANNEE_COULEURS has expected years."""
        expected_years = list(range(2012, 2027))  # 2012-2026
        assert set(ANNEE_COULEURS.keys()) == set(expected_years)
    
    def test_annee_couleurs_has_hex_values(self):
        """Test that all color values in ANNEE_COULEURS are valid hex colors."""
        for year, color in ANNEE_COULEURS.items():
            assert isinstance(color, str)
            assert color.startswith("#")
            # Check if it's a valid hex color (3, 4, 6, or 8 characters)
            hex_part = color[1:]
            assert all(c.lower() in "0123456789abcdef" for c in hex_part)
            assert len(hex_part) in [3, 4, 6, 8]
    
    def test_annee_couleurs_current_year_is_red(self):
        """Test that current year (2026) color is red."""
        current_year = datetime.now().year
        if current_year in ANNEE_COULEURS:
            # Red colors typically start with #e, #f, or specific patterns
            assert ANNEE_COULEURS[current_year] == "#ee0000"


class TestEnums:
    """Tests for enums.py"""
    
    def test_geographic_scale_clip_values(self):
        """Test GeographicScaleClip enum values."""
        assert GeographicScaleClip.NATIONAL.value == "NATIONAL"
        assert GeographicScaleClip.BASSIN.value == "BASSIN"
        assert GeographicScaleClip.REGION_ADMINISTRATIVE.value == "REGION_ADMINISTRATIVE"
        assert GeographicScaleClip.DEPARTEMENT_ADMINISTRATIF.value == "DEPARTEMENT_ADMINISTRATIF"
        assert GeographicScaleClip.REGION_BASSIN.value == "REGION_BASSIN"
        assert GeographicScaleClip.DEPARTEMENT_BASSIN.value == "DEPARTEMENT_BASSIN"
    
    def test_onde_campagne_type_values(self):
        """Test OndeCampagneType enum values."""
        assert OndeCampagneType.USUELLE.value == "U"
        assert OndeCampagneType.COMPLEMENTAIRE.value == "C"
        assert OndeCampagneType.ALL_CAMPAGNE.value == "A"
    
    def test_meteo_france_data_type_values(self):
        """Test MeteoFranceDataType enum values."""
        assert MeteoFranceDataType.SIM2_QUOT.value == 1
        assert MeteoFranceDataType.SIM2_MENS.value == 2
        assert MeteoFranceDataType.QUOT.value == 3
        assert MeteoFranceDataType.MENS.value == 4
