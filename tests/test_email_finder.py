import sys
from pathlib import Path

# Add project root to path to import utils
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.email_finder import (
    is_valid_business_email,
    generate_business_email,
    extract_emails_from_text
)

def test_is_valid_business_email():
    # Valid business emails
    assert is_valid_business_email("info@pizzaplace.com") is True
    assert is_valid_business_email("hello@softwarecorp.net") is True
    assert is_valid_business_email("sales@shop.org") is True
    
    # Invalid personal emails
    assert is_valid_business_email("john.doe@gmail.com") is False
    assert is_valid_business_email("marketing@yahoo.com") is False
    assert is_valid_business_email("support@hotmail.com") is False
    assert is_valid_business_email("admin@outlook.com") is False


def test_generate_business_email():
    # Generate business email for restaurant
    res = generate_business_email("pizzaplace.com", "Pizza Palace", "restaurant")
    assert res is not None
    email, confidence = res
    assert email == "info@pizzaplace.com"
    assert confidence == 0.5
    
    # Generate business email with subdomain cleanup
    res = generate_business_email("www.softwarecorp.com", "Software Corp", "solution_company")
    assert res is not None
    email, confidence = res
    assert email == "sales@softwarecorp.com"
    
    # Handle None/empty input
    assert generate_business_email("") is None
    assert generate_business_email(None) is None


def test_extract_emails_from_text():
    text = "Contact us at info@pizzaplace.com or personal@gmail.com. Admin email is admin@pizzaplace.com"
    emails = extract_emails_from_text(text)
    
    # Should only extract business emails
    assert "info@pizzaplace.com" in emails
    assert "admin@pizzaplace.com" in emails
    assert "personal@gmail.com" not in emails
    assert len(emails) == 2
