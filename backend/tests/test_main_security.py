from fastapi.middleware.cors import CORSMiddleware

from app.main import app


def test_cors_is_not_wildcard_by_default():
    cors = next(m for m in app.user_middleware if m.cls is CORSMiddleware)
    assert cors.kwargs["allow_origins"] == ["http://localhost:5173", "http://127.0.0.1:5173"]
    assert cors.kwargs["allow_credentials"] is True
