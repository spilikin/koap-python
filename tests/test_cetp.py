from koap.client import ConnectorClient, ConnectorServiceName, ConnectorConfig
from rich.console import Console
from koap.cetp import CETP
import asyncio
import socket

c = Console()
print = c.print


def test_subscribe():
    asyncio.run(async_test_subscribe())


async def async_test_subscribe():
    config = ConnectorConfig()
    conn = ConnectorClient(config)

    cetp = CETP(config, lambda event: print(event))
    server = await cetp.start_server()

    event_service = conn.create_service_client(ConnectorServiceName.EventService, '7.2.0')

    # determine local ip address
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)

    event_endpoint = f'cetp://{ip}:12201'

    subscriptions_response = event_service.GetSubscription(
        Context=conn.context(),
    )

    subscriptions = subscriptions_response['Subscriptions']['Subscription']

    # see if this host already has a subscription
    existing_subscription = next(filter(lambda s: s['EventTo'] == event_endpoint, subscriptions), None)

    if existing_subscription is None:
        response = event_service.Subscribe(
            Context=conn.context(),
            Subscription={
                'Topic': "CARD",
                'EventTo': f'cetp://{ip}:12201'
            }
        )
        print(response)
    else:
        print("Subscription already exists")
        print(existing_subscription)

    async def stop():
        await asyncio.sleep(10)
        print('Stopping server')
        await cetp.stop_server()

    stopper = asyncio.create_task(stop())

    await asyncio.gather(server, stopper, return_exceptions=True)
