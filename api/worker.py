from aiokafka import AIOKafkaConsumer
import asyncio
from api.preprocess import preprocess, Status
from sys import argv
from uuid import uuid4


async def listen(task_id: str, q: asyncio.Queue) -> None:
    """Listen kafka

    :param task_id: task_id
    :type task_id: str
    :param q: queue for consumer
    :type q: asyncio.Queue
    """
    consumer = AIOKafkaConsumer(
        'data', 'finished',
        loop=asyncio.get_event_loop(),
        bootstrap_servers='10.199.13.36:9091, 10.199.13.37:9092, 10.199.13.38:9093',
        value_deserializer=lambda m: json.loads(m.decode('utf8')))
    await consumer.start()
    async for msg in consumer:
        if msg.topic == 'data' and msg.value.get('task_id') == task_id and msg.value.get('data'):
            item = preprocess(item.get('data'), {})
            q.put(item['data'])
        elif msg.topic == 'finished' and msg.value.get('task_id') == task_id:
            break
    await consumer.stop()


async def main():
    q = asyncio.Queue()
