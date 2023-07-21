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

    response = event_service.Subscribe(
        Context=conn.context(),
        Subscription={
            'Topic': "CARD",
            'EventTo': f'cetp://{ip}:12201'
        }
    )
    print(response)

    response = event_service.GetSubscription(
        Context=conn.context(),
    )

    print(response)

    async def stop():
        await asyncio.sleep(10)
        print('Stopping server')
        await cetp.stop_server()

    stopper = asyncio.create_task(stop())

    await asyncio.gather(server, stopper, return_exceptions=True)
