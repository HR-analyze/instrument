import pytest

from app.deploy_config import auth_enabled, validate_deployment
from app import mail_import


def test_relaxdev_requires_database(monkeypatch):
    monkeypatch.setenv("RELAXDEV_DEPLOY", "1")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("APP_PASSWORD", raising=False)
    monkeypatch.delenv("APP_AUTH", raising=False)
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        validate_deployment()
    monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/example")
    validate_deployment()  # пароль не обязателен: сайт открыт


def test_relaxdev_password_is_required_only_with_app_auth(monkeypatch):
    monkeypatch.setenv("RELAXDEV_DEPLOY", "1")
    monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/example")
    monkeypatch.setenv("APP_AUTH", "1")
    monkeypatch.delenv("APP_PASSWORD", raising=False)
    with pytest.raises(RuntimeError, match="APP_PASSWORD"):
        validate_deployment()
    monkeypatch.setenv("APP_PASSWORD", "test-secret")
    validate_deployment()


def test_relaxdev_is_open_unless_app_auth(monkeypatch):
    monkeypatch.setenv("RELAXDEV_DEPLOY", "1")
    monkeypatch.setenv("APP_PASSWORD", "left-over-from-before")
    monkeypatch.delenv("APP_AUTH", raising=False)
    assert auth_enabled() is False
    monkeypatch.setenv("APP_AUTH", "1")
    assert auth_enabled() is True


def test_outside_relaxdev_password_decides(monkeypatch):
    monkeypatch.delenv("RELAXDEV_DEPLOY", raising=False)
    monkeypatch.delenv("APP_AUTH", raising=False)
    monkeypatch.setenv("APP_PASSWORD", "pw")
    assert auth_enabled() is True
    monkeypatch.setenv("APP_PASSWORD", "")
    assert auth_enabled() is False


def test_relaxdev_does_not_start_mail_automatically(monkeypatch):
    monkeypatch.setenv("RELAXDEV_DEPLOY", "1")
    monkeypatch.setenv("MAIL_HOST", "imap.example.org")
    monkeypatch.delenv("MAIL_IMPORT_ENABLED", raising=False)
    assert mail_import.start() is None
    assert mail_import.snapshot()["enabled"] is False


def test_local_mode_unchanged(monkeypatch):
    monkeypatch.delenv("RELAXDEV_DEPLOY", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("APP_PASSWORD", raising=False)
    validate_deployment()
