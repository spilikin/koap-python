# KOAP: Modern Konnektor SOAP Library

## Configuration using environment variables

| Environment variable | Comment |
| --- | --- |
| `KONNEKTOR_BASE_URL` | Base URL for Konnektor. The `connector.sds` must be available at `{KONNEKTOR_BASE_URL}/connector.sds`|
| `KONNEKTOR_MANDANT_ID` | Context Mandant ID (Tenant)|
| `KONNEKTOR_CLIENT_SYSTEM_ID` | Context Client System ID|
| `KONNEKTOR_WORKPLACE_ID` | Context Workplace ID|
| `KONNEKTOR_USER_ID` | Context UserID (optional)|
| *Basic Auth* |
| `KONNEKTOR_AUTH_BASIC_USERNAME` | Username for Basic authentication| 
| `KONNEKTOR_AUTH_BASIC_PASSWORD`| Password for Basic authentication| 
| *Mutual TLS Auth* |
| Not implemented yet | 

```bash
export KONNEKTOR_BASE_URL=https://.../
export KONNEKTOR_MANDANT_ID=m1
export KONNEKTOR_CLIENT_SYSTEM_ID=c1
export KONNEKTOR_WORKPLACE_ID=w1
export KONNEKTOR_USER_ID=user1
export KONNEKTOR_AUTH_BASIC_USERNAME=user1
export KONNEKTOR_AUTH_BASIC_PASSWORD='use strong passwords in production'
```

Once the environmant variables are set, the `koap.config.ConnectorConfig`can be instantiated without parameters. We make use of [Pydantic Model Config](https://docs.pydantic.dev/latest/usage/model_config/).

```python
from koap.config import ConnectorConfig
from koap.client import ConnectorClient

config = ConnectorConfig()

client = ConnectorClient(config)

event_service = client.create_service_client('EventService', '7.2.0')

cards = event_service.GetCards(client.context())

print(cards)

```

## Configuration in code

```python
from koap.config import ConnectorConfig
from koap.client import ConnectorClient

config = ConnectorConfig(
    base_url='https://.../',
    mandant_id='m1',
    client_system_id='c1',
    workplace_id='w1',
    user_id='user1',
    # Basic Auth
    auth_basic_username='user1',
    auth_basic_password='use secure passwords in production',
)

client = ConnectorClient(config)

event_service = client.create_service_client('EventService', '7.2.0')

cards = event_service.GetCards(client.context())

print(cards)
```

## Development

```bash
git submodule init
git submodule update
poetry install
```

