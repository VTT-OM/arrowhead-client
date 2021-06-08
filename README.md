# arrowhead-client <!-- omit in toc -->
Simple client for Arrowhead orchestration and service registration.


## Table of Contents <!-- omit in toc -->
- [Installation](#installation)
  - [Python package](#python-package)
  - [Development](#development)
- [Client](#client)
  - [Configuration](#configuration)
  - [Usage](#usage)


## Installation

Requires `Python >= 3.8`

### Python package

    pip install git+https://github.com/VTT-OM/arrowhead-client.git#egg=ah-client

### Development
Clone the repository to your device:

    git clone https://github.com/VTT-OM/arrowhead-client.git

From root folder install dependencies with:

    pip install -e .[dev]


## Client
Client is used to orchestrate with Arrowhead and register/unregister services.

### Configuration
Create and edit a `./config/arrowhead_system.json` file containing the required Arrowhead server URLs, system info and certificates:

    {
        "arrowheadSettings": {
            "orchestratorUrl": "https://<arrowhead-domain>:8441/orchestrator/",
            "serviceregistryUrl": "https://<arrowhead-domain>:8443/serviceregistry/"
        },
        "certificates": {
            "certificate": "./certs/system.crt",
            "key": "./certs/system.key",
            "certificate_authority": "./certs/system.ca"
        },
        "system": {
            "systemName": "system",
            "address": "localhost",
            "port": 1234
        }
    }

Some important notes for the configuration:
- `systemName` field and the certificate `common_name` (usually same as filename) must be equal.
- `systemName`, `address` and `port` combination must be unique within the Arrowhead cloud.
- `certificate_authority` file is strongly recommended but not required. The client will default to not verifying servers if `certificate_authority` file is not found.

### Usage
**Create** a client:

    from ah_client import AHClient
    client = AHClient("./config/arrowhead_system.json")

**Orchestrate** for desired service registered on Arrowhead:

    session, service_url = client.orchestrate(service_definition="some_service")

Orchestration returns a [requests `session`](https://docs.python-requests.org/en/master/user/advanced/#session-objects) with preset certificates and `service_url` for accessing the orchestrated service.

An example for consuming the service with the `session` and `service_url`:

    response = session.get(service_url)

**Register a service** with a `service_definition` and `service_uri_path`.

    client.register_service(
        service_definition="some_other_service",
        service_uri_path="service/path"
    )

- `service_uri_path` is the path from where the service is accessible on this systems host `address` and `port` (as set in `arrowhead_system.json`)

**Unregister a service**:

    client.unregister_service(service_definition="some_other_service")
