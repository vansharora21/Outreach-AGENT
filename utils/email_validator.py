import subprocess
import re
import smtplib
import socket
from typing import List

def get_mx_records(domain: str) -> List[str]:
    """Resolve MX records for a domain using nslookup on Windows."""
    try:
        output = subprocess.check_output(
            f"nslookup -type=mx {domain}", 
            shell=True, 
            stderr=subprocess.DEVNULL,
            timeout=5
        ).decode("utf-8", errors="ignore")
        
        # Match pattern: mail exchanger = mail.example.com
        matches = re.findall(r"mail exchanger\s*=\s*([a-zA-Z0-9.-]+)", output)
        if matches:
            return [m.strip().rstrip(".") for m in matches]
    except Exception:
        pass
    
    # Fallback to resolving the domain directly as an A record
    try:
        socket.gethostbyname(domain)
        return [domain]
    except Exception:
        return []


def verify_email_smtp(email: str, sender_email: str = "outreach@webuildsolutions21.com") -> bool:
    """
    Perform a live SMTP RCPT TO check on an email address without sending mail.
    Returns:
        bool: True if verified or if check is inconclusive, False if explicitly rejected.
    """
    if not email or "@" not in email:
        return False
        
    domain = email.split("@")[1].lower()
    mx_hosts = get_mx_records(domain)
    
    if not mx_hosts:
        # If no A or MX records resolve, the domain doesn't exist
        return False
        
    for host in mx_hosts:
        try:
            # Connect to SMTP server (standard port 25)
            smtp = smtplib.SMTP(host, port=25, timeout=7)
            
            # Identify ourselves
            smtp.helo(smtp.local_hostname)
            
            # Start the envelope sender
            smtp.mail(sender_email)
            
            # Ask the server if recipient is valid
            code, message = smtp.rcpt(email)
            smtp.quit()
            
            # 250 means recipient exists
            if code == 250:
                return True
            # 550, 551, 552, 553, 554 represent explicit permanent rejections
            elif 500 <= code < 600:
                print(f"❌ SMTP validation: {email} rejected by {host} with code {code} ({message.decode('utf-8', errors='ignore').strip()})")
                return False
            else:
                # Grey-listing or temporary server issues (4xx) - treat as valid
                return True
                
        except Exception as e:
            # Connection blocks (e.g., residential ISP port 25 blocking) or timeouts
            # are caught here. We treat them as valid (True) to prevent false exclusions.
            continue
            
    # If all MX connections failed or timed out, assume valid
    return True
