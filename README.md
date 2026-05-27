# Module 2 Assignment - SmartFactory IoT Protocol Integration

**Real-Time Data Analytics for IoT** · Graduate Course · Module 2

---

## Quick Start

```bash
# 1. Create the Python environment with uv
uv venv --python 3.11
uv sync

# 2. Run the implemented MQTT and CoAP tests
uv run pytest tests/mqtt/test_publisher.py tests/coap/test_server.py -v --tb=short

# AMQP was skipped for this submission as instructed.
```

---

## Repository Structure

```
smartfactory-iot-protocol-integration/
├── src/
│   ├── mqtt/
│   │   ├── publisher.py      ← Task 1.1 completed
│   │   └── subscriber.py     ← Task 1.2 completed
│   ├── coap/
│   │   ├── server.py         ← Task 2.1 completed
│   │   └── observer.py       ← Task 2.2 completed
│   └── amqp/
│       ├── topology.py       ← AMQP skipped
│       ├── producer.py       ← AMQP skipped
│       └── consumer.py       ← AMQP skipped
│
├── tests/
│   ├── mqtt/
│   │   ├── test_publisher.py   ← Do not modify
│   │   └── test_qos_loss.py    ← Do not modify (run with -s for output table)
│   ├── coap/
│   │   └── test_server.py      ← Do not modify
│   └── amqp/
│       └── test_topology.py    ← Do not modify
│
├── report/
│   ├── packet_analysis.md    ← Task 4  Fill in the annotation tables
│   └── comparison_report.md  ← Task 5  Write your analysis here
│
├── captures/                 ← Task 4 packet captures
├── scripts/
│   └── capture.sh            ← Task 4  Run to capture traffic
├── config/
│   └── mosquitto.conf        ← Mosquitto broker configuration
├── docker-compose.yml        ← Infrastructure: Mosquitto + RabbitMQ + InfluxDB
├── requirements.txt
├── pytest.ini
└── setup.sh                  ← Run this first
```

---

## Running Individual Components

```bash
# Task 1 - MQTT
uv run python -m src.mqtt.publisher       # Terminal 1
uv run python -m src.mqtt.subscriber      # Terminal 2

# Task 2 - CoAP
uv run python -m src.coap.server          # Terminal 1
uv run python -m src.coap.observer        # Terminal 2

# Task 3 - AMQP skipped

# Task 4 - Packet capture (with publisher/server running)
bash scripts/capture.sh
```

---

## Running Tests

```bash
# All tests
uv run pytest tests/mqtt/test_publisher.py tests/coap/test_server.py -v

# Individual task tests
uv run pytest tests/mqtt/ -v
uv run pytest tests/coap/ -v

# QoS experiment with output table (Task 1.3)
uv run pytest tests/mqtt/test_qos_loss.py -v -s
```

---

## Infrastructure

| Service | Port | URL |
|---------|------|-----|
| Mosquitto MQTT | 1883 | mqtt://localhost:1883 |
| RabbitMQ AMQP | 5672 | amqp://localhost:5672 |
| RabbitMQ Management | 15672 | http://localhost:15672 (guest/guest) |
| CoAP server (Python) | 5683 | coap://localhost:5683 |
| InfluxDB (optional) | 8086 | http://localhost:8086 |

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f mosquitto
docker compose logs -f rabbitmq
```

---

*Graduate Course: Real-Time Data Analytics for IoT · Module 2*
