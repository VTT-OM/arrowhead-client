# arrowhead-client <!-- omit in toc -->
Simple clients for Arrowhead orchestration, service registration and management.

### Coming soon. <!-- omit in toc -->


## Table of Contents <!-- omit in toc -->
- [Installation](#installation)
  - [Python package](#python-package)
  - [Development](#development)
- [Consumer](#consumer)
  - [Configuration](#configuration)
  - [Usage](#usage)
- [Provider](#provider)
  - [Configuration](#configuration-1)
  - [Usage](#usage-1)
- [Manager](#manager)


## Installation

Requires `Python > 3.8`

### Python package

    pip install git+https://github.com/VTT-OM/arrowhead-client.git

### Development
Clone the repository to your device:

    git clone https://github.com/VTT-OM/arrowhead-client.git

From root folder install dependencies with:

    pip install -e .[dev]


## Consumer
Consumer is used to orchestrate with Arrowhead and consume the provided services.

### Configuration
Create a `your_consumer.json` file containing the require consumer info etc. like so:

    {
        "arrowheadOrchestratorUrl": "https://domain:port/orchestrator",
        "requesterSystem": {
            "systemName": "your_consumer",
            "address": "localhost",
            "port": 2345
        },
        "certificates": {
            "certificate": "./path/to/your_consumer.crt",
            "key": "./path/to/your_consumer.key",
            "certificate_authority": "./path/to/your_consumer.ca"
        }
    }

If no certificates are given, the consumer will default to unsecured HTTP and MQTT interfaces when communicating with Arrowhead core systems and service providers.

### Usage
Create a consumer:

    from client import Consumer
    consumer = Consumer("./path/to/your_consumer.json")

Orchestrate for desired service registered on Arrowhead:

    consumer.orchestrate("your_service")

Depending on what interface the service uses, you may now use either HTTP(S) or MQTT(S):

HTTP(S):

    response = consumer.http.get(consumer.http_service_url)
                                or
                            .post(consumer.http_service_url, data=data)

MQTT(S):

    consumer.mqtt.publish("mqtt/topic", payload=data)
                    or
                 .on_message = on_message  # Callback function for subcriptions
                 .subscribe("mqtt/topic")   

`consumer.http` is a Python requests session object with given certificates already set for TLS.  
More on [Python requests and session here](https://requests.readthedocs.io).

`consumer.mqtt` is a Python Paho mqtt client object with given certificates already set for TLS and connection to broker established.  
More on [Python Paho MQTT client here](https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php).


## Provider

Provider is used to register your services with Arrowhead.

### Configuration

Create a `your_provider.json` file containing the require provider info and services like so:

    {
        "serviceRegistryUrl": "https://domain:port/serviceregistry",
        "providerSystem": {
            "systemName": "your_provider",
            "address": "localhost",
            "port": 2345
        },
        "services": [
            {
                "serviceDefinition": "service_1",
                "serviceUri": "service/1",
                "interfaces": [
                    "HTTPS-SECURE-JSON"
                ]
            }
        ],
        "certificates": {
            "certificate": "./certs/your_provider.crt",
            "key": "./certs/your_provider.key",
            "certificate_authority": "./certs/your_provider.ca"
        }
    }

If not certificates are given, the consumer will default to unsecured HTTP and MQTT interfaces with Arrowhead and service consumers.

### Usage

Create a provider:

    from client import Provider
    provider = Provider("./path/to/your_provider.json")

Register configured services with Arrowhead:

    provider.register_services()

Your configured services should now be available on Arrowhead.  
However, any consumer systems still need to be auhtorized to your services before consumption.

Unregister configured services with Arrowhead:

    provider.unregister_services()


## Manager

### Coming soon. <!-- omit in toc -->