import re
import requests
from typing import Optional, List, Tuple
from bs4 import BeautifulSoup
import json

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

# Common email patterns for businesses
COMMON_BUSINESS_EMAILS = [
    "info@{domain}",
    "contact@{domain}",
    "hello@{domain}",
    "support@{domain}",
    "business@{domain}",
    "admin@{domain}",
    "sales@{domain}",
    "hello@{domain}",
    "mail@{domain}",
]

# Personal name patterns (for LinkedIn, etc)
FIRST_NAMES = ["info", "contact", "hello", "support", "admin", "sales", "mail", "team"]


def find_email(text: str) -> Optional[str]:
    """
    Extract business email from text (regex).
    Filters out personal emails (gmail, yahoo, etc).
    """
    matches = re.findall(EMAIL_REGEX, text)
    for email in matches:
        if is_valid_business_email(email):
            return email
    return None


def extract_emails_from_text(text: str) -> List[str]:
    """Extract all business emails from text."""
    matches = re.findall(EMAIL_REGEX, text)
    return [email for email in matches if is_valid_business_email(email)]


def is_valid_business_email(email: str) -> bool:
    """Check if email is a business email (not personal)."""
    personal_domains = {
        "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
        "aol.com", "mail.com", "yandex.com", "protonmail.com",
        "icloud.com", "me.com", "live.com", "msn.com"
    }
    
    domain = email.split("@")[1].lower()
    return domain not in personal_domains


def find_email_from_website(website_url: str, timeout: int = 5, depth: int = 3) -> Optional[Tuple[str, float]]:
    """
    Try to extract email from website with deep scraping.
    Returns (email, confidence_score)
    
    Strategies:
    1. Homepage
    2. /contact page
    3. /about page
    4. /contact-us page
    5. Deep crawl multiple pages
    """
    if not website_url:
        return None
    
    # Normalize URL
    if not website_url.startswith(("http://", "https://")):
        website_url = "https://" + website_url
    
    # Remove trailing slash for consistency
    base_url = website_url.rstrip("/")
    domain = base_url.replace("https://", "").replace("http://", "").split("/")[0]
    
    # Priority pages to check
    pages_to_check = [
        base_url,
        f"{base_url}/contact",
        f"{base_url}/about",
        f"{base_url}/contact-us",
        f"{base_url}/about-us",
        f"{base_url}/help",
        f"{base_url}/support",
        f"{base_url}/footer",
    ]
    
    visited_urls = set()
    
    for page_url in pages_to_check:
        if page_url in visited_urls or len(visited_urls) >= depth:
            continue
            
        try:
            response = requests.get(page_url, timeout=timeout)
            response.raise_for_status()
            visited_urls.add(page_url)
            
            # Extract emails from HTML
            emails = extract_emails_from_text(response.text)
            if emails:
                # Prioritize emails by relevance
                for email in emails:
                    if is_valid_business_email(email):
                        # Higher confidence for contact/about pages
                        confidence = 0.9 if "/contact" in page_url or "/about" in page_url else 0.7
                        return (email, confidence)
        
        except Exception as e:
            continue  # Try next page
    
    return None


def generate_business_email(domain: str, business_name: str = "", business_type: str = "generic") -> Optional[Tuple[str, float]]:
    """
    Generate probable business email for a business.
    Returns (email, confidence_score)
    
    E.g., info@pizzaplace.com
    """
    if not domain:
        return None
    
    # Extract domain without http/https
    domain = domain.replace("http://", "").replace("https://", "").rstrip("/")
    
    # Remove subdomains (www, blog, etc)
    parts = domain.split(".")
    if parts[0] in ["www", "blog", "mail", "shop"]:
        domain = ".".join(parts[1:])
    
    # Type-specific patterns
    type_patterns = {
        "restaurant": ["info", "reservations", "orders", "contact", "hello"],
        "solution_company": ["sales", "business", "info", "contact", "support"],
        "hr_company": ["hr", "recruitment", "hiring", "jobs", "careers"],
        "ecommerce": ["shop", "orders", "sales", "support", "info"],
        "service_business": ["info", "contact", "quote", "support", "hello"],
        "generic": FIRST_NAMES
    }
    
    patterns = type_patterns.get(business_type, FIRST_NAMES)
    
    # Try patterns
    for pattern in patterns:
        email = f"{pattern}@{domain}"
        if re.match(EMAIL_REGEX, email):
            confidence = 0.5 + (0.1 if pattern != "info" else 0)  # Slightly lower for generic
            return (email, confidence)
    
    return None


def find_email_via_clearbit(domain: str) -> Optional[Tuple[str, float]]:
    """
    Query Clearbit API (free tier available) for email.
    Returns (email, confidence_score)
    
    Free tier: 100 requests/month
    """
    try:
        # Clearbit Prospector API (free)
        url = f"https://prospector.clearbit.com/v1/people?domain={domain}&page_size=1"
        
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("results"):
                person = data["results"][0]
                email = person.get("email")
                if email and is_valid_business_email(email):
                    return (email, 0.95)  # High confidence from Clearbit
    
    except Exception as e:
        pass  # Free API may not be available
    
    return None


def find_email_via_hunter(domain: str) -> Optional[Tuple[str, float]]:
    """
    Query Hunter.io API (free tier: 50 requests/month).
    Returns (email, confidence_score)
    """
    try:
        # Hunter.io API
        url = f"https://api.hunter.io/v2/domain-search?domain={domain}&limit=1"
        # Note: Requires API key in production, but has free tier with limited requests
        
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("data", {}).get("emails"):
                email_info = data["data"]["emails"][0]
                email = email_info.get("value")
                confidence = email_info.get("confidence", 0.8) / 100  # Normalize to 0-1
                
                if email and is_valid_business_email(email):
                    return (email, min(confidence, 0.95))
    
    except Exception as e:
        pass
    
    return None


def find_email_via_linkedin(business_name: str, domain: str) -> Optional[Tuple[str, float]]:
    """
    Try to find email from LinkedIn company page.
    Returns (email, confidence_score)
    """
    try:
        # LinkedIn doesn't expose email via API, but we can try company page
        # This is a placeholder for LinkedIn scraping (requires careful implementation)
        pass
    
    except Exception as e:
        pass
    
    return None


def find_email_via_google_search(business_name: str, domain: str) -> Optional[Tuple[str, float]]:
    """
    Try to find email via Google Custom Search (requires API key).
    Returns (email, confidence_score)
    """
    try:
        # This would require Google Custom Search API key
        # Placeholder for future implementation
        pass
    
    except Exception as e:
        pass
    
    return None


def find_email_multi_strategy(business_name: str, website: str, domain: str = None,
                             business_type: str = "generic") -> Optional[Tuple[str, str, float]]:
    """
    Try multiple strategies to find email.
    Returns (email, source, confidence_score) with highest confidence.
    
    Strategies (in order):
    1. Website scraping (70-90% confidence)
    2. Clearbit API (95% confidence)
    3. Hunter.io API (80-95% confidence)
    4. Email generation from domain (50-60% confidence)
    5. LinkedIn/Google (variable)
    """
    results = []
    
    # Strategy 1: Website scraping (usually most reliable for businesses)
    if website:
        result = find_email_from_website(website)
        if result:
            results.append(("website", result[0], result[1]))
    
    # Extract domain if not provided
    if not domain and website:
        domain = website.replace("http://", "").replace("https://", "").split("/")[0]
    
    # Strategy 2: Clearbit API
    if domain:
        result = find_email_via_clearbit(domain)
        if result:
            results.append(("clearbit", result[0], result[1]))
    
    # Strategy 3: Hunter.io API
    if domain:
        result = find_email_via_hunter(domain)
        if result:
            results.append(("hunter", result[0], result[1]))
    
    # Strategy 4: Email generation
    if domain:
        result = generate_business_email(domain, business_name, business_type)
        if result:
            results.append(("generated", result[0], result[1]))
    
    # Return highest confidence result
    if results:
        results.sort(key=lambda x: x[2], reverse=True)  # Sort by confidence
        best = results[0]
        return (best[0], best[1], best[2])
    
    return None


def verify_email_format(email: str) -> bool:
    """Basic email format validation."""
    return bool(re.match(EMAIL_REGEX, email)) and is_valid_business_email(email)


def get_email_finding_score(results: List[Tuple[str, float]]) -> float:
    """
    Calculate overall email finding success rate.
    Input: List of (strategy, confidence) tuples
    Output: Average confidence score
    """
    if not results:
        return 0.0
    
    total_confidence = sum(score for _, score in results)
    return total_confidence / len(results)


