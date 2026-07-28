import os
import ssl

import certifi
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

_CONFIGURED = False


def configure_ssl() -> str:
    """Apply certifi CA bundle for macOS/Homebrew Python SSL issues."""
    global _CONFIGURED
    ca_bundle = certifi.where()
    os.environ["SSL_CERT_FILE"] = ca_bundle
    os.environ["REQUESTS_CA_BUNDLE"] = ca_bundle

    try:
        ssl_context = ssl.create_default_context(cafile=ca_bundle)
        ssl._create_default_https_context = lambda *args, **kwargs: ssl_context  # type: ignore[attr-defined]
    except Exception:
        pass

    _CONFIGURED = True
    return ca_bundle


def get_ssl_verify() -> str:
    if not _CONFIGURED:
        configure_ssl()
    return certifi.where()


def create_http_session() -> requests.Session:
    if not _CONFIGURED:
        configure_ssl()

    session = requests.Session()
    retry = Retry(
        total=2,
        connect=2,
        read=2,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("POST", "GET"),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.verify = get_ssl_verify()
    return session


# Configure as early as possible when this module is imported.
configure_ssl()
