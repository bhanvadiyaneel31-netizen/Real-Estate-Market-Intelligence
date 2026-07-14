"""
Unit tests for the Ames Housing local sandbox scraper.
"""

from unittest import mock
from typing import Generator
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.db.models import Base, RawListing
from app.scraper.scraper import AmesSandboxScraper

# Mock HTML content for testing
MOCK_LISTINGS_HTML: str = """<html>
<body>
    <h1>Properties</h1>
    <ul>
        <li class="cl-static-search-result"><a href="/listings/1001">Property 1</a></li>
        <li class="cl-static-search-result"><a href="/listings/1002">Property 2</a></li>
    </ul>
    <a href="/listings?page=2&limit=2" class="next-page">Next</a>
</body>
</html>"""

MOCK_DETAIL_1001: str = """<html>
<body>
    <h1 class="title">Residential Property in CollegeCreek</h1>
    <div class="details">
        <span class="price">$150,000</span>
        <span class="location">CollegeCreek, Ames, IA</span>
        <span class="bedrooms">3 BR</span>
        <span class="area">1200 sqft</span>
        <div class="amenities">Central Air, Garage (Attchd)</div>
        <div id="postingbody">A beautiful 1Story house in CollegeCreek with 3 bedrooms.</div>
    </div>
</body>
</html>"""

MOCK_DETAIL_1002: str = """<html>
<body>
    <h1 class="title">Residential Property in Somerset</h1>
    <div class="details">
        <span class="price">$200,000</span>
        <span class="location">Somerset, Ames, IA</span>
        <span class="bedrooms">4 BR</span>
        <span class="area">1500 sqft</span>
        <div class="amenities">None</div>
        <div id="postingbody">A beautiful 2Story house in Somerset with 4 bedrooms.</div>
    </div>
</body>
</html>"""


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """
    Fixture providing an in-memory SQLite database session.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionClass = sessionmaker(bind=engine)
    session = SessionClass()
    try:
        yield session
    finally:
        session.close()


@mock.patch("requests.Session.get")
def test_scrape_listings_happy_path(mock_get: mock.MagicMock, db_session: Session) -> None:
    """
    Test successful scraping and saving to the database.
    """
    # Setup mock responses for list page and two detail pages
    mock_resp_list = mock.Mock()
    mock_resp_list.status_code = 200
    mock_resp_list.text = MOCK_LISTINGS_HTML

    mock_resp_1001 = mock.Mock()
    mock_resp_1001.status_code = 200
    mock_resp_1001.text = MOCK_DETAIL_1001

    mock_resp_1002 = mock.Mock()
    mock_resp_1002.status_code = 200
    mock_resp_1002.text = MOCK_DETAIL_1002

    # Return list page first, then detail 1001, then detail 1002
    mock_get.side_effect = [mock_resp_list, mock_resp_1001, mock_resp_1002]

    scraper = AmesSandboxScraper(base_url="http://localhost:8001", delay_seconds=0.0)
    listings = scraper.scrape_listings(limit=2)

    assert len(listings) == 2
    assert listings[0]["external_id"] == "1001"
    assert listings[0]["price"] == "$150,000"
    assert listings[0]["location"] == "CollegeCreek, Ames, IA"
    assert listings[0]["bedrooms"] == "3 BR"
    assert listings[0]["area"] == "1200 sqft"
    assert listings[0]["amenities"] == "Central Air, Garage (Attchd)"
    assert "beautiful 1Story house" in listings[0]["description_text"]

    assert listings[1]["external_id"] == "1002"
    assert listings[1]["price"] == "$200,000"

    # Save to mock DB
    saved_count = scraper.save_raw_listings(db_session, listings)
    assert saved_count == 2

    # Query DB to verify
    db_listings = db_session.query(RawListing).all()
    assert len(db_listings) == 2
    assert db_listings[0].external_id == "1001"
    assert db_listings[0].price == "$150,000"


@mock.patch("requests.Session.get")
def test_scrape_listings_resiliency(mock_get: mock.MagicMock, db_session: Session) -> None:
    """
    Test that scraper handles individual network or parsing errors and continues the batch.
    """
    mock_resp_list = mock.Mock()
    mock_resp_list.status_code = 200
    mock_resp_list.text = MOCK_LISTINGS_HTML

    # Detail 1001 fails (returns 404), detail 1002 succeeds
    mock_resp_1001_fail = mock.Mock()
    mock_resp_1001_fail.status_code = 404

    mock_resp_1002_success = mock.Mock()
    mock_resp_1002_success.status_code = 200
    mock_resp_1002_success.text = MOCK_DETAIL_1002

    # Next page returns 404 to end pagination loop
    mock_resp_next_fail = mock.Mock()
    mock_resp_next_fail.status_code = 404

    mock_get.side_effect = [
        mock_resp_list,
        mock_resp_1001_fail,
        mock_resp_1002_success,
        mock_resp_next_fail
    ]

    scraper = AmesSandboxScraper(base_url="http://localhost:8001", delay_seconds=0.0)
    listings = scraper.scrape_listings(limit=2)

    # 1001 should be skipped, but 1002 should succeed, returning 1 item total
    assert len(listings) == 1
    assert listings[0]["external_id"] == "1002"

    saved_count = scraper.save_raw_listings(db_session, listings)
    assert saved_count == 1


@mock.patch("requests.Session.get")
def test_scrape_listings_malformed_html(mock_get: mock.MagicMock, db_session: Session) -> None:
    """
    Test that a listing with missing required fields (e.g. price) is skipped
    and does not crash the scraper batch.
    """
    mock_resp_list = mock.Mock()
    mock_resp_list.status_code = 200
    mock_resp_list.text = MOCK_LISTINGS_HTML

    # Detail 1001 is missing the price tag completely
    mock_resp_1001_malformed = mock.Mock()
    mock_resp_1001_malformed.status_code = 200
    mock_resp_1001_malformed.text = """<html>
<body>
    <h1 class="title">Residential Property in CollegeCreek</h1>
    <div class="details">
        <span class="location">CollegeCreek, Ames, IA</span>
        <span class="bedrooms">3 BR</span>
    </div>
</body>
</html>"""

    mock_resp_1002_success = mock.Mock()
    mock_resp_1002_success.status_code = 200
    mock_resp_1002_success.text = MOCK_DETAIL_1002

    mock_resp_next_fail = mock.Mock()
    mock_resp_next_fail.status_code = 404

    mock_get.side_effect = [
        mock_resp_list,
        mock_resp_1001_malformed,
        mock_resp_1002_success,
        mock_resp_next_fail
    ]

    scraper = AmesSandboxScraper(base_url="http://localhost:8001", delay_seconds=0.0)
    listings = scraper.scrape_listings(limit=2)

    # 1001 is skipped due to missing price; 1002 succeeds
    assert len(listings) == 1
    assert listings[0]["external_id"] == "1002"

    saved_count = scraper.save_raw_listings(db_session, listings)
    assert saved_count == 1

