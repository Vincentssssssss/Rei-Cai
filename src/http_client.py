import os
import ssl
import sys

import certifi
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

_CONFIGURED = False
_SSL_BACKEND = "none"


def get_ssl_backend() -> str:
    if not _CONFIGURED:
        configure_ssl()
    return _SSL_BACKEND


def configure_ssl() -> str:
    """Configure SSL for macOS/Homebrew Python and other platforms."""
    global _CONFIGURED, _SSL_BACKEND
    if _CONFIGURED:
        return _SSL_BACKEND

    if os.getenv("LLM_INSECURE_SSL", "").lower() in {"1", "true", "yes"}:
        _SSL_BACKEND = "disabled"
        _CONFIGURED = True
        return _SSL_BACKEND

    if sys.platform == "darwin":
        try:
            import truststore

            truststore.inject_into_ssl()
            _SSL_BACKEND = "truststore"
            _CONFIGURED = True
            return _SSL_BACKEND
        except ImportError:
            pass

    ca_bundle = certifi.where()
    os.environ["SSL_CERT_FILE"] = ca_bundle
    os.environ["REQUESTS_CA_BUNDLE"] = ca_bundle

    try:
        ssl_context = ssl.create_default_context(cafile=ca_bundle)
        ssl._create_default_https_context = lambda *args, **kwargs: ssl_context  # type: ignore[attr-defined]
    except Exception:
        pass

    _SSL_BACKEND = "certifi"
    _CONFIGURED = True
    return _SSL_BACKEND


def get_ssl_verify() -> str | bool:
    backend = configure_ssl()
    if backend == "disabled":
        return False
    if backend == "truststore":
        return True
    return certifi.where()


def create_http_session() -> requests.Session:
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


configure_ssl()
