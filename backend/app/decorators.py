import functools
from django.http import JsonResponse
from engine.exceptions import ParseError, SchemaError, ExecutionError, EngineError
import logging  # Use the logger from dev.py

logger = logging.getLogger("app")

def handle_engine_errors(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)

        except (ParseError, SchemaError, ExecutionError) as e:
            sql = getattr(request, "sql", "<unknown>")
            logger.warning(f"{e.__class__.__name__}: {str(e)} | SQL: {sql}")
            return JsonResponse(
                {"status": "ERROR", "error": {"type": e.__class__.__name__, "message": str(e)}},
                status=400
            )

        except EngineError as e:
            sql = getattr(request, "sql", "<unknown>")
            logger.error(f"{e.__class__.__name__}: {str(e)} | SQL: {sql}")
            return JsonResponse(
                {"status": "ERROR", "error": {"type": e.__class__.__name__, "message": str(e)}},
                status=400
            )

        except Exception as e:
            sql = getattr(request, "sql", "<unknown>")
            logger.exception(f"Unexpected InternalError | SQL: {sql}")
            return JsonResponse(
                {"status": "ERROR", "error": {"type": "InternalError", "message": "An unexpected error occurred."}},
                status=500
            )

    return wrapper
