
import os
import requests
import ssl
import warnings
import urllib3
import logging
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager

# Initialize logging
logger = logging.getLogger(__name__)

# Flag to prevent double-patching
_SSL_PATCHED = False

def patch_ssl_requests():
    """
    Apply global SSL and Requests patching to bypass Zscaler/Firewall/Cert blocking on Windows.
    This effectively sets verify=False for ALL requests.
    """
    global _SSL_PATCHED
    if _SSL_PATCHED:
        return
    
    _SSL_PATCHED = True

    logger.warning("⚠️ APPLYING GLOBAL SSL PATCH FOR WINDOWS/ENTERPRISE ENVIRONMENT ⚠️")
    # SIMPLIFIED STRATEGY: Directly monkey-patch Session.request to force verify=False
    # This avoids the complex HTTPAdapter/PoolManager init signatures which vary by urllib3 version
    
    # 1. Disable warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # 2. Patch socket/ssl defaults just in case
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    # 3. Aggressive requests patch
    original_session_request = requests.Session.request
    
    def patched_session_request(self, method, url, *args, **kwargs):
        kwargs['verify'] = False  # FORCE FALSE
        return original_session_request(self, method, url, *args, **kwargs)
        
    requests.Session.request = patched_session_request
    
    # 4. Also patch the top-level api methods because they create transient Sessions
    original_request = requests.request
    
    def patched_top_level_request(method, url, **kwargs):
        kwargs['verify'] = False
        return original_request(method, url, **kwargs)
        
    requests.request = patched_top_level_request
    requests.get = lambda url, **kwargs: patched_top_level_request('GET', url, **kwargs)
    requests.post = lambda url, **kwargs: patched_top_level_request('POST', url, **kwargs)

    print("DEBUG: SSL Patch applied (Simplified Strategy).", flush=True)

if __name__ == "__main__":
    patch_ssl_requests()
    print("Test request starting...")
    try:
        r = requests.get("https://www.google.com")
        print(f"Test request status: {r.status_code}") 
    except Exception as e:
        print(f"Test request failed: {e}")
