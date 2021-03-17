import requests
import json


class Provider:
    """ Provider for registering services to Arrowhead """

    def __init__(self, config_json: str):

        with open(config_json, "r") as file:
            config = json.load(file)
        self.service_registry_url = config["serviceRegistryUrl"]
        self.system = config["providerSystem"]
        self.services = []
        for service in config["services"]:
            service["providerSystem"] = self.system
            self.services.append(service)

        self._secure = self.set_certificates(config.get("certificates", None))

    def set_certificates(self, certificates: dict = None) -> bool:
        """Set certificates from a dict containing filepaths to files

        certificate:            "*.crt"
        key:                    "*.key"
        certificate_authority:  "*.ca"
        """

        if certificates is not None:
            try:
                self.cert = certificates["certificate"]
                self.key = certificates["key"]
                self.ca = certificates["certificate_authority"]
                return True
            except KeyError:
                pass
        return False

    def register_services(self):
        """ Register services """

        with requests.Session() as ses:
            if self._secure:
                ses.cert = (self.cert, self.key)
                ses.verify = self.ca

            for service in self.services:
                response = ses.post(
                    f"{self.service_registry_url}/register", json=service
                )
                response.raise_for_status()

        return response.ok

    def unregister_services(self):
        """ Unregister provider """

        with requests.Session() as ses:
            if self._secure:
                ses.cert = (self.cert, self.key)
                ses.verify = self.ca

            params = {
                "system_name": self.system["systemName"],
                "address": self.system["address"],
                "port": self.system["port"],
            }

            for service in self.services:
                params["service_definition"] = service["serviceDefinition"]

                response = ses.delete(
                    f"{self.service_registry_url}/unregister", params=params
                )
                response.raise_for_status()

        return response.ok
