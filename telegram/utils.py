from datetime import datetime

from pytz import timezone


def convert_date(date_str):
    """
    Converts a UTC datetime string to a datetime string in the Moscow timezone.

    Args:
        date_str (str): UTC datetime string in the format
        '%Y-%m-%dT%H:%M:%S.%fZ'.

    Returns:
        str: Datetime string in the Moscow timezone in the format
        '%d-%m-%Y %H:%M'.
    """
    dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    dt = dt.replace(tzinfo=timezone('UTC'))
    dt = dt.astimezone(timezone('Europe/Moscow'))
    return dt.strftime('%d-%m-%Y %H:%M')


class User:
    """
    User class for handling and formatting user data.

    Attributes:
        data (dict): Dictionary of user data.
        name (str): User's name.
        status (str): User's status.
        last_visit (str): The last time the user visited.
        quota (int): Remaining monthly quota in GB.
        problems (str): Any problems associated with the user.
    """

    def __init__(self, data):
        """
        Initializes a User object with the provided data.

        Args:
            data (dict): Dictionary of user data.
        """
        self.data = data
        self.name = self.data.get('UserName')
        self.status = self.data.get('Status')
        self.last_visit = (
            convert_date(self.data.get('LastVisitHour'))
            if self.data.get('LastVisitHour')
            else None
        )
        self.quota = self.data.get('MonthlyQuotaRemainingGB')
        self.problems = self.data.get('Problems')

    @property
    def is_active(self):
        """
        Checks if the user is active.

        Returns:
            bool: True if the user's status is 'green' (active),
            False otherwise.
        """
        return self.status == 'green'

    @property
    def has_visited(self):
        """
        Checks if the user has visited.

        Returns:
            bool: True if the user's last visit is not None, False otherwise.
        """
        return self.last_visit is not None

    @property
    def has_low_quota(self):
        """
        Checks if the user has low quota remaining.

        Returns:
            bool: True if the user's quota is less than 10 GB, False otherwise.
        """
        return self.quota < 10

    def format_message(self):
        """
        Formats a message with the user's data.

        Returns:
            str: Formatted message with the user's data.
        """
        status_icon = '🟩' if self.is_active else '🟥'
        problems_string = f'⛔: {self.problems} ' if self.problems else ''
        time_string = (
            f'<b>Last enter:</b> <code>{self.last_visit}</code>'
            if self.last_visit
            else '<b>Last enter:</b>'
        )
        return (
            f'{status_icon} :<code>{self.name}</code> '
            f'{problems_string}'
            f'🔃: <code>{self.quota} GB</code>\n'
            f'{time_string}\n'
            f'--------------------------------------------------------\n'
        )
