# app/views.py
import json, logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from app.db.session import get_session
from .auth import auth_required
from .decorators import handle_engine_errors

logger = logging.getLogger("app")

def extract_sql(request):
    """Extract SQL from POST JSON body or GET query param."""
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            sql = body.get("query")
            if sql:
                return sql
            else:
                raise ValueError("No query provided in POST body")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON body")
    # Fallback to GET
    sql = request.GET.get("q")
    if sql:
        return sql
    raise ValueError("No query provided")

# This prevents Django from blocking POST requests from curl
@csrf_exempt
@auth_required
@handle_engine_errors
def query_endpoint(request):
    try:
        sql = extract_sql(request)
        request.sql = sql
        logger.info(f"Received SQL: {sql}")  # always logs live

        session = get_session()
        result = session.execute(sql)
        logger.info(f"Query succeeded: {sql}")
        return JsonResponse({"status": "OK", "data": result})

    except ValueError as e:
        logger.warning(f"Invalid request: {str(e)}")
        return JsonResponse(
            {"status": "ERROR", "error": {"type": "InvalidRequest", "message": str(e)}},
            status=400
        )
