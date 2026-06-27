import json
from aiokafka import AIOKafkaProducer
from app.core.config import settings

# Глобальная переменная будет хранить инициализированный продюсер
producer: AIOKafkaProducer | None = None

async def start_producer():
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
    await producer.start()

async def stop_producer():
    global producer
    if producer:
        await producer.stop()

async def publish_event(topic: str, event: dict):
    """Отправляет событие в указанный топик Kafka."""
    if producer is None:
        raise RuntimeError("Producer has not been started")
    await producer.send_and_wait(topic, event)