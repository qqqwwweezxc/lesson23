from django.core.cache import cache


class BookListCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:
            return self.get_response(request)

        cache_key = f"page:{request.path}"
        cached_response = cache.get(cache_key)

        if cached_response:
            return cached_response

        response = self.get_response(request)
        cache.set(cache_key, response, 60)
        return response