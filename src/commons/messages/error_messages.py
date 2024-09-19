from enum import Enum

from django.utils.translation import gettext_lazy as _


class ErrorMessages(Enum):
    REGISTRATION_FAILED = {
        "message": _("Registration failed. Please check your input and try again."),
        "code": "registration_failed"
    }
    INVALID_CREDENTIALS = {
        "message": _("Invalid credentials provided."),
        "code": "invalid_credential"
    }
    UNKNOWN_ERROR = {
        "message": _("Unknown error occurred"),
        "code": "unknown_error"
    }

    @property
    def message(self):
        return self.value["message"]

    @property
    def code(self):
        return self.value["code"]
