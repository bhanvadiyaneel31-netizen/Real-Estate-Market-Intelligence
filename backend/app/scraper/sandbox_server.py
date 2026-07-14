"""
Local sandbox server serving Ames Housing data as static HTML pages.
"""

import os
import pandas as pd
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI(title="Ames Housing Scraping Sandbox")

# Load Ames Housing dataset
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(CURRENT_DIR, "AmesHousing.txt")

if os.path.exists(DATA_PATH):
    # The official dataset is tab-separated
    df = pd.read_csv(DATA_PATH, sep="\t")
else:
    df = pd.DataFrame()


@app.get("/listings", response_class=HTMLResponse)
async def list_listings(page: int = Query(1, ge=1), limit: int = Query(20, ge=1)):
    """
    Renders a paginated list of properties.
    """
    if df.empty:
        return "<html><body><h1>No data loaded. Make sure AmesHousing.txt is in backend/app/scraper/</h1></body></html>"
    
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    sliced_df = df.iloc[start_idx:end_idx]
    
    html_lines = [
        "<html>",
        "<head><title>Ames Housing Listings</title></head>",
        "<body>",
        "<h1>Properties for Sale in Ames, IA</h1>",
        "<ul>"
    ]
    
    for _, row in sliced_df.iterrows():
        pid = row.get("PID", "")
        # Handle cases where PID is missing or NaN
        if pd.isna(pid):
            continue
        pid_str = str(int(pid))
        neighborhood = row.get("Neighborhood", "Unknown")
        price = row.get("SalePrice", "Unknown")
        
        # Format price cleanly if it's numeric
        try:
            price_formatted = f"${int(price):,}"
        except (ValueError, TypeError):
            price_formatted = f"${price}"
            
        title = f"Property in {neighborhood} - {price_formatted}"
        html_lines.append(f'  <li class="cl-static-search-result"><a href="/listings/{pid_str}">{title}</a></li>')
        
    html_lines.append("</ul>")
    
    # Add pagination links
    total_pages = (len(df) + limit - 1) // limit
    if page < total_pages:
        html_lines.append(f'<a href="/listings?page={page + 1}&limit={limit}" class="next-page">Next</a>')
    if page > 1:
        html_lines.append(f'<a href="/listings?page={page - 1}&limit={limit}" class="prev-page">Previous</a>')
        
    html_lines.append("</body></html>")
    return "\n".join(html_lines)


@app.get("/listings/{pid}", response_class=HTMLResponse)
async def get_listing(pid: int):
    """
    Renders detail page for a single property.
    """
    if df.empty:
        raise HTTPException(status_code=500, detail="No data loaded.")
        
    # Search by PID
    match = df[df["PID"] == pid]
    if match.empty:
        raise HTTPException(status_code=404, detail="Listing not found.")
        
    row = match.iloc[0]
    
    neighborhood = row.get("Neighborhood", "Unknown")
    price = row.get("SalePrice", 0)
    area = row.get("Gr Liv Area", 0)
    beds = row.get("Bedroom AbvGr", 0)
    baths = row.get("Full Bath", 0)
    
    # Build list of amenities
    amenities = []
    if row.get("Central Air") == "Y":
        amenities.append("Central Air")
    garage_type = row.get("Garage Type")
    if pd.notna(garage_type) and garage_type != "NA":
        amenities.append(f"Garage ({garage_type})")
    pool_area = row.get("Pool Area", 0)
    if pool_area > 0:
        amenities.append("Pool")
    fireplace_count = row.get("Fireplaces", 0)
    if fireplace_count > 0:
        amenities.append(f"{fireplace_count} Fireplace(s)")
        
    amenities_str = ", ".join(amenities) if amenities else "None"
    
    description = (
        f"This beautiful {row.get('House Style', 'Residential')} style property is located in the desirable "
        f"{neighborhood} neighborhood of Ames, IA. Built in {int(row.get('Year Built', 1900))}, this home features "
        f"{int(beds)} bedrooms and {int(baths)} bathrooms, offering a comfortable living area of {int(area)} sqft. "
        f"The property includes {amenities_str.lower()} and is sold under {row.get('Sale Condition', 'Normal')} conditions."
    )
    
    # Render detail structure mapping exactly to required parsing elements
    html = f"""<html>
<head><title>Property {pid}</title></head>
<body>
    <h1 class="title">Residential Property in {neighborhood}</h1>
    <div class="details">
        <span class="price">${price:,}</span>
        <span class="location">{neighborhood}, Ames, IA</span>
        <span class="bedrooms">{int(beds)} BR</span>
        <span class="area">{int(area)} sqft</span>
        <div class="amenities">{amenities_str}</div>
        <div id="postingbody">{description}</div>
    </div>
</body>
</html>"""
    return html
