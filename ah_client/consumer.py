import requests
import paho.mqtt.client as mqtt
import json


class Consumer:
    """ Consumer for orchestrating usage of available Arrowhead services """

    _interfaces = ["HTTP-INSECURE-JSON", "MQTT-INSECURE-JSON"]
    _secure_interfaces = ["HTTPS-SECURE-JSON", "MQTTS-SECURE-JSON"]

    def __init__(self, config_json: str):

        with open(config_json, "r") as file:
            config = json.load(file)
        self.orchestrator_url = config["arrowheadOrchestratorUrl"]
        self.system = config["requesterSystem"]
        self.service = None

        self._secure = self.set_certificates(config.get("certificates", None))

        # Init interfaces
        self.mqtt = None
        self.http = None
        self.http_service_url = None

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
            except KeyError as error:
                print(error)
                pass
        return False

    def orchestrate(
        self, service_definition: str = None, interface: str = None
    ) -> [dict]:
        """ Orchestrate for given service """

        with requests.Session() as ses:
            if self._secure:
                ses.cert = (self.cert, self.key)
                ses.verify = self.ca

            msg = {
                "requesterSystem": self.system,
            }

            if service_definition is not None:
                if interface is None:
                    if self._secure:
                        interface = self._secure_interfaces[0]
                    else:
                        interface = self._interfaces[0]
                elif interface not in [*self._interfaces, *self._secure_interfaces]:
                    raise ValueError("Given interface is not supported")
                msg["requestedService"] = {
                    "serviceDefinitionRequirement": service_definition,
                    "interfaceRequirements": [interface],
                }
                msg["orchestrationFlags"] = {"overrideStore": True}

            response = ses.post(f"{self.orchestrator_url}/orchestration", json=msg)
            response.raise_for_status()

        services = response.json().get("response")
        if len(services) > 0:
            self.service = services[0]
            self._setup_interfaces(self.service)
        return self.service

    def _setup_interfaces(self, service: dict):
        """Set up interfaces for given service

        Either secure or insecure, depending on if the consumer itself is secure"""

        # Reset interfaces to None
        self.mqtt = None
        self.http = None
        self.http_service_url = None

        for interface in service["interfaces"]:
            interface_name = interface["interfaceName"]
            # Only check for secure interfaces if consumer is set secure
            if self._secure:
                if interface_name in self._secure_interfaces:
                    scheme = interface_name.split("-")[0].lower()
                    if scheme == "mqtts":
                        self._setup_mqtt_interface(service)
                    elif scheme == "https":
                        self._setup_http_interface(service)
            else:
                if interface_name in self._interfaces:
                    scheme = interface_name.split("-")[0].lower()
                    if scheme == "mqtt":
                        self._setup_mqtt_interface(service)
                    elif scheme == "http":
                        self._setup_http_interface(service)

    def _setup_mqtt_interface(self, service: dict):
        """ Set up MQTT interface for the service """

        # Create MQTT client if it's not already set up
        self.mqtt = mqtt.Client(self.system["systemName"])
        if self._secure:
            self.mqtt.tls_set(self.ca, self.cert, self.key)

        # Reconnect and update host and port if changes found
        self.mqtt.connect(service["provider"]["address"], service["provider"]["port"])

    def _setup_http_interface(self, service: dict):
        """ Set up HTTP interface for the service """

        # Create HTTP session if it's not already set up
        self.http = requests.Session()
        if self._secure:
            self.http.cert = (self.cert, self.key)
            self.http.verify = self.ca

        # Construct URL to service
        scheme = "http"
        if self._secure:
            scheme += "s"
        authority = f"//{service['provider']['address']}:{service['provider']['port']}"
        path = service.get("serviceUri", "")
        if path != "":
            path = f"/{path}"

        # Set URL as service_url
        self.http_service_url = f"{scheme}:{authority}{path}"