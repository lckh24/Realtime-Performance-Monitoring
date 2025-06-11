from sqlalchemy import create_engine, Column, Integer, Numeric, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from kafka import KafkaConsumer
import json

Base = declarative_base()

# Define bảng trong schema bronze với id auto-increment
class BronzePerformance(Base):
    __tablename__ = 'bronze_performance'
    __table_args__ = {'schema': 'bronze'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(TIMESTAMP)
    cpu_usage = Column(Numeric(5, 2))
    memory_usage = Column(Numeric(5, 2))
    cpu_interrupts = Column(Numeric(18, 0))
    cpu_calls = Column(Numeric(18, 0))
    memory_used = Column(Numeric(18, 0))
    memory_free = Column(Numeric(18, 0))
    bytes_sent = Column(Numeric(18, 0))
    bytes_received = Column(Numeric(18, 0))
    disk_usage = Column(Numeric(5, 2))

# Define bảng trong schema silver với id auto-increment
class SilverPerformance(Base):
    __tablename__ = 'silver_performance'
    __table_args__ = {'schema': 'silver'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(TIMESTAMP)
    cpu_usage = Column(Numeric(5, 2))
    memory_usage = Column(Numeric(5, 2))
    cpu_interrupts = Column(Numeric(18, 0))
    cpu_calls = Column(Numeric(18, 0))
    memory_used = Column(Numeric(18, 0))
    memory_free = Column(Numeric(18, 0))
    bytes_sent = Column(Numeric(18, 0))
    bytes_received = Column(Numeric(18, 0))
    disk_usage = Column(Numeric(5, 2))


# Kết nối PostgreSQL
engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5433/cpu-tracking")
Session = sessionmaker(bind=engine)
session = Session()

# Tạo schema nếu chưa có
with engine.connect() as conn:
    conn.execute("CREATE SCHEMA IF NOT EXISTS bronze;")
    conn.execute("CREATE SCHEMA IF NOT EXISTS silver;")

# Tạo bảng nếu chưa tồn tại
Base.metadata.create_all(engine)

# Hàm transform từ bronze row sang silver
def transform_row_to_silver(bronze_row):
    try:
        
        if any(getattr(bronze_row, col.name) is None for col in bronze_row.__table__.columns):
            print("Skip record due to None values")
            return
        if bronze_row.memory_used > 16:
            print(f"Skip record with memory_used_gb = {bronze_row.memory_used:.2f} GB > 16 GB of My Laptop")
            return  
        elif bronze_row.cpu_usage > 101:
            print(f"Skip record with cpu_usage > 100")
            return
        elif bronze_row.memory_usage > 101:
            print(f"Skip record with cpu_usage > 100")
            return
        elif bronze_row.disk_usage > 101:
            print(f"Skip record with disk_usage > 100")
            return
        
        cpu_usage_percent = round(bronze_row.cpu_usage / 100, 2)
        memory_usage_percent = round(bronze_row.memory_usage / 100, 2)
        memory_free = bronze_row.memory_free if bronze_row.memory_free < 16 else round(bronze_row.memory_free / 1024, 2)
        disk_usage = round(bronze_row.disk_usage / 100, 2)

        silver_record = SilverPerformance(
            time=bronze_row.time,
            cpu_usage=cpu_usage_percent,
            memory_usage=memory_usage_percent,
            cpu_interrupts=bronze_row.cpu_interrupts,
            cpu_calls=bronze_row.cpu_calls,
            
            memory_used=bronze_row.memory_used,
            memory_free=memory_free,
            bytes_sent=bronze_row.bytes_sent,
            bytes_received=bronze_row.bytes_received,
            disk_usage=disk_usage
        )

        session.add(silver_record)
        session.commit()

    except Exception as e:
        print(f"[Transform Error] {e}")
        session.rollback()


consumer = KafkaConsumer(
    'Tracking',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='latest',
)

print("Kafka consumer started…")

for msg in consumer:
    value = msg.value.decode('utf-8')
    data = json.loads(value)
    print("Received:", data)

    # Ghi raw data vào bronze
    bronze_record = BronzePerformance(
        time=datetime.now(),
        cpu_usage=data.get("cpu_usage_percent"),
        memory_usage=data.get("memory_percent"),
        cpu_interrupts=data.get("cpu_interrupts"),
        cpu_calls=data.get("cpu_syscalls"),
        memory_used=data.get("memory_used"),
        memory_free=data.get("memory_free"),
        bytes_sent=data.get("bytes_sent"),
        bytes_received=data.get("bytes_received"),
        disk_usage=data.get("disk_usage_percent"),
    )

    session.add(bronze_record)
    session.commit()

    transform_row_to_silver(bronze_record)


