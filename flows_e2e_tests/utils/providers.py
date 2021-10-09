from flows_e2e_tests.config import get_settings


def action_provider_url_for_environment(s: str) -> str:
    protocol, fqdn = s.split("://")
    settings = get_settings()
    if settings.current_env != "production" and not fqdn.startswith(
        settings.current_env
    ):
        return f"{protocol}://{settings.current_env}.{fqdn}"
    return s
