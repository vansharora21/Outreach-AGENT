"""
Business search configuration.
Allows searching for different types of businesses (restaurants, solution companies, HR, etc)
"""

# Restaurant Configuration
RESTAURANT_CONFIG = {
    "name": "restaurant",
    "search_terms": ["restaurant", "cafe", "bar", "pizza", "diner"],
    "keywords": ["menu", "dining", "cuisine", "reservation", "delivery"],
    "email_patterns": [
        "info@{domain}",
        "contact@{domain}",
        "hello@{domain}",
        "support@{domain}",
        "reservations@{domain}",
        "orders@{domain}",
    ],
    "priority_cuisines": ["italian", "french", "japanese", "thai", "indian", "spanish", "mexican", "fusion"],
    "exclude_cuisines": ["fast_food", "pizza", "sandwich", "burger", "wings"]
}

# Software/IT Solution Company Configuration
SOLUTION_COMPANY_CONFIG = {
    "name": "solution_company",
    "search_terms": ["software", "tech", "IT solutions", "consulting", "development"],
    "keywords": ["services", "solutions", "technology", "enterprise", "development", "consulting"],
    "email_patterns": [
        "info@{domain}",
        "contact@{domain}",
        "sales@{domain}",
        "business@{domain}",
        "hello@{domain}",
        "support@{domain}",
    ],
    "priority_keywords": ["enterprise", "b2b", "services", "solutions", "consulting"],
}

# HR/Recruitment Company Configuration
HR_COMPANY_CONFIG = {
    "name": "hr_company",
    "search_terms": ["recruitment", "staffing", "HR", "human resources", "recruiting"],
    "keywords": ["recruitment", "careers", "hiring", "jobs", "talent"],
    "email_patterns": [
        "hr@{domain}",
        "recruitment@{domain}",
        "hiring@{domain}",
        "jobs@{domain}",
        "careers@{domain}",
        "info@{domain}",
        "contact@{domain}",
    ],
    "priority_keywords": ["recruitment", "staffing", "hiring", "talent"],
}

# E-commerce Business Configuration
ECOMMERCE_CONFIG = {
    "name": "ecommerce",
    "search_terms": ["shop", "store", "ecommerce", "retail", "online store"],
    "keywords": ["products", "shopping", "commerce", "store", "retail"],
    "email_patterns": [
        "shop@{domain}",
        "sales@{domain}",
        "info@{domain}",
        "contact@{domain}",
        "support@{domain}",
        "orders@{domain}",
    ],
    "priority_keywords": ["shop", "store", "online", "retail"],
}

# Service Business Configuration (Plumber, Electrician, etc)
SERVICE_BUSINESS_CONFIG = {
    "name": "service_business",
    "search_terms": ["services", "plumber", "electrician", "contractor", "repair"],
    "keywords": ["services", "professional", "contractor", "service", "repair"],
    "email_patterns": [
        "info@{domain}",
        "contact@{domain}",
        "hello@{domain}",
        "support@{domain}",
        "quote@{domain}",
    ],
    "priority_keywords": ["professional", "services", "local"],
}

# Default to restaurant
DEFAULT_CONFIG = RESTAURANT_CONFIG

# All available configs
ALL_CONFIGS = {
    "restaurant": RESTAURANT_CONFIG,
    "solution_company": SOLUTION_COMPANY_CONFIG,
    "hr_company": HR_COMPANY_CONFIG,
    "ecommerce": ECOMMERCE_CONFIG,
    "service_business": SERVICE_BUSINESS_CONFIG,
}


def get_config(business_type: str = "restaurant"):
    """Get configuration for a business type."""
    return ALL_CONFIGS.get(business_type.lower(), DEFAULT_CONFIG)


def list_available_configs():
    """List all available business types."""
    return list(ALL_CONFIGS.keys())
