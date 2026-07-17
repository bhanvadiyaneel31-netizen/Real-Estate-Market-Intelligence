"""
Unit tests for the Click CLI commands.
"""

from unittest import mock
from click.testing import CliRunner
from app.cli.commands import cli

def test_predict_command_success() -> None:
    """
    Verify cli predict command runs and prints formatted output when Predictor returns values.
    """
    runner = CliRunner()
    with mock.patch("app.ml.predictor.Predictor") as mock_predictor:
        mock_instance = mock_predictor.return_value
        mock_instance.run_all_predictions.return_value = (
            {
                "estimated_price": 203366.68,
                "confidence": 0.7982,
                "is_below_market_value": False,
                "price_tier": "High",
                "proxy_explainability_factors": [
                    {"feature": "area", "impact": 38635.63},
                    {"feature": "fireplace_count", "impact": 17788.44},
                ]
            },
            {
                "price_estimator": "xgboost_regression",
                "factor_explainer": "decision_tree_regression",
            }
        )

        result = runner.invoke(cli, [
            "predict",
            "--bedrooms", "3",
            "--area", "1800",
            "--neighborhood", "Somerset",
            "--central-air",
            "--garage",
            "--no-pool",
            "--fireplaces", "1",
            "--desc", "Spacious renovated premium property in desirable Somerset."
        ])

        assert result.exit_code == 0
        assert "Platform Inference Report" in result.output
        assert "Estimated Property Value   : $203,366.68" in result.output
        assert "Model Prediction Confidence: 79.82%" in result.output
        assert "Priced Below Neighborhood? : No" in result.output
        assert "Calculated Price Tier      : High" in result.output
        assert "area" in result.output
        assert "+38,635.63" in result.output
        assert "xgboost_regression" in result.output

        # Verify arguments passed to run_all_predictions
        mock_instance.run_all_predictions.assert_called_once_with({
            "bedrooms": 3,
            "area": 1800.0,
            "neighborhood": "Somerset",
            "has_central_air": 1,
            "has_garage": 1,
            "has_pool": 0,
            "fireplace_count": 1,
            "description_text": "Spacious renovated premium property in desirable Somerset.",
        })


def test_predict_command_model_files_missing() -> None:
    """
    Verify cli predict command handles FileNotFoundError gracefully.
    """
    runner = CliRunner()
    with mock.patch("app.ml.predictor.Predictor", side_effect=FileNotFoundError("Mocked missing file")):
        result = runner.invoke(cli, ["predict"])
        assert result.exit_code == 0
        assert "Error: Model files not found." in result.output


def test_serve_command_success() -> None:
    """
    Verify cli serve command launches uvicorn with correct options.
    """
    runner = CliRunner()
    with mock.patch("app.cli.commands.uvicorn.run") as mock_run:
        result = runner.invoke(cli, ["serve", "--host", "0.0.0.0", "--port", "9001", "--reload"])
        assert result.exit_code == 0
        assert "Launching FastAPI Server on http://0.0.0.0:9001..." in result.output
        mock_run.assert_called_once_with("app.main:app", host="0.0.0.0", port=9001, reload=True)
