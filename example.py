# pip install git+https://github.com/VTT-OM/arrowhead-client.git#egg=ah-client
from ah_client import AHClient

# Filepath to Arrowhead system JSON config
arrowhead_system_filepath = "./config/arrowhead_system.json"

if __name__ == "__main__":

    # Initiate Arrowhead client with the config json file
    client = AHClient(arrowhead_system_filepath)

    # Orchestrate with Arrowhead for configured service.
    # Returns a requests.session object with preset certificates,
    # and service_url for accessing the service.
    session, service_url = client.orchestrate(service_definition="service")
    print("Service available at URL:", service_url)

    # For example, consume service with HTTP GET method.
    response = session.get(service_url)
    print(response.content)

    # Register service to Arrowhead
    # NOTE: Any systems wanting to consume newly registered services must be
    # first authenticated by the Arrowhead Cloud administrator.
    # service_uri_path is used to access the service at the host address
    # of this system.
    client.register_service(
        service_definition="some_service", service_uri_path="service/some"
    )

    # Unregister a registered service
    client.unregister_service(service_definition="some_service")
