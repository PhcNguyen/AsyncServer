
from sources.model.utils import InternetProtocol



class NetworkConfigs:
    """
    Configuration settings for network communication.

    Attributes:
    - DEBUG (bool): Indicates if debug mode is enabled.
    - local (str): Local IP address of the machine.
    - public (str): Public IP address of the machine.
    - port (int): Port number for network communication (default is 7272).

    """
    DEBUG: bool = False

    MAX_CONNECTIONS = 1000  # Define your max connections

    LOCAL: str = InternetProtocol.local()  # Retrieve local IP address
    PUBLIC: str = InternetProtocol.public()  # Retrieve public IP address
    PORT: int = 7272  # Default port number