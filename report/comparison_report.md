# Module 2 protocol comparison report

AMQP was skipped for this submission as instructed, so this report focuses on MQTT and CoAP. I still mention where AMQP would normally fit, but I did not implement or measure it.

## 5.1 QoS comparison results table

I ran the MQTT QoS harness against the Mosquitto broker in Docker using:

```bash
uv run pytest tests/mqtt/test_qos_loss.py -v -s
```

I also measured CoAP GET requests locally against the implemented CoAP server. The test environment was local, so there was no real packet loss in this run. The MQTT harness label says "~10% loss", but in this starter kit the in-process loss simulation did not drop any messages during my run.

| Protocol / QoS | Sent | Received | Lost (%) | Duplicates | Avg Latency (ms) |
|---|---:|---:|---:|---:|---:|
| MQTT QoS 0 | 100 | 100 | 0.0 | 0 | 1.1 |
| MQTT QoS 1 | 100 | 100 | 0.0 | 0 | 1.0 |
| MQTT QoS 2 | 100 | 100 | 0.0 | 0 | 1.7 |
| CoAP NON | 100 | 100 | 0.0 | 0 | 1.2 |
| CoAP CON | 100 | 100 | 0.0 | 0 | 1.1 |

QoS 0 can lose messages because it has no acknowledgement step. The publisher sends a PUBLISH packet and moves on. If the packet is dropped, the broker and subscriber have no protocol-level way to ask for it again. QoS 1 and QoS 2 add acknowledgement flows, so the sender can retry when the exchange does not complete.

QoS 1 can produce duplicates when the receiver gets the original PUBLISH but the PUBACK is lost. The sender then retransmits the same packet identifier with the DUP flag set. For telemetry, this is usually acceptable if each reading has a sequence number or timestamp. My publisher includes both `seq` and `timestamp`, so the backend can detect repeated readings.

QoS 2 had the highest MQTT latency in my run, 1.7 ms compared with 1.0 ms for QoS 1. That is expected because QoS 2 uses PUBLISH, PUBREC, PUBREL, and PUBCOMP instead of a single PUBACK. I would not use QoS 2 for every high-frequency sensor sample. I would reserve it for events where duplicate processing is more harmful than the extra round trip.

## 5.2 CoAP-HTTP proxy mapping

The starter kit I received did not include `tests/coap/test_proxy.py`, so I mapped the HTTP headers from the CoAP options present in the captured CoAP response. In the capture, the CoAP response includes Content-Format 50 and does not include ETag or Location options.

| HTTP Header | CoAP Option | Observed Value |
|---|---|---|
| Content-Type | Content-Format | `application/json`, from CoAP Content-Format 50 |
| Cache-Control: max-age | Max-Age | Default CoAP freshness applies when Max-Age is absent; a proxy may expose this as `max-age=60` |
| ETag | ETag | Not present |
| Location | Location-Path / Location-Query | Not present |

## 5.3 Protocol selection recommendation

| Data Path | Recommended Protocol | Justification |
|---|---|---|
| Sensor to cloud, high frequency and under 100 ms latency | MQTT QoS 0 or QoS 1 | MQTT matched the telemetry pattern best. QoS 0 is enough for lossy high-rate readings like vibration, while QoS 1 is safer for temperature because the alert threshold matters. |
| Actuator commands, safety critical | CoAP CON with command IDs | CoAP PUT gives direct request-response control for resources such as `/actuator/line1/fan`. I would add an application command ID because true exactly-once actuator behavior cannot rely only on transport QoS. |
| Backend service-to-service routing | MQTT for this submission; AMQP in a full backend | Since AMQP was skipped, MQTT topic routing is the implemented choice. In a production backend I would normally use AMQP/RabbitMQ for durable queues and dead letters. |
| OTA firmware delivery to constrained MCU | CoAP Block2 | CoAP is built for constrained devices, and aiocoap handled the large manifest response without manual chunking in my code. |

For sensor-to-cloud telemetry, I would use MQTT. The topic structure in my implementation, `factory/{line}/{sensor}`, maps cleanly to the factory layout. The subscriber can listen to all telemetry with `factory/#`, or only temperatures with `factory/+/temperature`. That gives the backend a simple way to route data without parsing every payload first. The measured local latency was also low. MQTT QoS 0 averaged 1.1 ms, QoS 1 averaged 1.0 ms, and QoS 2 averaged 1.7 ms. The difference is small on localhost, but the packet capture shows why QoS 2 costs more: it needs a longer acknowledgement sequence.

For high-frequency readings, I would not use the same reliability level for every sensor. Vibration data changes quickly and a single missing sample is usually not important, so QoS 0 is fine. Temperature is different because readings above 85 C trigger a critical alert. I used QoS 1 for temperature because it gives at-least-once delivery without the full QoS 2 handshake. Power readings were sent at QoS 2 for the assignment, but in a real deployment I would only keep that if the power data affected billing, compliance, or another process where duplicates and missing values are both costly.

For actuator commands, I would use CoAP confirmable requests. The fan actuator is naturally a resource: `PUT /actuator/line1/fan` with `{"state": "ON"}` or `{"state": "OFF"}`. My server returns `2.04 Changed` for valid commands and `4.00 Bad Request` for invalid states. That explicit response is useful for control paths. I would still include a command ID and make commands idempotent, because neither MQTT nor CoAP can guarantee that the physical world changed exactly once. If the fan is already ON, receiving the same ON command twice should not cause a new side effect.

For backend service-to-service routing, MQTT is acceptable for this reduced assignment because the topic tree already separates line and sensor type. In a full version of SmartFactory, I would probably choose AMQP for this layer. AMQP exchanges, durable queues, publisher confirms, and dead-letter queues are designed for backend workflows. Since AMQP was intentionally skipped here, I would keep the backend simple and use MQTT subscriptions until the routing requirements become more complex.

For OTA firmware delivery, I would choose CoAP Block2. The manifest resource in my implementation returns a JSON document larger than 3 KB. The application code returns one payload, and aiocoap handles block-wise transfer below that. That is a better fit for constrained MCUs than forcing a heavier HTTP stack. The MCU can fetch `/factory/manifest`, compare versions, and then request only the firmware it needs.

## 5.4 Reflection

The biggest technical challenge was not the sensor simulation itself. It was getting CoAP to run reliably in the test environment. The starter code used the default server context binding, but aiocoap on my machine refused the any-address bind. I fixed that by binding the server explicitly to `localhost` on port 5683. I also used `uv` with Python 3.11 and pinned pytest-asyncio to the version range the starter kit expected. With newer Python and newer pytest-asyncio, the CoAP tests ran into event loop issues that were not caused by my resource logic.

The packet capture task made the MQTT QoS difference much clearer. In Python, publishing a message is one method call. On the wire, QoS 0, QoS 1, and QoS 2 are not the same at all. QoS 1 added a PUBACK with the same packet identifier as the PUBLISH packet. QoS 2 added more protocol traffic. Seeing the packet identifiers match in the capture helped me understand why QoS 1 is usually enough for telemetry that can tolerate duplicates.

CoAP surprised me in a different way. The packets are compact, but a lot is packed into the option encoding. In the GET request, the URI path is split into several Uri-Path options and each option uses delta encoding. The Observe registration was only one option with value 0, and later notifications reused the same token with increasing Observe sequence values. That is efficient, but it is less obvious than MQTT topics when reading the packet for the first time.

The most complex protocol to implement correctly was CoAP. MQTT had more broker setup, but the programming model was direct: connect, publish to topics, subscribe with wildcards, and handle messages. CoAP required resource classes, asyncio update loops, observable resources, response codes, content formats, Block2 behavior, and sequence-number handling for stale notifications. Once it worked, it felt like the better fit for constrained devices, but it took more care to get right.
