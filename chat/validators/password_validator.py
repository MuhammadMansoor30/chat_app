import re
from django.core.exceptions import ValidationError

class CustomPasswordValidator:
    def __init__(self):
        self.min_length = 8
        self.special_char_regex = r'[\W_]'  # Matches any non-word character or special character
        self.alphanumeric_regex = r'[A-Za-z0-9]'  # Matches any alphanumeric character
        self.uppercase_regex = r'[A-Z]'  # Matches uppercase letters

    def __call__(self, password):
        errors = []

        # Check for minimum length
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters long.")

        # Check for at least one special character
        if not re.search(self.special_char_regex, password):
            errors.append("Password must contain at least one special character.")

        # Check for at least one alphanumeric character
        if not re.search(self.alphanumeric_regex, password):
            errors.append("Password must contain at least one alphanumeric character.")

        # Check for at least one uppercase letter
        if not re.search(self.uppercase_regex, password):
            errors.append("Password must contain at least one uppercase letter.")

        if errors:
            raise ValidationError(errors)

    def validate(self, password, user=None):
        errors = []

        # Check for minimum length
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters long.")

        # Check for at least one special character
        if not re.search(self.special_char_regex, password):
            errors.append("Password must contain at least one special character.")

        # Check for at least one alphanumeric character
        if not re.search(self.alphanumeric_regex, password):
            errors.append("Password must contain at least one alphanumeric character.")

        # Check for at least one uppercase letter
        if not re.search(self.uppercase_regex, password):
            errors.append("Password must contain at least one uppercase letter.")

        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return "Your password must contain at least 8 characters, including one uppercase letter, one alphanumeric character, and one special character."