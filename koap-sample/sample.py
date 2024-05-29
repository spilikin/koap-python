from koap.config import ConnectorConfig
from koap.client import ConnectorClient
from icecream import ic

# Create a configuration object, the parameters are read from the environment variables
# see README.md for more details
config = ConnectorConfig()

# print config to see the configuration
ic(config)

# Create a client object
client = ConnectorClient(config)
# print the service directory to see the available services at the konnektor
ic(client.service_directory)

# create EventService client for a specific version
event_service = client.create_service_client("EventService", "7.2.0")

# get available cards
cards = event_service.GetCards(client.context())

# print the cards
ic(cards)
