import sys
import sqlite3
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path to import scraper and utils
sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper import scrape_businesses
from utils.database import init_database

@patch("utils.search.requests.post")
@patch("utils.email_finder.requests.get")
def test_full_scraping_pipeline_integration(mock_get, mock_post):
    # Setup mock for Overpass API
    mock_post_response = MagicMock()
    mock_post_response.status_code = 200
    mock_post_response.json.return_value = {
        "elements": [
            {
                "type": "node",
                "id": 999111,
                "lat": 26.9124,
                "lon": 75.7873,
                "tags": {
                    "name": "Mocked Palace",
                    "website": "http://mockedpalace.com",
                    "cuisine": "Indian"
                }
            },
            {
                "type": "node",
                "id": 999222,
                "lat": 26.9150,
                "lon": 75.7890,
                "tags": {
                    "name": "Mocked Trattoria",
                    "website": "http://mockedtrattoria.com",
                    "cuisine": "Italian"
                }
            }
        ]
    }
    mock_post.return_value = mock_post_response

    # Setup mock for website crawling (extracting email)
    mock_get_response = MagicMock()
    mock_get_response.status_code = 200
    mock_get_response.text = "Hello! Reach us at contact@mockedpalace.com or office@mockedtrattoria.com"
    mock_get_response.json.return_value = {}
    mock_get.return_value = mock_get_response

    # Re-initialize test database
    init_database()
    
    # Run the scraper in test_mode=True so it doesn't fail on Overpass issues
    total, found, ready_list = scrape_businesses(
        business_type="restaurant",
        verbose=False,
        test_mode=True
    )
    
    
    # Assertions
    assert total >= 2
    assert found > 0
    assert len(ready_list) > 0
    
    # Verify that the contacts are actually in SQLite database
    conn = sqlite3.connect("data/agent.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, email FROM contacts WHERE osm_id IN ('999111', '999222')")
    contacts = cursor.fetchall()
    conn.close()
    
    assert len(contacts) > 0
