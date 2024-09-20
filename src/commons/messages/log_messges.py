from django.utils.translation import gettext as _


class LogMessages:
    REGISTRATION_ATTEMPT = _("Attempted registration with username: {}")
    FAILED_LOGIN_ATTEMPT = _("Failed login attempt for username: {}")
    UPDATE_POST_STATS = _("Updated stats for post_id {post_id}: average_rate={average_rate}, total_rates={total_rates}")
    ERROR_UPDATE_POST_STATS = _("Error updating stats for post_id {post_id}: {error}")

    @classmethod
    def register_existing_user(cls, username):
        return cls.REGISTRATION_ATTEMPT.format(username)

    @classmethod
    def login_fail(cls, username):
        return cls.FAILED_LOGIN_ATTEMPT.format(username)

    @classmethod
    def update_post_stats(cls, post_id, average_rate, total_rates):
        return cls.UPDATE_POST_STATS.format(post_id=post_id, average_rate=average_rate, total_rates=total_rates)

    @classmethod
    def error_update_post_stats(cls, post_id, error):
        return cls.ERROR_UPDATE_POST_STATS.format(post_id=post_id, error=error)
