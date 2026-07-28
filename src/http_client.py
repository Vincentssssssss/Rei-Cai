import certifi


def get_ssl_verify() -> str | bool:
    return certifi.where()
