"""Deployment-only safeguards. Do not affect existing VM or local tests."""
import os


def auth_enabled() -> bool:
    """Нужен ли вход по паролю.

    На RelaxDev сайт открыт без пароля, пока не задано APP_AUTH=1. Вне RelaxDev
    (ВМ, локально) поведение прежнее: пароль включается заданным APP_PASSWORD.
    Запись данных (загрузка, удаление, настройки) на RelaxDev при APP_AUTH!=1
    тоже открыта: отдельного ключа, как у дашбордов, в приложении нет.
    """
    if os.environ.get("RELAXDEV_DEPLOY") == "1":
        return os.environ.get("APP_AUTH") == "1"
    return bool(os.environ.get("APP_PASSWORD", ""))


def validate_deployment() -> None:
    if os.environ.get("RELAXDEV_DEPLOY") != "1":
        return
    if not os.environ.get("DATABASE_URL", "").strip():
        raise RuntimeError("RelaxDev: DATABASE_URL is required (create a separate PostgreSQL)")
    if auth_enabled():
        if not os.environ.get("APP_PASSWORD", "").strip():
            raise RuntimeError("RelaxDev: APP_PASSWORD is required when APP_AUTH=1")
        if not os.environ.get("APP_USER", "admin").strip():
            raise RuntimeError("RelaxDev: APP_USER must not be empty when APP_AUTH=1")
    if os.environ.get("MAIL_HOST") and os.environ.get("MAIL_IMPORT_ENABLED") != "1":
        # Email importer is deliberately not started before old/new data reconciliation.
        pass
