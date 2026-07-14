"""
CLI commands module containing click commands for scraping and serving the sandbox.
"""

import click
import uvicorn
from app.db.session import SessionLocal, init_db
from app.scraper.scraper import AmesSandboxScraper


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
