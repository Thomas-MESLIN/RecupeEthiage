"""
Unit tests for the plotting module.
"""
import pytest
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
from unittest.mock import patch, MagicMock
import tempfile

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import src.plotting.plot_grandeur as plot_grandeur
import src.plotting.plot_meteoFrance as plot_meteoFrance
import src.plotting.plot_onde as plot_onde
from src.model.enums import GeographicScaleClip, OndeCampagneType, MeteoFranceDataType
from src.processing.meteoFrance_aggregation_donnee import GroupByMethod


class TestPlotGrandeur:
    """Tests for plot_grandeur.py"""
    
    def test_print_results(self, capsys):
        """Test print_results function."""
        res = {
            "y": np.array([1, 2, 3, 4, 5]),
            "z": np.array([1, 2, 3, 4, 5]),
            "p0": 0.1,
            "mu": 1.0,
            "sigma": 0.5,
            "params": (0.5, 0.0, 1.0),
            "empirical": {
                "y_sorted": np.array([1, 2, 3, 4, 5]),
                "freq": np.array([0.1, 0.3, 0.5, 0.7, 0.9]),
                "T": np.array([10, 3.3, 2, 1.4, 1.1])
            },
            "quantiles": {
                "T": np.array([2, 5, 10]),
                "p": np.array([0.5, 0.2, 0.1]),
                "q": np.array([1.5, 2.5, 3.5]),
                "IC_low": np.array([1.0, 2.0, 3.0]),
                "IC_high": np.array([2.0, 3.0, 4.0])
            },
            "pcdf": {
                "x": np.array([0, 1, 2, 3, 4, 5]),
                "cdf": np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6]),
                "T": np.array([10, 5, 3.3, 2.5, 2, 1.7]),
                "IC_low": np.array([0.5, 1.5, 2.5, 3.5, 4.5, 5.5]),
                "IC_high": np.array([1.5, 2.5, 3.5, 4.5, 5.5, 6.5])
            }
        }
        
        # Should not raise an exception
        plot_grandeur.print_results(res)
        
        # Check that something was printed
        captured = capsys.readouterr()
        assert len(captured.out) > 0
    
    def test_plot_results(self, temp_dir):
        """Test plot_results function."""
        res = {
            "y": np.array([1, 2, 3, 4, 5]),
            "z": np.array([1, 2, 3, 4, 5]),
            "p0": 0.1,
            "mu": 1.0,
            "sigma": 0.5,
            "params": (0.5, 0.0, 1.0),
            "empirical": {
                "y_sorted": np.array([1, 2, 3, 4, 5]),
                "freq": np.array([0.1, 0.3, 0.5, 0.7, 0.9]),
                "T": np.array([10, 3.3, 2, 1.4, 1.1])
            },
            "quantiles": {
                "T": np.array([2, 5, 10]),
                "p": np.array([0.5, 0.2, 0.1]),
                "q": np.array([1.5, 2.5, 3.5]),
                "IC_low": np.array([1.0, 2.0, 3.0]),
                "IC_high": np.array([2.0, 3.0, 4.0])
            },
            "pcdf": {
                "x": np.array([0, 1, 2, 3, 4, 5]),
                "cdf": np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6]),
                "T": np.array([10, 5, 3.3, 2.5, 2, 1.7]),
                "IC_low": np.array([0.5, 1.5, 2.5, 3.5, 4.5, 5.5]),
                "IC_high": np.array([1.5, 2.5, 3.5, 4.5, 5.5, 6.5])
            }
        }
        
        output_path = temp_dir / "test_plot.png"
        
        # Should not raise an exception
        plot_grandeur.plot_results(res, output_path, title="Test Plot")
        
        # Check that file was created
        assert output_path.exists()
    
    def test_plot_period_from_flow(self, temp_dir):
        """Test plot_period_from_flow function."""
        res_station = {
            "debit_obs": 2.5,
            "frequence_non_depassement": 0.5,
            "Periode_de_retour": 2.0,
            "Periode_de_retour_interval_confiance_bas": 1.5,
            "Periode_de_retour_interval_confiance_haut": 2.5
        }
        
        res_estimation = {
            "y": np.array([1, 2, 3, 4, 5]),
            "z": np.array([1, 2, 3, 4, 5]),
            "p0": 0.1,
            "mu": 1.0,
            "sigma": 0.5,
            "params": (0.5, 0.0, 1.0),
            "empirical": {
                "y_sorted": np.array([1, 2, 3, 4, 5]),
                "freq": np.array([0.1, 0.3, 0.5, 0.7, 0.9]),
                "T": np.array([10, 3.3, 2, 1.4, 1.1])
            },
            "quantiles": {
                "T": np.array([2, 5, 10]),
                "p": np.array([0.5, 0.2, 0.1]),
                "q": np.array([1.5, 2.5, 3.5]),
                "IC_low": np.array([1.0, 2.0, 3.0]),
                "IC_high": np.array([2.0, 3.0, 4.0])
            },
            "pcdf": {
                "x": np.array([0, 1, 2, 3, 4, 5]),
                "cdf": np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6]),
                "T": np.array([10, 5, 3.3, 2.5, 2, 1.7]),
                "IC_low": np.array([0.5, 1.5, 2.5, 3.5, 4.5, 5.5]),
                "IC_high": np.array([1.5, 2.5, 3.5, 4.5, 5.5, 6.5])
            }
        }
        
        output_path = temp_dir / "test_period_plot.png"
        
        # Should not raise an exception
        plot_grandeur.plot_period_from_flow(
            q_obs=2.5,
            res_station=res_station,
            res_estimation=res_estimation,
            code_station="S001",
            output_path=output_path
        )
        
        # Check that file was created
        assert output_path.exists()


class TestPlotMeteoFrance:
    """Tests for plot_meteoFrance.py"""
    
    def test_to_lambert2_geodataframe_sim2(self):
        """Test to_lambert2_geodataframe with SIM2 data."""
        df = pd.DataFrame({
            "LAMBX": [1000, 2000],
            "LAMBY": [1000, 2000],
            "DATE": [20230601, 20230602],
            "PE": [1.0, 2.0]
        })
        
        result = plot_meteoFrance.to_lambert2_geodataframe(
            MeteoFranceDataType.SIM2_QUOT,
            df
        )
        
        assert result is not None
        assert hasattr(result, 'geometry')
    
    def test_plot_bar_dataframe(self, temp_dir):
        """Test plot_bar_dataframe function."""
        series = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0], name="Test Values")
        date_series = pd.Series(pd.date_range("2023-06-01", periods=5))
        
        output_path = temp_dir / "test_bar_plot.png"
        
        # Should not raise an exception
        plot_meteoFrance.plot_bar_dataframe(
            series_to_plot=series,
            series_date=date_series,
            normale_value=3.0,
            plot_title="Test Bar Plot",
            output_path=output_path
        )
        
        # Check that file was created
        assert output_path.exists()
    
    def test_get_chemin_sauvegarde_sim2_quot_range(self):
        """Test get_chemin_sauvegarde with SIM2_QUOT range."""
        start_date = datetime(2023, 6, 1)
        end_date = datetime(2023, 6, 10)
        
        result = plot_meteoFrance.get_chemin_sauvegarde(
            MeteoFranceDataType.SIM2_QUOT,
            start_date,
            end_date,
            is_data_aggregated=False
        )
        
        assert isinstance(result, Path)
        assert "QUOT-SIM2" in str(result)
    
    def test_get_chemin_sauvegarde_sim2_mens_single(self):
        """Test get_chemin_sauvegarde with SIM2_MENS single month."""
        start_date = datetime(2023, 6, 1)
        end_date = datetime(2023, 6, 1)
        
        result = plot_meteoFrance.get_chemin_sauvegarde(
            MeteoFranceDataType.SIM2_MENS,
            start_date,
            end_date,
            is_data_aggregated=False
        )
        
        assert isinstance(result, Path)
        assert "MENS-SIM2-202306" in str(result)


class TestPlotOnde:
    """Tests for plot_onde.py"""
    
    def test_get_titre_from_campagne_type(self):
        """Test get_titre_from_campagne_type function."""
        assert plot_onde.get_titre_from_campagne_type(OndeCampagneType.USUELLE) == "Usuelle"
        assert plot_onde.get_titre_from_campagne_type(OndeCampagneType.COMPLEMENTAIRE) == "Complémentaire"
        assert plot_onde.get_titre_from_campagne_type(OndeCampagneType.ALL_CAMPAGNE) == "Usuelle et Complémentaire"
    
    def test_configure_matplotlib(self):
        """Test configure_matplotlib function."""
        import matplotlib.pyplot as plt
        
        # Should not raise an exception
        plot_onde.configure_matplotlib()
        
        # Check that matplotlib settings were changed
        assert plt.rcParams["font.size"] == 11
    
    def test_save_and_close_plot(self, temp_dir, capsys):
        """Test save_and_close_plot function."""
        import matplotlib.pyplot as plt
        
        output_path = temp_dir / "test_save_close.png"
        
        # Create a simple plot
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])
        
        # Should not raise an exception
        plot_onde.save_and_close_plot(output_path)
        
        # Check that file was created
        assert output_path.exists()
        
        # Check that plot was closed
        assert plt.get_fignums() == []
    
    def test_plot_evolution_assecs(self, temp_dir):
        """Test plot_evolution_assecs function."""
        df = pd.DataFrame({
            "annee": [2020, 2020, 2021, 2021, 2022, 2022],
            "mois": [5, 6, 5, 6, 5, 6],
            "date_observation": pd.to_datetime(["2020-05-01", "2020-06-01", "2021-05-01", "2021-06-01", "2022-05-01", "2022-06-01"]),
            "libelle_ecoulement": ["Assec", "Assec", "Assec", "Ecoulement visible acceptable", "Assec", "Assec"],
            "code_type_campagne": [1, 1, 1, 1, 1, 1]
        })
        
        output_path = temp_dir / "test_evolution_assecs.png"
        
        # Should not raise an exception
        plot_onde.plot_evolution_assecs(
            df,
            datetime(2020, 5, 1),
            datetime(2022, 6, 30),
            2022,
            OndeCampagneType.USUELLE,
            output_path
        )
        
        # Check that file was created
        assert output_path.exists()
    
    def test_plot_evolution_ecoulements(self, temp_dir):
        """Test plot_evolution_ecoulements function."""
        df = pd.DataFrame({
            "annee": [2020, 2020, 2020, 2021, 2021, 2021],
            "mois": [6, 6, 6, 6, 6, 6],
            "code_ecoulement": ["1", "1f", "2", "1", "1f", "3"]
        })
        
        output_path = temp_dir / "test_evolution_ecoulements.png"
        
        # Should not raise an exception
        plot_onde.plot_evolution_ecoulements(
            df,
            OndeCampagneType.USUELLE,
            6,
            nb_mesures=10,
            output_path=output_path
        )
        
        # Check that file was created
        assert output_path.exists()


class TestRasterize:
    """Tests for rasterize.py"""
    
    def test_get_graphic_parameter_sswi(self):
        """Test get_graphic_parameter with SSWI."""
        result = plot_onde.get_graphic_parameter("SSWI1")
        
        assert result is not None
        palette, is_invert, labels, ticks = result
        
        assert isinstance(palette, str)
        assert isinstance(is_invert, bool)
        assert isinstance(labels, list)
        assert isinstance(ticks, list)
        assert len(labels) > 0
        assert len(ticks) > 0
    
    def test_get_graphic_parameter_unknown(self):
        """Test get_graphic_parameter with unknown unit."""
        result = plot_onde.get_graphic_parameter("UNKNOWN")
        assert result is None
