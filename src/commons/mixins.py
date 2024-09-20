class FixStatusMixin:
    """
    A mixin that allows to fix the status code of the response.
    """
    fix_status = None

    def finalize_response(self, request, response, *args, **kwargs):
        if self.fix_status is not None:
            response.status_code = self.fix_status
        return super().finalize_response(request, response, *args, **kwargs)


class SingletonMeta(type):
    """Singleton metaclass."""

    def __init__(self, *args, **kwargs):
        super(SingletonMeta, self).__init__(*args, **kwargs)
        self.__instance = None

    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            self.__instance = super(SingletonMeta, self).__call__(*args, **kwargs)
        return self.__instance
