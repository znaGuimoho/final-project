from fastapi import Request
from fastapi.exceptions import HTTPException

# ── Error messages shown on the page ─────────────────────────────────────────
ERROR_MESSAGES = {
    400: ("Bad Request", "The request was invalid or malformed."),
    401: ("Unauthorized", "You need to be logged in to access this page."),
    403: ("Forbidden", "You don't have permission to access this page."),
    404: ("Page Not Found", "The page you're looking for doesn't exist."),
    405: ("Method Not Allowed", "This action isn't allowed here."),
    409: ("Conflict", "There was a conflict with the current state of the resource."),
    410: ("Gone", "This page has been permanently removed."),
    422: ("Unprocessable", "The request data couldn't be processed."),
    429: ("Too Many Requests", "You're doing that too fast. Please slow down."),
    500: ("Server Error", "Something went wrong on our end. Please try again later."),
    502: ("Bad Gateway", "The server received an invalid response."),
    503: (
        "Service Unavailable",
        "The service is temporarily unavailable. Try again soon.",
    ),
}


def register_exception_handlers(app, templates):
    """
    Call this in main.py after creating the FastAPI app:

        from app.routers.errors import register_exception_handlers
        register_exception_handlers(app)
    """

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        code = exc.status_code
        title, message = ERROR_MESSAGES.get(
            code, ("Error", exc.detail or "An unexpected error occurred.")
        )

        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "code": code,
                "title": title,
                "message": message,
            },
            status_code=code,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        """Catch-all for any unhandled Python exception — shows a clean 500."""
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "code": 500,
                "title": "Server Error",
                "message": "Something went wrong on our end. Please try again later.",
            },
            status_code=500,
        )
