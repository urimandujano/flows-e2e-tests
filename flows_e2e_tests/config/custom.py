from dynaconf import Dynaconf


class CensoredDynaconf(Dynaconf):
    dict_fields = ["globus_auth_client_id", "max_wait_time"]
    censored_fields = ["globus_auth_client_secret"]
    censored_field_length = 10

    @property
    def censored(self):
        settings = {}
        for f in self.dict_fields:
            settings[f] = getattr(self, f)

        for f in self.censored_fields:
            value = self._censor_value(getattr(self, f))
            settings[f] = value
        return settings

    def _censor_value(self, value: str):
        value = "*" * 20 + value[-5:]
        return value[-self.censored_field_length :]
