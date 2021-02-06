import socket

import logging
logger = logging.getLogger(__name__)


def internet_available(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    checks if the internet is available.
    Attempts to connect to google.com with a timeout of 5 seconds to check
    if the network can be reached.
    Returns:
        - True if connection could be established.
        - False if the internet could not be reached.
    Returned output can be used to add a check for internet availability:
    >>> if internet_available() == True:
    >>> #...do something that requires internet connectivity
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(ex)
        logger.critical(f"Could not reach network!.\nReason: {ex}")
        return False
