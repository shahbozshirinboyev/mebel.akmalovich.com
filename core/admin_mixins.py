from django.contrib import admin
from django.http import HttpResponseRedirect
from urllib.parse import urlparse, urlencode

class PreserveFiltersAdminMixin:
    """
    Admin mixin that preserves filter states in session storage.
    """
    def changelist_view(self, request, extra_context=None):
        session_key = f'admin_filters_{request.resolver_match.url_name}'
        current_path = request.path
        referer = request.META.get('HTTP_REFERER', '')

        def same_model():
            return referer.startswith(request.build_absolute_uri(current_path))

        # 🔁 RESTORE: boshqa modeldan qaytildi
        if not request.GET and session_key in request.session and not same_model():
            saved_filters = request.session[session_key]
            if saved_filters:
                return HttpResponseRedirect(
                    f"{request.path}?{self._encode(saved_filters)}"
                )

        # ❌ RESET: shu model ichida "Сбросить"
        if not request.GET and same_model():
            request.session.pop(session_key, None)
            request.session.modified = True
            return super().changelist_view(request, extra_context)

        # � SAQLASH
        if request.GET:
            filter_keys = set()

            for f in self.get_list_filter(request):
                if hasattr(f, 'parameter_name'):
                    filter_keys.add(f.parameter_name)
                else:
                    filter_keys.add(str(f))

            filter_keys.update(getattr(self, 'preserved_filters', set()))

            request.session[session_key] = {
                k: v for k, v in request.GET.items()
                if any(k == fk or k.startswith(f"{fk}__") for fk in filter_keys)
                or k == 'q'
            }
            request.session.modified = True

        return super().changelist_view(request, extra_context)

    def _encode(self, data):
        return urlencode(data, doseq=True)
