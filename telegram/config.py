import os

from dotenv import load_dotenv

# Specifies the path of the .env file which contains environment variables.
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

# Loads the .env file.
load_dotenv(dotenv_path)

# Gets the Bot API token from environment variable.
BOT_API = os.getenv('BOT_API')

# Gets the chat ID from environment variable and converts it to integer.
CHAT_ID = int(os.getenv('CHAT_ID'))

# Gets the start message from environment variable,
# defaults to 'Hello World!' if not set.
START_MSG = os.getenv('START_MSG', 'Hello World!')


def check_credentials():
    """
    Checks if the Bot API token and chat ID are set in
    the environment variables.

    Returns:
        str: Error message if either the Bot API token or chat ID is not set.
    """
    if not [BOT_API, CHAT_ID]:
        return 'You must create .env file with BOT_API and CHAT_ID'


# Calls the check_credentials function to ensure the
# Bot API token and chat ID are set.
check_credentials()
