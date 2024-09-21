from django.utils.translation import gettext as _


class LogMessages:
    REGISTRATION_ATTEMPT = _("Attempted registration with username: {}")
    FAILED_LOGIN_ATTEMPT = _("Failed login attempt for username: {}")
    NO_NEW_RATE = _("No new rates to apply.")
    UPDATE_POST_STATS = _(
        "Updated stats for post_id {post_id}: average_rates={average_rates}, total_rates={total_rates}"
    )
    ERROR_UPDATE_POST_STATS = _("Error updating stats: {error}")

    @classmethod
    def register_existing_user(cls, username):
        return cls.REGISTRATION_ATTEMPT.format(username)

    @classmethod
    def login_fail(cls, username):
        return cls.FAILED_LOGIN_ATTEMPT.format(username)

    @classmethod
    def no_new_rate(cls, post_id, average_rates, total_rates):
        return cls.NO_NEW_RATE.format(post_id=post_id, average_rates=average_rates, total_rates=total_rates)

    @classmethod
    def update_post_stats(cls, post_id, average_rates, total_rates):
        return cls.UPDATE_POST_STATS.format(post_id=post_id, average_rates=average_rates, total_rates=total_rates)

    @classmethod
    def error_update_post_stats(cls, error):
        return cls.ERROR_UPDATE_POST_STATS.format(error=error)
