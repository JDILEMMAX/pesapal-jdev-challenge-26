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


# ============================================
# STRUCTURED REST ENDPOINTS
# ============================================

@csrf_exempt
def health_check(request):
    """GET /health - Server health check."""
    return JsonResponse({"status": "OK", "message": "Server is healthy"})


@csrf_exempt
@auth_required
def get_stats(request):
    """GET /stats - Database statistics."""
    try:
        session = get_session()
        engine = session.engine
        
        stats = {
            "tables": len(engine.catalog.tables),
            "table_names": list(engine.catalog.tables.keys()),
        }
        
        return JsonResponse({"status": "OK", "data": stats})
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        return JsonResponse({"status": "ERROR", "error": str(e)}, status=500)


@csrf_exempt
@auth_required
def list_tables(request):
    """GET /tables - List all tables."""
    try:
        session = get_session()
        engine = session.engine
        
        tables = []
        for table_name in engine.catalog.tables:
            rows = engine.get_rows(table_name)
            tables.append({
                "name": table_name,
                "row_count": len(rows)
            })
        
        return JsonResponse({"status": "OK", "data": {"tables": tables}})
    except Exception as e:
        logger.error(f"List tables error: {str(e)}")
        return JsonResponse({"status": "ERROR", "error": str(e)}, status=500)


@csrf_exempt
@auth_required
def get_table_schema(request, table_name):
    """GET /tables/{name} - Get table schema."""
    try:
        session = get_session()
        engine = session.engine
        
        table = engine.catalog.get_table(table_name.upper())
        
        columns = []
        for col in table.columns:
            columns.append({
                "name": col.name,
                "dtype": col.dtype.__name__,
                "nullable": col.nullable,
                "primary_key": col.primary_key,
                "auto_increment": col.auto_increment,
                "constraints": col.constraints
            })
        
        return JsonResponse({
            "status": "OK",
            "data": {
                "table": table_name,
                "columns": columns
            }
        })
    except Exception as e:
        logger.error(f"Get table error: {str(e)}")
        return JsonResponse({"status": "ERROR", "error": str(e)}, status=404)


@csrf_exempt
@auth_required
def get_table_rows(request, table_name):
    """GET /tables/{name}/rows - Get all rows in a table."""
    try:
        session = get_session()
        engine = session.engine
        
        rows = engine.get_rows(table_name.upper())
        
        return JsonResponse({
            "status": "OK",
            "data": {
                "table": table_name,
                "rows": rows,
                "row_count": len(rows)
            }
        })
    except Exception as e:
        logger.error(f"Get rows error: {str(e)}")
        return JsonResponse({"status": "ERROR", "error": str(e)}, status=404)


@csrf_exempt
@auth_required
def insert_row(request, table_name):
    """POST /tables/{name}/rows/new/ - Insert a row into a table."""
    if request.method != "POST":
        return JsonResponse({"status": "ERROR", "error": "Method not allowed"}, status=405)
    
    try:
        body = json.loads(request.body)
        data = body.get("data", {})
        
        session = get_session()
        engine = session.engine
        table = engine.catalog.get_table(table_name.upper())
        
        # Convert data dict to ordered list matching column order
        values = [data.get(col.name.lower()) for col in table.columns]
        
        engine.insert_row(table_name.upper(), values)
        
        return JsonResponse({
            "status": "OK",
            "message": f"Row inserted into {table_name}",
            "data": data
        })
    except Exception as e:
        logger.error(f"Insert row error: {str(e)}")
        return JsonResponse({"status": "ERROR", "error": str(e)}, status=400)


@csrf_exempt
@auth_required
def delete_row(request, table_name, row_id):
    """DELETE /tables/{name}/rows/{id} - Delete a row from a table."""
    if request.method != "DELETE":
        return JsonResponse({"status": "ERROR", "error": "Method not allowed"}, status=405)
    
    try:
        session = get_session()
        engine = session.engine
        table = engine.catalog.get_table(table_name.upper())
        
        # Build WHERE predicate for the primary key
        # Assuming first column is the primary key
        pk_col = table.columns[0]
        
        def where_fn(row):
            return row.get(pk_col.name.lower()) == int(row_id)
        
        result = engine.delete_rows(table_name.upper(), where_fn=where_fn)
        deleted = result[0].get("deleted", 0)
        
        if deleted == 0:
            return JsonResponse({"status": "ERROR", "error": "Row not found"}, status=404)
        
        return JsonResponse({
            "status": "OK",
            "message": f"Row {row_id} deleted from {table_name}",
            "data": {"deleted": deleted}
        })
    except Exception as e:
        logger.error(f"Delete row error: {str(e)}")
        return JsonResponse({"status": "ERROR", "error": str(e)}, status=400)


@csrf_exempt
@auth_required
@handle_engine_errors
def execute_query(request):
    """POST /query/execute/ - Execute arbitrary SQL query."""
    if request.method != "POST":
        return JsonResponse({"status": "ERROR", "error": "Method not allowed"}, status=405)
    
    try:
        body = json.loads(request.body)
        sql = body.get("query")
        
        if not sql:
            raise ValueError("No query provided")
        
        logger.info(f"Received SQL: {sql}")
        
        session = get_session()
        raw_result = session.execute(sql)
        
        return JsonResponse({
            "status": "OK",
            "data": raw_result.get("data", [])
        })
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        return JsonResponse({"status": "ERROR", "error": str(e)}, status=400)


@csrf_exempt
@auth_required
def reset_database(request):
    """POST /reset - Reset the database (delete all tables)."""
    if request.method != "POST":
        return JsonResponse({"status": "ERROR", "error": "Method not allowed"}, status=405)
    
    try:
        session = get_session()
        engine = session.engine
        
        # Drop all tables
        table_names = list(engine.catalog.tables.keys())
        for table_name in table_names:
            engine.drop_table(table_name)
        
        return JsonResponse({
            "status": "OK",
            "message": f"Dropped {len(table_names)} tables",
            "data": {"tables_dropped": table_names}
        })
    except Exception as e:
        logger.error(f"Reset error: {str(e)}")
        return JsonResponse({"status": "ERROR", "error": str(e)}, status=500)
