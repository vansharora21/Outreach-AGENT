import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.search import build_overpass_query


def test_business_type_changes_osm_selector():
    restaurant_query = build_overpass_query((26.9, 75.8), 5000, "restaurant")
    ecommerce_query = build_overpass_query((26.9, 75.8), 5000, "ecommerce")

    assert '"amenity"~"^(restaurant|cafe|bar)$"' in restaurant_query
    assert 'nwr["shop"]' in ecommerce_query
    assert "around:5000,26.9,75.8" in ecommerce_query
