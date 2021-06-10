import json
import logging
import time

import requests

console_logger = logging.StreamHandler()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)-2s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[console_logger],
)


class AHClient:
    def __init__(self, ah_system_json: str):

        try:
            with open(ah_system_json) as config_file:
                config = json.load(config_file)

            self.system = {
                "systemName": config["system"]["systemName"],
                "address": config["system"]["address"],
                "port": config["system"]["port"],
            }

            self.orchestrator_url = config["arrowheadSettings"]["orchestratorUrl"]
            self.serviceregistry_url = config["arrowheadSettings"]["serviceregistryUrl"]

            # Set certificates
            self.cert = config["certificates"]["certificate"]
            self.key = config["certificates"]["key"]
            self.verify = config["certificates"].get("certificate_authority", False)
        except FileNotFoundError as file_error:
            logging.error(f"Ensure that file '{ah_system_json}' exists")
            raise
        except KeyError as key_error:
            logging.error(
                f"Key {str(key_error)} not found in config file: {ah_system_json}"
            )
            raise

        # Ensure necessary Arrowhead core services are available
        self.echo_until_available(self.serviceregistry_url)
        self.echo_until_available(self.orchestrator_url)

        self.register_system()

    def echo_until_available(self, core_system_url: str, retry_timer: int = 10) -> None:
        """Echo Arrowhead core service until it is available

        Arguments:
            core_system_url: str
                Arrowhead core system url to echo.
            retry_timer: int = 10
                Time between echo attempts in seconds.
        """

        with requests.Session() as ses:
            # Set certificates
            ses.cert = (self.cert, self.key)
            ses.verify = self.verify

            # Echo Arrowhead system
            system_available = False
            while not system_available:
                try:
                    response = ses.get(f"{core_system_url}echo/")
                    logging.info(response.text)
                    if response.status_code == 200:
                        system_available = True
                except requests.exceptions.ConnectionError:
                    logging.info(
                        f"Arrowhead not available at address: {core_system_url}"
                    )
                    logging.info(f"Retrying in {retry_timer}...")
                    time.sleep(retry_timer)

        logging.info(f"Arrowhead available at: {core_system_url}")

    def register_system(self) -> None:
        """ Register system to Arrowhead """

        logging.info("Registering system to Arrowhead")

        with requests.Session() as session:
            # Set certificates
            if None not in (self.cert, self.key):
                session.cert = (self.cert, self.key)
                session.verify = self.verify

            # Register system to Arrowhead
            response = session.post(
                f"{self.serviceregistry_url}register-system/",
                json=self.system,
            )
            if response.status_code == 201:
                logging.info("System registered successfully")
            elif response.status_code == 400:
                logging.info("System has already been registered")
            else:
                logging.info(f"System registration response: {response.text}")
                response.raise_for_status()

    def orchestrate(
        self, service_definition: str, interface: str = "HTTP-SECURE-JSON"
    ) -> (requests.Session, str):
        """
        Orchestrate for service with Arrowhead

        Arguments:
            service_definition: str
                Service definition of the desired service

        Outputs:
            session: requests.Session
                Python requests session object with required certificates
                set for service consumption
            service_url: str
                Base URL for accessing the orchestrated service
        """

        logging.info("Orchestrating for service with Arrowhead")

        session = requests.Session()
        session.headers.update({"Connection": "close"})

        # Set certificates
        if None not in (self.cert, self.key):
            session.cert = (self.cert, self.key)
            session.verify = self.verify

        # Orhcestrate with Arrowhead
        orchestration_request = {
            "requesterSystem": self.system,
            "requestedService": {
                "serviceDefinitionRequirement": service_definition,
                "interfaceRequirements": [interface],
            },
            "orchestrationFlags": {"overrideStore": True},
        }
        response = session.post(
            f"{self.orchestrator_url}orchestration/",
            json=orchestration_request,
        )
        logging.info(f"Arrowhead orchestration response: {response.text}")
        if response.status_code != 200:
            response.raise_for_status()

        # Fail if no services received
        services = response.json().get("response", [])
        if len(services) < 1:
            raise ValueError(
                "No Arrowhead service available for this system with definition: "
                f"{service_definition}"
            )

        # Select first (and only) service
        service = services[0]

        # Construct service url
        port = ""
        if service["provider"]["port"] not in (80, 443):
            port = f":{service['provider']['port']}"
        service_url = f"https://{service['provider']['address']}{port}"
        # Append service path to service url
        service_url = f"{service_url}/{service['serviceUri']}"

        return session, service_url

    def register_service(
        self,
        service_definition: str,
        service_uri_path: str,
        interface: str = "HTTP-SECURE-JSON",
    ) -> None:
        """
        Register service with Arrowhead
        Before the service can be consumed by systems, the systems must be
        authorized for the service by the Arrowhead Cloud administrator

        Arguments:
            service_definition: str
                Service definition for the service to be registered
            service_uri_path: str
                Service uri path for accessing the service. Domain and port is
                resolved from the Arrowhead system address and port
        """

        logging.info("Registering service to Arrowhead")

        with requests.Session() as session:

            # Set certificates
            if None not in (self.cert, self.key):
                session.cert = (self.cert, self.key)
                session.verify = self.verify

            # Register service definition and uri as Arrowhead service
            service = {
                "providerSystem": self.system,
                "interfaces": [interface],
            }
            service["serviceDefinition"] = service_definition
            service["serviceUri"] = service_uri_path
            response = session.post(
                f"{self.serviceregistry_url}/register",
                json=service,
            )
            logging.info(response.text)

    def unregister_service(self, service_definition: str) -> None:
        """ Unregister service from Arrowhead """

        logging.info("Unregistering service from Arrowhead")

        with requests.Session() as session:

            # Set certificates
            if None not in (self.cert, self.key):
                session.cert = (self.cert, self.key)
                session.verify = self.verify

            params = {
                "system_name": self.system["systemName"],
                "address": self.system["address"],
                "port": self.system["port"],
                "service_definition": service_definition,
            }
            response = session.delete(
                f"{self.service_registry_url}/unregister", params=params
            )
            logging.info(response.text)
