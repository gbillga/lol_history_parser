from urllib.parse import quote
import os


def encode_string(input: str) -> str:
    """
    Encodes a string so that it can be safely used in a URL query.

    This function takes an input string and encodes it using `urllib.parse.quote`,
    making it suitable for inclusion in a URL query string by escaping special characters.

    Args:
        input (str): The string to be encoded.

    Returns:
        str: The encoded input string.

    Example:
        >>> encoded_string = encode_string("Hello World!")
        >>> print(encoded_string)
        'Hello%20World%21'
    """
    return quote(input)


def get_riotid() -> dict:
    """
    Retrieves and encodes the Riot ID from environment variables.

    This function fetches the summoner's name and tag stored in the environment variables
    'SUMMONERS_NAME' and 'TAG', respectively. It then encodes these values using the
    `encode_string` function and returns them in a dictionary.

    Returns:
        dict: A dictionary containing the encoded summoner's name and tag.
              The dictionary has the following keys:
                - "summoners_name": The summoner's name retrieved from the environment variable.
                - "summoners_tag": The summoner's tag retrieved from the environment variable.
                - "encoded_summoners_name": The encoded summoner's name.
                - "encoded_summoners_tag": The encoded summoner's tag.

    Example:
        >>> riot_id = get_riotid()
        >>> print(riot_id)
        {'summoners_name': 'encoded_name', 'summoners_tag': 'encoded_tag',
         'encoded_summoners_name': 'encoded_name', 'encoded_summoners_tag': 'encoded_tag'}
    """
    output = dict()
    output["summoners_name"] = os.getenv("SUMMONERS_NAME")
    output["summoners_tag"] = os.getenv("TAG")
    output["encoded_summoners_name"] = encode_string(os.getenv("SUMMONERS_NAME"))
    output["encoded_summoners_tag"] = encode_string(os.getenv("TAG"))
    return output


def get_api_key() -> str:
    """
    Retrieves the API key from environment variables.

    This function fetches the API key stored in the environment variable 'API_KEY'.
    It is expected that this environment variable is set before running the function.

    Returns:
        str: The API key as a string. If the API key is not found, it returns None.

    Example:
        >>> api_key = get_api_key()
        >>> print(api_key)
        'your_api_key'
    """
    return os.getenv("API_KEY")


def check_if_folder_exists(folder_path: str) -> bool:
    """
    Checks if a folder exists at the specified path.

    This function checks if a folder exists at the given path using the `os.path.exists` function.
    It returns True if the folder exists, and False otherwise.

    Args:
        folder_path (str): The path of the folder to check for existence.

    Returns:
        bool: True if the folder exists, False otherwise.

    Example:
        >>> check_if_folder_exists("./data")
        True

    Notes:
        - This function can be used to check for the existence of any folder specified by its path.
        - It returns True even if the specified path points to a file rather than a folder.
    """
    return os.path.exists(folder_path)
