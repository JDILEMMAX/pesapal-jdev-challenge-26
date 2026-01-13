from django.http import JsonResponse
from app.db.session import get_session
from .auth import auth_required


@auth_required
def query_endpoint(request):
    sql = request.GET.get("q")
    if not sql:
        return JsonResponse(
            {"error": "No query provided"},
            status=400
        )

    session = get_session()

    try:
        result = session.execute(sql)
        return JsonResponse(
            {"status": "OK", "data": result},
            status=200
        )
    except Exception as e:
        return JsonResponse(
            {"status": "ERROR", "message": str(e)},
            status=500
        )
