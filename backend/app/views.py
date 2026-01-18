# app/views.py
import json, logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from app.db.session import get_session
from .auth import auth_required
from .decorators import handle_engine_errors
from collections.abc import Iterator


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

    sql = request.GET.get("q")
    if sql:
        return sql

    raise ValueError("No query provided")


def normalize_result(sql: str, result):
    """
    Session already returns normalized payloads.
    This function is now a pass-through.
    """

    sql_upper = sql.strip().upper()

    payload = {
        "data": result.get("data", [])
    }

    # propagate warning if present
    if "warning" in result:
        payload["warning"] = result["warning"]

    if sql_upper.startswith("CREATE TABLE"):
        payload["message"] = "Table created successfully"

    elif sql_upper.startswith("INSERT"):
        payload["message"] = "Insert executed successfully"

    elif sql_upper.startswith("SHOW TABLES"):
        if not payload["data"]:
            payload["message"] = "No tables found"

    return payload

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
        raw_result = session.execute(sql)

        data = normalize_result(sql, raw_result)

        logger.info(f"Query succeeded: {sql}")
        return JsonResponse({
            "status": "OK",
            "data": data
        })

    except ValueError as e:
        logger.warning(f"Invalid request: {str(e)}")
        return JsonResponse(
            {
                "status": "ERROR",
                "error": {
                    "type": "InvalidRequest",
                    "message": str(e)
                }
            },
            status=400
        )
