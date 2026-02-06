import os
import re
import datetime
from urllib.parse import urlparse

import sys

def get_app_path():
    """Get the absolute path to the application directory."""
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def sanitize_filename(name):
    """Remove invalid characters from filename."""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def format_filename(url, page_title, page_date, original_filename, index, naming_pattern):
    """
    Format the filename based on the pattern.
    
    Args:
        url (str): The page URL.
        page_title (str): The title of the page.
        page_date (datetime.datetime): The publication date of the page.
        original_filename (str): The original filename of the image.
        index (int): The sequence number of the image in the page (0-based).
        naming_pattern (str): The pattern string.
        
    Returns:
        str: The formatted relative path.
    """
    
    # Basic components
    parsed_url = urlparse(url)
    host = parsed_url.netloc
    
    # Handle page date (default to now if None)
    if not page_date:
        page_date = datetime.datetime.now()
        
    # Sanitize components
    safe_title = sanitize_filename(page_title)
    safe_host = sanitize_filename(host)
    
    # 1. Handle time formats: {YYYY-MM-DD}, {HH-mm-ss}, etc.
    # We use strftime for standard codes, but user used specific placeholders.
    # Let's replace user specific placeholders with strftime values
    
    res = naming_pattern
    
    # Date placeholders
    res = res.replace("{YYYY-MM-DD}", page_date.strftime("%Y-%m-%d"))
    res = res.replace("{YYYY}", page_date.strftime("%Y"))
    res = res.replace("{MM}", page_date.strftime("%m"))
    res = res.replace("{DD}", page_date.strftime("%d"))
    
    res = res.replace("{HH-mm-ss}", page_date.strftime("%H-%M-%S"))
    res = res.replace("{HH}", page_date.strftime("%H"))
    res = res.replace("{mm}", page_date.strftime("%M"))
    res = res.replace("{ss}", page_date.strftime("%S"))
    
    # Page info placeholders
    res = res.replace("{page.title}", safe_title)
    res = res.replace("{page.host}", safe_host)
    
    # File info placeholders
    res = res.replace("{filename}", original_filename)
    
    # Sequence placeholders
    # {no.10001} -> implies starting at 1, padded? 
    # Or does it mean "index + 10001"? 
    # Usually it means a counter formatted. 
    # Let's support {no} (simple index+1), and {no.000} (padded).
    # Also user said {no.10001}, maybe they mean start at 10001? 
    # Let's assume {no.N} means format index+1 with zero padding to length of N?
    # Or just a fixed format. 
    # Let's implement {origin_serial} as index+1.
    
    res = res.replace("{origin_serial}", str(index + 1))
    
    # Handle {no.10001} style - complex regex
    # Matches {no.001} -> 001, 002...
    def replace_padding(match):
        pattern = match.group(1) # e.g. 0001 or 10001
        # If it's just zeros, pad to length.
        # If it's a number like 10001, maybe add index to it?
        # Let's assume it specifies the width and starting offset? 
        # Usually it just means "pad to this length".
        # But 10001 is 5 digits. 
        # Let's treat it as: width = len(pattern). value = index + 1.
        width = len(pattern)
        val = index + 1
        return f"{val:0{width}d}"

    res = re.sub(r'\{no\.(\d+)\}', replace_padding, res)
    
    # Fallback/Cleanup
    # Ensure no double slashes if not intended (though os.path.join handles some)
    # But user might put "/" in pattern to create folders.
    
    return res

if __name__ == "__main__":
    # Test
    d = datetime.datetime(2025, 7, 18, 9, 9, 0)
    p = "{page.host}/{YYYY-MM-DD}/{page.title}/{no.001}_{filename}"
    print(format_filename("http://example.com/a", "Test Title", d, "img.jpg", 5, p))
