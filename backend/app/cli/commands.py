"""
CLI commands module containing click commands for scraping and serving the sandbox.
"""

import click
import uvicorn
from app.db.session import SessionLocal, init_db
from app.scraper.scraper import AmesSandboxScraper
from app.etl.pipeline import ETLPipeline


@click.group()
def cli() -> None:
    """
    Real Estate Market Intelligence Platform CLI tool.
    """
    pass


@cli.command("sandbox")
@click.option("--host", default="127.0.0.1", help="Bind host.")
@click.option("--port", default=8001, help="Bind port.")
def sandbox(host: str, port: int) -> None:
    """
    Start the local Ames Housing static HTML sandbox server.
    """
    click.echo(f"Starting Ames Housing Sandbox on http://{host}:{port}...")
    uvicorn.run("app.scraper.sandbox_server:app", host=host, port=port, log_level="info")


@cli.command("scrape")
@click.option("--limit", default=20, help="Max listings to scrape.")
@click.option("--url", default="http://127.0.0.1:8001", help="Base URL of the sandbox server.")
@click.option("--delay", default=0.1, help="Delay in seconds between requests.")
def scrape(limit: int, url: str, delay: float) -> None:
    """
    Scrape properties from the Ames sandbox server and store them in the DB.
    """
    click.echo("Initializing database tables if not exists...")
    init_db()

    click.echo(f"Starting crawler targeting {url} (limit={limit}, delay={delay}s)...")
    scraper = AmesSandboxScraper(base_url=url, delay_seconds=delay)

    db = SessionLocal()
    try:
        listings = scraper.scrape_listings(limit=limit)
        if not listings:
            click.echo("No listings gathered. Make sure the sandbox server is running!")
            return
            
        saved_count = scraper.save_raw_listings(db, listings)
        click.echo(f"Scrape completed successfully. Gathered: {len(listings)}, Saved to DB: {saved_count}")
    except Exception as e:
        click.echo(f"Error during scrape operation: {e}", err=True)
    finally:
        db.close()


@cli.command("clean")
@click.option("--version", default="1.0.0", help="Feature set version identifier.")
def clean(version: str) -> None:
    """
    Run the ETL pipeline: clean raw listings and build features.
    """
    click.echo("Initializing database tables if not exists...")
    init_db()

    click.echo(f"Starting ETL pipeline for version {version}...")
    db = SessionLocal()
    try:
        pipeline = ETLPipeline(db, feature_set_version=version)
        saved_count = pipeline.run()
        click.echo(f"ETL completed successfully. Cleaned & featured records saved to DB: {saved_count}")
    except Exception as e:
        click.echo(f"Error during clean operation: {e}", err=True)
    finally:
        db.close()


@cli.command("train")
@click.option("--version", default="1.0.0", help="Feature set version to use for training.")
def train(version: str) -> None:
    """
    Train and evaluate all 10 models using the specified feature set version.
    """
    click.echo("Initializing database tables if not exists...")
    init_db()

    click.echo(f"Starting model training pipeline for version {version}...")
    db = SessionLocal()
    try:
        from app.ml.trainer import ModelTrainer
        trainer = ModelTrainer(db)
        elapsed, metrics = trainer.train_all(feature_set_version=version)

        click.echo("\n" + "=" * 50)
        click.echo(f"Training Batch Completed Successfully in {elapsed:.2f} seconds!")
        click.echo("=" * 50)
        for model_name, eval_metrics in metrics.items():
            metrics_str = ", ".join(f"{k}: {v:.4f}" for k, v in eval_metrics.items())
            click.echo(f" - {model_name:28}: {metrics_str}")
        click.echo("=" * 50)
    except Exception as e:
        click.echo(f"Error during training operation: {e}", err=True)
    finally:
        db.close()


@cli.command("predict")
@click.option("--bedrooms", default=3, help="Number of bedrooms.")
@click.option("--area", default=1500.0, help="Living area in square feet.")
@click.option("--neighborhood", default="Somerset", help="Neighborhood name.")
@click.option("--central-air/--no-central-air", default=True, help="Central air conditioning presence.")
@click.option("--garage/--no-garage", default=True, help="Garage presence.")
@click.option("--pool/--no-pool", default=False, help="Pool presence.")
@click.option("--fireplaces", default=0, help="Number of fireplaces.")
@click.option("--desc", default="", help="Optional description text.")
def predict(
    bedrooms: int,
    area: float,
    neighborhood: str,
    central_air: bool,
    garage: bool,
    pool: bool,
    fireplaces: int,
    desc: str,
) -> None:
    """
    Query the prediction pipeline for a single property and print attributions.
    """
    click.echo("Running inference engine on input features...")
    try:
        from app.ml.predictor import Predictor
        predictor = Predictor()

        # Build raw features dict
        raw_features = {
            "bedrooms": bedrooms,
            "area": area,
            "neighborhood": neighborhood,
            "has_central_air": 1 if central_air else 0,
            "has_garage": 1 if garage else 0,
            "has_pool": 1 if pool else 0,
            "fireplace_count": fireplaces,
            "description_text": desc,
        }

        pred_res, models_used = predictor.run_all_predictions(raw_features)

        click.echo("\n" + "=" * 60)
        click.echo("Platform Inference Report")
        click.echo("=" * 60)
        click.echo(f"Estimated Property Value   : ${pred_res['estimated_price']:,.2f}")
        click.echo(f"Model Prediction Confidence: {pred_res['confidence'] * 100:.2f}%")
        click.echo(f"Priced Below Neighborhood? : {'Yes' if pred_res['is_below_market_value'] else 'No'}")
        click.echo(f"Calculated Price Tier      : {pred_res['price_tier']}")
        click.echo("-" * 60)
        click.echo("Proxy Feature Attributions (Decision Tree Surrogate):")
        for factor in pred_res["proxy_explainability_factors"]:
            click.echo(f" - {factor['feature']:24}: ${factor['impact']:+,.2f}")
        click.echo("-" * 60)
        click.echo("Models Employed:")
        for task, name in models_used.items():
            click.echo(f" - {task:25}: {name}")
        click.echo("=" * 60)

    except FileNotFoundError as fnf:
        click.echo(
            f"Error: Model files not found. Please run 'train' command first. Details: {fnf}",
            err=True,
        )
    except Exception as e:
        click.echo(f"Error executing prediction: {e}", err=True)


@cli.command("serve")
@click.option("--host", default="127.0.0.1", help="Bind host address.")
@click.option("--port", default=8000, help="Bind port number.")
@click.option("--reload/--no-reload", default=False, help="Enable auto-reload on code change.")
def serve(host: str, port: int, reload: bool) -> None:
    """
    Start the FastAPI production backend application server.
    """
    click.echo(f"Launching FastAPI Server on http://{host}:{port}...")
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    cli()




