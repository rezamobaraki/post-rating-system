from django.utils.translation import gettext as _


class LogMessages:
    @staticmethod
    def register_existing_user(username):
        return _("Attempted registration with existing username: {}").format(username)

    @staticmethod
    def login_fail(username):
        return _("Failed login attempt for username: {}").format(username)
