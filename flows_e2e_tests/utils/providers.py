from flows_e2e_tests.config import settings


def action_provider_url_for_environment(s: str) -> str:
    protocol, fqdn = s.split("://")
    if settings.current_env != "production" and not fqdn.startswith(
        settings.current_env
    ):
        return f"{protocol}://{settings.current_env}.{fqdn}"
    return s
