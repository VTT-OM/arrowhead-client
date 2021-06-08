import requests
import json


class Manager:
    """ Manager for Arrowhead systems and authorizations """

    def __init__(self, config_json: str):

        with open(config_json, "r") as file:
            config = json.load(file)
        self.service_registry_url = config["serviceRegistryUrl"]
        self.authorization_url = config["authorizationUrl"]

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

    def authorize_system(self, system_id: int, service_definition: str):
        """ Authorize system for service """

        with requests.Session() as ses:
            if self._secure:
                ses.cert = (self.cert, self.key)
                ses.verify = self.ca

            # Get service by definition
            response = ses.get(
                f"{self.service_registry_url}/mgmt/servicedef/{service_definition}"
            )
            response.raise_for_status()
            services = response.json()["data"]

            # Collect ids for authorization
            ids = {}
            ids["consumerId"] = system_id
            ids["interfaceIds"] = []
            ids["providerIds"] = []
            ids["serviceDefinitionIds"] = []
            for service in services:
                for interface in service["interfaces"]:
                    ids["interfaceIds"].append(interface["id"])
                ids["providerIds"].append(service["provider"]["id"])
                ids["serviceDefinitionIds"].append(service["serviceDefinition"]["id"])

            response = ses.post(
                f"{self.authorization_url}/mgmt/intracloud",
                json=ids,
            )
            response.raise_for_status()

        return response.ok

    def delete_authorizations(self):
        """ Delete authorizations """

        with requests.Session() as ses:
            if self._secure:
                ses.cert = (self.cert, self.key)
                ses.verify = self.ca

            response = ses.get(f"{self.authorization_url}/mgmt/intracloud")
            response.raise_for_status()

            for authorization in response.json()["data"]:
                response = ses.delete(
                    f"{self.authorization_url}/mgmt/intracloud/{authorization['id']}"
                )
                response.raise_for_status()

        return response.ok
