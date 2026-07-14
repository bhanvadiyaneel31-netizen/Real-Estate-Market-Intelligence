"""
Web scraper class for extracting listings from the Ames Housing sandbox server.
"""

import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from app.db.models import RawListing

logger = logging.getLogger("app.scraper")


class AmesSandboxScraper:
    """
    Scraper designed to crawl and extract property listing details from the local Ames sandbox.
    """

    def __init__(self, base_url: str, delay_seconds: float = 0.5, max_retries: int = 3) -> None:
        """
        Initialize the scraper.

        Args:
            base_url (str): The base URL of the sandbox server.
            delay_seconds (float): Delay in seconds between requests to avoid overloading.
            max_retries (int): Maximum number of retry attempts for failed requests.
        """
        self.base_url: str = base_url.rstrip("/")
        self.delay_seconds: float = delay_seconds
        self.max_retries: int = max_retries
        self.session: requests.Session = requests.Session()
        self.session.headers.update({
            "User-Agent": "AmesSandboxScraper/1.0 (Portfolio Project Crawler)"
        })

    def _fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch HTML content from a URL with retries and exponential backoff.
        """
        retries: int = 0
        backoff: float = self.delay_seconds

        while retries < self.max_retries:
            try:
                logger.debug(f"Fetching URL: {url}")
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 429:
                    logger.warning(f"Rate limited (429). Retrying in {backoff} seconds...")
                    time.sleep(backoff)
                    backoff *= 2
                    retries += 1
                else:
                    logger.error(f"Failed to fetch {url} (Status: {response.status_code})")
                    return None
            except requests.RequestException as e:
                logger.error(f"Network error fetching {url}: {e}. Retrying...")
                time.sleep(backoff)
                backoff *= 2
                retries += 1

        logger.error(f"Max retries reached for {url}")
        return None

    def scrape_listings(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Crawl the sandbox server, traverse pagination, and parse listings up to the limit.

        Args:
            limit (int): The maximum number of listings to scrape.

        Returns:
            List[Dict[str, Any]]: List of scraped listing objects.
        """
        listings: List[Dict[str, Any]] = []
        current_url: Optional[str] = f"{self.base_url}/listings?page=1"

        logger.info(f"Starting scrape from {current_url} (Limit: {limit})")

        while current_url and len(listings) < limit:
            time.sleep(self.delay_seconds)
            html = self._fetch_page(current_url)
            if not html:
                logger.error("Could not fetch page. Aborting list traversal.")
                break

            soup = BeautifulSoup(html, "html.parser")
            search_results = soup.find_all("li", class_="cl-static-search-result")

            if not search_results:
                logger.warning("No listings found on page.")
                break

            for li in search_results:
                if len(listings) >= limit:
                    break

                a_tag = li.find("a")
                if not a_tag or not a_tag.get("href"):
                    logger.warning("Skipping invalid search result listing link.")
                    continue

                href: str = a_tag["href"]
                detail_url = href if href.startswith("http") else f"{self.base_url}{href}"

                # Extract external ID from URL (e.g. /listings/12345 -> 12345)
                parts = href.rstrip("/").split("/")
                external_id = parts[-1] if parts else href

                # Scrape listing detail page
                time.sleep(self.delay_seconds)
                detail_listing = self._scrape_detail(detail_url, external_id)
                if detail_listing:
                    listings.append(detail_listing)
                else:
                    logger.warning(f"Skipping malformed or failed listing: {detail_url}")

            # Check for next page pagination link
            next_link = soup.find("a", class_="next-page")
            if next_link and next_link.get("href"):
                next_href: str = next_link["href"]
                current_url = next_href if next_href.startswith("http") else f"{self.base_url}{next_href}"
            else:
                current_url = None

        logger.info(f"Scrape session finished. Collected {len(listings)} listings.")
        return listings

    def _scrape_detail(self, url: str, external_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch and parse a single listing detail page.
        """
        html = self._fetch_page(url)
        if not html:
            return None

        try:
            soup = BeautifulSoup(html, "html.parser")
            
            # Find details elements
            title_tag = soup.find("h1", class_="title")
            title: str = title_tag.text.strip() if title_tag else f"Property {external_id}"

            price_tag = soup.find("span", class_="price")
            price: Optional[str] = price_tag.text.strip() if price_tag else None

            location_tag = soup.find("span", class_="location")
            location: Optional[str] = location_tag.text.strip() if location_tag else None

            bedrooms_tag = soup.find("span", class_="bedrooms")
            bedrooms: Optional[str] = bedrooms_tag.text.strip() if bedrooms_tag else None

            area_tag = soup.find("span", class_="area")
            area: Optional[str] = area_tag.text.strip() if area_tag else None

            amenities_tag = soup.find("div", class_="amenities")
            amenities: Optional[str] = amenities_tag.text.strip() if amenities_tag else None

            desc_tag = soup.find(id="postingbody")
            description: Optional[str] = desc_tag.text.strip() if desc_tag else None

            # Skip listing if crucial data points are missing (resiliency checklist)
            if not price or not location:
                logger.warning(f"Listing {external_id} is missing critical fields (price/location). Skipping.")
                return None

            return {
                "source": "ames_sandbox",
                "external_id": external_id,
                "url": url,
                "title": title,
                "price": price,
                "location": location,
                "bedrooms": bedrooms,
                "area": area,
                "amenities": amenities,
                "description_text": description,
                "scraped_at": datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error parsing listing detail page {url}: {e}", exc_info=True)
            return None

    def save_raw_listings(self, db: Session, listings: List[Dict[str, Any]]) -> int:
        """
        Save parsed listings into the raw_listings database table.

        Args:
            db (Session): SQLAlchemy session.
            listings (List[Dict[str, Any]]): List of parsed listing dictionaries.

        Returns:
            int: The number of saved records.
        """
        saved_count = 0
        for data in listings:
            try:
                db_listing = RawListing(
                    source=data["source"],
                    external_id=data["external_id"],
                    url=data["url"],
                    title=data["title"],
                    price=data["price"],
                    location=data["location"],
                    bedrooms=data["bedrooms"],
                    area=data["area"],
                    amenities=data["amenities"],
                    description_text=data["description_text"],
                    scraped_at=data["scraped_at"]
                )
                db.add(db_listing)
                saved_count += 1
            except Exception as e:
                logger.error(f"Failed to add listing {data.get('external_id')} to DB: {e}")
                db.rollback()

        if saved_count > 0:
            try:
                db.commit()
                logger.info(f"Committed {saved_count} raw listings to database.")
            except Exception as e:
                logger.error(f"Failed to commit transaction to DB: {e}")
                db.rollback()
                return 0

        return saved_count
