from django.contrib.auth.middleware import LoginRequiredMiddleware as DjangoLoginMiddleware

class LoginRequiredMiddleware(DjangoLoginMiddleware):
    EXCEPTION_URLS = [
        "/login/",
        "/logout/",
    ]
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.path in self.EXCEPTION_URLS:
            return None

        return super().process_view(request, view_func, view_args, view_kwargs)
