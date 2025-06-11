# from kafka import KafkaProducer
# import json
# import time

# def send_message(message):
#     bootstrap_servers = 'broker:29092'
#     topic = 'Tracking'
#     producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
#                              value_serializer=lambda v: json.dumps(v).encode('utf-8'))
#     producer.send(topic, value=message)
#     print(f"Produced: {message} to Kafka topic: {topic}")



from kafka import KafkaProducer
import json

class KafkaProducerClient:
    def __init__(self, bootstrap_servers='broker:29092', topic='Tracking'):
        self.topic = topic
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def send_message(self, message: dict):
        try:
            self.producer.send(self.topic, value=message)
            self.producer.flush()  
            print(f"Produced: {message} to Kafka topic: {self.topic}")
        except Exception as e:
            print(f"Failed to send message: {e}")
        
