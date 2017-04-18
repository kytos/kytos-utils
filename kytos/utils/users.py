"""Module used to handle Users in Napps Server."""
import logging
import re
from getpass import getpass

from kytos.utils.client import UsersClient

log = logging.getLogger(__name__)

NAME_PATTERN = ("\t- insert only letters", r'[a-zA-Z][a-zA-Z]{2,}$')
USERNAME_PATTERN = ("\t- start with letter\n"
                    "\t- insert only numbers and letters",
                    r'[a-zA-Z][a-zA-Z0-9_]{2,}$')
PASSWORD_PATTERN = ("\t- insert only the caracters:"
                    " [letters, numbers, _, %, &, -, $]"
                    "\n\t- must be at least 6 characters",
                    r'[a-zA-Z0-9_%\-&$]{6,}$')
EMAIL_PATTERN = ("\t- follow the format: <login>@<domain>\n"
                 "\t\te.g. john@test.com", r'[^@]+@[^@]+\.[^@]+')
PHONE_PATTERN = ("\t- insert only numbers", r'\d*$')


class UsersManager:
    """Class used to handle users stored by Napps server."""

    attributes = {
        "username": {"field_name": "Username (Required)",
                     "pattern": USERNAME_PATTERN},
        "first_name": {"field_name": "First Name (Required)",
                       "pattern": NAME_PATTERN},
        "last_name": {"field_name": "Last Name", "pattern": NAME_PATTERN},
        "password": {"field_name": "Password (Required)",
                     "pattern": PASSWORD_PATTERN},
        "email": {"field_name": "Email (Required)", "pattern": EMAIL_PATTERN},
        "phone": {"field_name": "Phone", "pattern": PHONE_PATTERN},
        "city": {"field_name": "City", "pattern": NAME_PATTERN},
        "state": {"field_name": "State", "pattern": NAME_PATTERN},
        "country": {"field_name": "Country", "pattern": NAME_PATTERN}
    }

    required = ["username", "first_name", "password", "email"]

    def __init__(self):
        """Constructor of UsersManager do not need parameters."""
        self._users_client = UsersClient()

    def register(self):
        """Method used to register a new user.

        This method will ask for user attributes and create the user in
        Napps server, when All required fields is filled.

        Returns:
            result(string): Response of user registration process.
        """
        user = {}

        print('--------------------------------------------------------------')
        print('Welcome to the user registration process.')
        print('--------------------------------------------------------------')
        print("To continue you must fill the following fields.")
        for attribute, value in self.attributes.items():

            is_required = attribute in self.required
            field_name = value['field_name']
            pattern = value['pattern']

            if attribute != 'password':
                user[attribute] = self.ask_question(field_name, pattern,
                                                    is_required)
            else:
                user[attribute] = self.ask_question(field_name, pattern,
                                                    password=True)

        return self._users_client.register(user)

    def ask_question(self, field_name, pattern=NAME_PATTERN, is_required=False,
                     password=False):
        """Method used to ask a question and get the input values.

        This method will validade the input values.
        Args:
            field_name(string): Field name used to ask for input value.
            pattern(tuple): Pattern to validate the input value.
            is_required(bool): Boolean value if the input value is required.
            password(bool): Boolean value to get input password with mask.
        Returns:
            input_value(string): Input value validated.
        """
        input_value = ""
        question = ("Insert the field using the pattern below:"
                    "\n{}\n{}: ".format(pattern[0], field_name))

        while not input_value:
            input_value = getpass(question) if password else input(question)

            if not (input_value or is_required):
                break

            if password:
                confirm_password = getpass('Confirm your password: ')
                if confirm_password != input_value:
                    print("Password does not match")
                    input_value = ""

            if not self.valid_attribute(input_value, pattern[1]):
                error_message = "The content must fit the pattern: {}\n"
                print(error_message.format(pattern[0]))
                input_value = ""

        return input_value

    @classmethod
    def valid_attribute(cls, attribute, pattern):
        """Check the validity of the given 'attribute' using the given pattern.

        Args:
            attribute(string): String with the value of an attribute
            pattern(string): Pattern used to validate the attribute value.
        Returns:
            pattern_found(bool): Return True if the pattern match.
        """
        return attribute and re.match(pattern, attribute)
