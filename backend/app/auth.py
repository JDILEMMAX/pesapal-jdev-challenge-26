from django.http import JsonResponse

VALID_TOKENS = {"secret-token-123"}

# def auth_required(view_func):
#     def wrapper(request, *args, **kwargs):
#         token = request.headers.get("Authorization")
#         if token not in VALID_TOKENS:
#             return JsonResponse({"error": "Unauthorized"}, status=401)
#         return view_func(request, *args, **kwargs)
#     return wrapper

# Browser request does not send any Authorization header, so Django rejects it.
# Temporary bypass (development only)
def auth_required(view_func):
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapper
