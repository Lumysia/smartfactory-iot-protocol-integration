# Packet Analysis

This analysis uses the captures in `captures/mqtt.pcap` and `captures/coap.pcap`. AMQP was skipped for this submission as instructed.

## 4.2 MQTT packet annotations

### CONNECT packet

Captured frame: MQTT frame 4 in `captures/mqtt.pcap`.

| Field | Offset | Raw Hex | Decoded Value |
|---|---:|---|---|
| Frame type + flags | 0 | `10` | Type = CONNECT (`0001`), flags = `0000` |
| Remaining length | 1 | `45` | 69 bytes |
| Protocol name length | 2-3 | `00 04` | 4 bytes |
| Protocol name | 4-7 | `4D 51 54 54` | `MQTT` |
| Protocol version | 8 | `04` | MQTT 3.1.1 |
| Connect flags | 9 | `2C` | `00101100` |
| Keep-alive | 10-11 | `00 3C` | 60 seconds |
| Client ID length | 12-13 | `00 1A` | 26 bytes |
| Client ID | 14-39 | `73 6D 61 72 74 66 61 63 74 6F 72 79 2D 70 75 62 6C 69 73 68 65 72 2D 30 30 31` | `smartfactory-publisher-001` |

Full MQTT CONNECT payload:

```text
10 45 00 04 4D 51 54 54 04 2C 00 3C 00 1A 73 6D
61 72 74 66 61 63 74 6F 72 79 2D 70 75 62 6C 69
73 68 65 72 2D 30 30 31 00 14 66 61 63 74 6F 72
79 2F 6C 69 6E 65 31 2F 73 74 61 74 75 73 00 07
6F 66 66 6C 69 6E 65
```

Connect flags byte breakdown for `0x2C`:

| Bit | Name | Value | Meaning |
|---:|---|---:|---|
| 7 | Username flag | 0 | No username |
| 6 | Password flag | 0 | No password |
| 5 | Will retain | 1 | Last Will message is retained |
| 4-3 | Will QoS | `01` | Last Will uses QoS 1 |
| 2 | Will flag | 1 | Last Will is present |
| 1 | Clean session | 0 | Persistent session |
| 0 | Reserved | 0 | Required zero |

### QoS 1 PUBLISH packet

Captured frame: MQTT frame 13. Topic: `factory/line1/temperature`.

| Field | Offset | Raw Hex | Decoded Value |
|---|---:|---|---|
| Fixed header byte 1 | 0 | `32` | Type = PUBLISH (`0011`), DUP = 0, QoS = `01`, RETAIN = 0 |
| Remaining length | 1-2 | `A0 01` | 160 bytes |
| Topic length | 3-4 | `00 19` | 25 bytes |
| Topic string | 5-29 | `66 61 63 74 6F 72 79 2F 6C 69 6E 65 31 2F 74 65 6D 70 65 72 61 74 75 72 65` | `factory/line1/temperature` |
| Packet Identifier | 30-31 | `00 03` | 3 |
| Payload | 32 onward | JSON bytes | `{"line": "line1", "sensor": "temperature", "value": 65.847, "unit": "C", "timestamp": "2026-05-27T14:44:45.307282+00:00", "seq": 1}` |

Fixed header byte `0x32` expands to `00110010`:

| Bits 7-4 | Bit 3 | Bits 2-1 | Bit 0 |
|---|---:|---:|---:|
| `0011` = PUBLISH | `0` = not duplicate | `01` = QoS 1 | `0` = not retained |

### PUBACK packet

Captured frame: MQTT frame 14.

| Field | Offset | Raw Hex | Decoded Value |
|---|---:|---|---|
| Fixed header | 0 | `40` | Type = PUBACK (`0100`) |
| Remaining length | 1 | `02` | 2 bytes |
| Packet Identifier | 2-3 | `00 03` | 3 |

Packet Identifier match: PUBLISH packet ID = 3; PUBACK packet ID = 3; Match = yes.

## 4.3 CoAP packet annotations

### CON GET request

Captured frame: CoAP frame 1 in `captures/coap.pcap`. URI: `coap://localhost/factory/line1/temperature`.

CoAP UDP payload:

```text
42 01 42 CB C9 47 39 6C 6F 63 61 6C 68 6F 73 74
30 57 66 61 63 74 6F 72 79 05 6C 69 6E 65 31 0B
74 65 6D 70 65 72 61 74 75 72 65
```

| Field | Bits / Bytes | Raw Value | Decoded Value |
|---|---|---|---|
| Version | bits 7-6 | `01` | Version 1 |
| Type | bits 5-4 | `00` | CON |
| TKL | bits 3-0 | `0010` | Token length = 2 |
| Code | byte 1 | `01` | 0.01 GET |
| Message ID | bytes 2-3 | `42 CB` | 17099 |
| Token | bytes 4-5 | `C9 47` | `0xC947` |
| Uri-Host option | option bytes | `39 6C 6F 63 61 6C 68 6F 73 74` | Delta 3, length 9, `localhost` |
| Observe option | option byte | `30` | Delta 3 from Uri-Host, option 6, length 0, register observe = 0 |
| Uri-Path option | option bytes | `57 66 61 63 74 6F 72 79` | Delta 5 to option 11, length 7, `factory` |
| Uri-Path option | option bytes | `05 6C 69 6E 65 31` | Delta 0, length 5, `line1` |
| Uri-Path option | option bytes | `0B 74 65 6D 70 65 72 61 74 75 72 65` | Delta 0, length 11, `temperature` |

Byte 0 expansion for `0x42` (`01000010`):

| Bit 7 | Bit 6 | Bit 5 | Bit 4 | Bit 3 | Bit 2 | Bit 1 | Bit 0 |
|---|---|---|---|---|---|---|---|
| 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0 |

### ACK 2.05 Content response

Captured frame: CoAP frame 2.

CoAP UDP payload starts with:

```text
62 45 42 CB C9 47 60 61 32 FF 7B 22 6C 69 6E 65 ...
```

| Field | Raw Hex | Decoded Value |
|---|---|---|
| Fixed header byte 0 | `62` | Version = 1, Type = ACK (`10`), TKL = 2 |
| Code byte 1 | `45` | 2.05 Content |
| Message ID | `42 CB` | 17099, matches request |
| Token | `C9 47` | Matches request token |
| Observe option | `60` | Option number 6, sequence value 0 |
| Content-Format option | `61 32` | Option number 12, value 50 (`application/json`) |
| Payload Marker | `FF` | Marks the start of the JSON payload |
| Payload | JSON bytes | `{"line": "line1", "sensor": "temperature", "value": 69.829, "unit": "C", "ts": "2026-05-27T14:46:10.483985+00:00"}` |

### Observe notification

Captured frame: CoAP frame 5.

CoAP UDP payload starts with:

```text
42 45 51 5E C9 47 61 01 61 32 FF 7B 22 6C 69 6E ...
```

| Field | Value |
|---|---|
| Observe option number | 6 |
| Observe sequence value | 1 |
| Message type | CON |
| Response code | 2.05 Content |
| Message ID | `0x515E` |
| Token | `0xC947`, same observation token as the original request |
| Content-Format | 50, `application/json` |

The notification payload contained an updated line1 temperature reading: `74.658 C`.

## 4.4 AMQP frame annotations

AMQP was skipped for this assignment run, so no AMQP packet analysis is included.
