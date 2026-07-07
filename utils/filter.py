from typing import List, Dict
import re
from datetime import datetime

# Cuisines to prioritize (fine dining, higher value targets)
PRIORITY_CUISINES = [
    "italian", "french", "japanese", "thai", "indian",
    "spanish", "mexican", "fusion", "mediterranean", "seafood"
]

# Cuisines to exclude (low priority)
EXCLUDE_CUISINES = [
    "fast_food", "pizza", "sandwich", "burger", "wings",
    "taco", "shawarma", "kebab"
]


def filter_no_website(restaurants: List[Dict]) -> List[Dict]:
    """
    Flag restaurants on whether they have a website rather than dropping them.
    Adds a 'has_website' key (bool) to each restaurant dictionary.
    """
    processed = []

    for restaurant in restaurants:
        restaurant["has_website"] = bool(restaurant.get("website"))
        processed.append(restaurant)

    return processed


def calculate_contact_quality_score(restaurant: Dict) -> float:
    """
    Calculate a quality score (0-1) for how good a contact this is.
    Higher score = better outreach target.
    """
    score = 0.5  # Base score
    
    # +0.1 if has phone
    if restaurant.get("phone"):
        score += 0.1
    
    # +0.1 if has email
    if restaurant.get("email"):
        score += 0.1
    
    # +0.1 if has opening hours (well-established)
    if restaurant.get("opening_hours"):
        score += 0.1
    
    # +0.2 if has cuisine info
    if restaurant.get("cuisine"):
        score += 0.2
    
    # Bonus for priority cuisines
    cuisine = (restaurant.get("cuisine") or "").lower()
    if any(pc in cuisine for pc in PRIORITY_CUISINES):
        score += 0.1
    
    # Penalty for excluded cuisines
    if any(ec in cuisine for ec in EXCLUDE_CUISINES):
        score -= 0.2
        
    # +0.1 if does NOT have website (target businesses without website)
    has_web = restaurant.get("has_website") if "has_website" in restaurant else bool(restaurant.get("website"))
    if not has_web:
        score += 0.1
    
    return min(score, 1.0)  # Cap at 1.0


def is_open_now(opening_hours: str) -> bool:
    """
    Check if restaurant is currently open based on opening_hours string.
    Format example: "Mo-Su 10:00-22:00" or "Mo-Fr 11:00-23:00; Sa,Su 12:00-23:00"
    """
    if not opening_hours:
        return None  # Unknown
    
    try:
        now = datetime.now()
        current_day = now.strftime("%a")[:2]  # Mon, Tue, etc.
        current_time = now.strftime("%H:%M")
        
        # Very basic parsing - full implementation would be more complex
        # This is a simplified version
        if "-" in opening_hours:
            parts = opening_hours.split(";")[0]  # Get first part
            times = parts.split("-")[-1].strip()  # Get time range
            
            if "-" in times:
                open_time, close_time = times.split("-")
                if open_time.strip() <= current_time <= close_time.strip():
                    return True
        
        return None  # Couldn't determine
    
    except:
        return None  # Parse error


def filter_by_criteria(restaurants: List[Dict], **filters) -> List[Dict]:
    """
    Advanced filtering with multiple criteria.
    
    Args:
        restaurants: List of restaurants
        filters: Dict of filters like:
            - has_website: bool (default False - we want NO website)
            - min_quality_score: float (0-1)
            - cuisines: List of cuisines to include
            - exclude_cuisines: List of cuisines to exclude
            - has_email: bool
            - has_phone: bool
            - has_opening_hours: bool
    
    Returns:
        Filtered list
    """
    filtered = []
    
    for restaurant in restaurants:
        # Skip if has website (unless we want websites)
        if not filters.get("has_website", False) and restaurant.get("website"):
            continue
        
        # Quality score filter
        quality_score = calculate_contact_quality_score(restaurant)
        if quality_score < filters.get("min_quality_score", 0.3):
            continue
        
        # Email filter
        if filters.get("has_email", False) and not restaurant.get("email"):
            continue
        
        # Phone filter
        if filters.get("has_phone", False) and not restaurant.get("phone"):
            continue
        
        # Opening hours filter
        if filters.get("has_opening_hours", False) and not restaurant.get("opening_hours"):
            continue
        
        # Cuisine filter
        cuisine = (restaurant.get("cuisine") or "").lower()
        
        if "cuisines" in filters:
            cuisines_list = filters["cuisines"]
            if not any(c.lower() in cuisine for c in cuisines_list):
                continue
        
        if "exclude_cuisines" in filters:
            exclude_list = filters["exclude_cuisines"]
            if any(c.lower() in cuisine for c in exclude_list):
                continue
        
        # Passed all filters
        filtered.append(restaurant)
    
    return filtered


def rank_restaurants(restaurants: List[Dict]) -> List[Dict]:
    """
    Rank restaurants by quality score (highest first).
    Returns sorted list.
    """
    restaurants_with_scores = [
        (restaurant, calculate_contact_quality_score(restaurant))
        for restaurant in restaurants
    ]
    
    # Sort by score descending
    sorted_restaurants = sorted(
        restaurants_with_scores,
        key=lambda x: x[1],
        reverse=True
    )
    
    # Add score to restaurant dict and return
    result = []
    for restaurant, score in sorted_restaurants:
        restaurant["quality_score"] = score
        result.append(restaurant)
    
    return result
