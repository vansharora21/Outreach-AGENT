import requests
from typing import List, Dict
import time

# Multiple Overpass API endpoints (for redundancy)
OVERPASS_ENDPOINTS = [
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://overpass.osm.ch/api/interpreter",
    "https://z.overpass-api.de/api/interpreter"
]

# Mock data for testing when APIs are down
MOCK_RESTAURANTS = [
    {
        "name": "Pizza Palace",
        "lat": 26.9124,
        "lon": 75.7873,
        "place_id": "osm_mock_1",
        "osm_id": "mock_1",
        "osm_type": "node",
        "website": None,
        "phone": "+91-9876543210",
        "email": "info@pizzapalace.com",
        "opening_hours": "10:00-23:00",
        "cuisine": "Italian"
    },
    {
        "name": "Royal Biryani House",
        "lat": 26.9140,
        "lon": 75.7885,
        "place_id": "osm_mock_2",
        "osm_id": "mock_2",
        "osm_type": "node",
        "website": None,
        "phone": "+91-9876543211",
        "email": "contact@royalbiryani.com",
        "opening_hours": "11:00-22:30",
        "cuisine": "Indian"
    },
    {
        "name": "The Spice Garden",
        "lat": 26.9150,
        "lon": 75.7865,
        "place_id": "osm_mock_3",
        "osm_id": "mock_3",
        "osm_type": "node",
        "website": None,
        "phone": "+91-9876543212",
        "email": "hello@spicegarden.com",
        "opening_hours": "12:00-23:00",
        "cuisine": "Indian"
    },
    {
        "name": "Cafe Aurora",
        "lat": 26.9110,
        "lon": 75.7890,
        "place_id": "osm_mock_4",
        "osm_id": "mock_4",
        "osm_type": "node",
        "website": None,
        "phone": "+91-9876543213",
        "email": "info@cafeaurora.com",
        "opening_hours": "08:00-21:00",
        "cuisine": "Cafe"
    },
    {
        "name": "Tandoori Express",
        "lat": 26.9130,
        "lon": 75.7875,
        "place_id": "osm_mock_5",
        "osm_id": "mock_5",
        "osm_type": "node",
        "website": None,
        "phone": "+91-9876543214",
        "email": "order@tandooriexpress.com",
        "opening_hours": "11:30-23:00",
        "cuisine": "Indian"
    }
]

def get_restaurants(location: tuple, radius: int = 3000) -> List[Dict]:
    """
    Search for nearby restaurants using Overpass API (OpenStreetMap).
    Includes retry logic with exponential backoff and fallback to mock data.
    
    Args:
        location: Tuple of (latitude, longitude)
        radius: Search radius in meters (default: 3000m = 3km)
    
    Returns:
        List of restaurant dictionaries with name, lat, lon, and place_id
    """
    
    lat, lon = location
    
    # Overpass API query for restaurants
    overpass_query = f"""
    [out:json][timeout:30];
    (
      node["amenity"="restaurant"](around:{radius},{lat},{lon});
      way["amenity"="restaurant"](around:{radius},{lat},{lon});
      relation["amenity"="restaurant"](around:{radius},{lat},{lon});
    );
    out center;
    """
    
    restaurants = []
    retry_count = 0
    max_retries = 2
    
    # Try each endpoint with retry logic
    for endpoint in OVERPASS_ENDPOINTS:
        for attempt in range(max_retries):
            try:
                if attempt == 0:
                    print(f"🔄 Trying Overpass endpoint: {endpoint}")
                else:
                    print(f"🔄 Retry {attempt}/{max_retries-1} on {endpoint}...")
                
                headers = {
                    "User-Agent": "MultiBusinessOutreachAgent/1.0 (contact@webuildsolutions21.gmail.com)",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
                response = requests.post(
                    endpoint, 
                    data=overpass_query,
                    headers=headers,
                    timeout=60  # Increased timeout
                )
                response.raise_for_status()
                data = response.json()
                
                print(f"✅ Successfully queried Overpass API")
                
                for element in data.get("elements", []):
                    name = element.get("tags", {}).get("name", "Unknown Restaurant")
                    
                    # Get coordinates
                    if "lat" in element and "lon" in element:
                        lat_val = element["lat"]
                        lon_val = element["lon"]
                    elif "center" in element:
                        lat_val = element["center"]["lat"]
                        lon_val = element["center"]["lon"]
                    else:
                        continue
                    
                    # Create a unique place_id based on OSM id
                    place_id = f"osm_{element.get('id', 'unknown')}"
                    
                    restaurant = {
                        "name": name,
                        "lat": lat_val,
                        "lon": lon_val,
                        "place_id": place_id,
                        "osm_id": element.get("id"),
                        "osm_type": element.get("type"),
                        "website": element.get("tags", {}).get("website"),
                        "phone": element.get("tags", {}).get("phone"),
                        "email": element.get("tags", {}).get("email"),
                        "opening_hours": element.get("tags", {}).get("opening_hours"),
                        "cuisine": element.get("tags", {}).get("cuisine")
                    }
                    
                    restaurants.append(restaurant)
                
                if restaurants:
                    print(f"✅ Found {len(restaurants)} restaurants from OpenStreetMap")
                    return restaurants
                else:
                    print(f"⚠️ No restaurants found on this endpoint, trying next...")
                    break
                
            except requests.exceptions.Timeout:
                print(f"⏱️ Timeout on {endpoint} (attempt {attempt+1}/{max_retries})...")
                if attempt < max_retries - 1:
                    wait_time = 5 * (attempt + 1)
                    print(f"⏳ Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                continue
                
            except requests.exceptions.ConnectionError:
                print(f"🔌 Connection error on {endpoint} (attempt {attempt+1}/{max_retries})...")
                if attempt < max_retries - 1:
                    wait_time = 5 * (attempt + 1)
                    print(f"⏳ Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                continue
                
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:
                    print(f"⛔ Rate limited on {endpoint}, waiting 60s...")
                    time.sleep(60)
                elif response.status_code in [500, 502, 503, 504]:
                    print(f"🚫 Server error ({response.status_code}) on {endpoint} (attempt {attempt+1}/{max_retries})...")
                    if attempt < max_retries - 1:
                        wait_time = 10 * (attempt + 1)
                        print(f"⏳ Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                else:
                    print(f"❌ HTTP Error {response.status_code} on {endpoint}, trying next...")
                    break
                continue
                
            except Exception as e:
                print(f"❌ Error on {endpoint}: {e}")
                break
    
    # If all APIs failed, use mock data for testing
    print("\n⚠️ All Overpass endpoints failed. Using mock data for testing...")
    print("💡 Tips to fix:")
    print("   - Check your internet connection")
    print("   - Try again in 30 minutes (Overpass API may be overloaded)")
    print("   - Verify coordinates are correct: " + str(location))
    print("   - Visit https://overpass-api.de/status to check server status")
    print("\n🧪 Testing with mock restaurant data...\n")
    
    return MOCK_RESTAURANTS
