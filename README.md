# Open Hardware & Low-Cost IoT for Heritage Monitoring
### CAA2026 Workshop Materials

This repository contains the materials, demos, and example code for the workshop
**"Open Hardware and Low-cost Electronics and IoT for sensing and monitoring heritage assets"**,
presented at the Computer Applications and Quantitative Methods in Archaeology (CAA) 2026 conference.

The workshop is a practical introduction to building simple sensing systems using
low-cost hardware, aimed at people working in archaeology, heritage, and environmental monitoring.

---

## What is in this repo

- Presentation slides (`caa2026_workshop_2025_slides.pdf`)
- Setup instructions and prerequisites (`caa2026-workshop-open-hardware-getting_ready.pdf`)
- A series of progressive demos, from basic electronics to wireless sensor networks
- Utility scripts for testing and debugging boards
- Additional demos covering OLED displays, BLE GATT services, WiFi servers, and camera streaming

All examples use MicroPython on ESP32-C3 SuperMini boards, except where noted.

---

## Repository structure

```
.
├── demo_01_blinking_led/             # Blinking an LED (basic GPIO)
│   ├── demo1_blinking_led.py
│   └── demo_1_blinking_led.fzz          # Fritzing wiring diagram
│
├── demo_02_reading_LDR/              # Reading a light sensor (analog input)
│   ├── demo_02_reading_LDR_console.py
│   ├── demo_02_reading_LDR_flash.py
│   └── demo_02_reading_LDR.fzz
│
├── demo_03_HCSR04_ultrasonic_distance_sensor/  # Ultrasonic distance measurement
│   ├── demo_03_HCSR04.py
│   └── demo_03_HCSR04.fzz
│
├── demo_04_BMP280_temp_pressure/     # Temperature and pressure sensor (I2C)
│   ├── demo_04_BMP280.py
│   ├── demo_04_I2C_scanner.py
│   ├── bmp280.py                         # BMP280 driver library
│   ├── demo_04_BMP280.fzz
│   └── bst-bmp280-ds001.pdf              # BMP280 datasheet
│
├── demo_05_espnow_messaging/         # Peer-to-peer messaging with ESP-NOW
│   ├── demo_05_espnow_messaging_sender.py
│   └── demo_05_espnow_messaging_receiver.py
│
├── demo_06_ble_advertiser/           # BLE advertising and scanning
│   ├── demo_06_BLE_advertiser.py
│   └── demo_06_BLE_advertiser_scanner.py
│
├── demo_07_BLE_advertiser_multi/     # BLE sensor network with multiple nodes
│   ├── demo_07_BLE_advertiser_multi_dht.py
│   ├── demo_07_BLE_advertiser_multi_bmp.py
│   ├── demo_07_BLE_advertiser_multi_filtered_scanner.py
│   ├── demo_07_BLE_advertiser_multi_decoder_scanner.py
│   ├── demo_07_BLE_advertiser_multi_universal_scanner.py
│   └── bmp280.py                         # BMP280 driver library (copy)
│
├── other_demos/                      # Extra demos beyond the workshop session
│   ├── 0.91_OLED/                        # 0.91" OLED display over I2C
│   │   ├── 0_91_oled.py
│   │   ├── I2C_scanner.py
│   │   └── ssd1306.py                    # SSD1306 OLED driver
│   ├── BLE_beacon_DHT22/                 # BLE beacon broadcasting DHT22 data
│   │   ├── BLE_beacon_DHT22_advertiser.py
│   │   └── BLE_beacon_DHT22_scanner.py
│   ├── BLE_GATT_DHT22/                  # BLE GATT service for DHT22 data
│   │   ├── BLE_GATT_DHT22_sender.py
│   │   └── BLE_GATT_DHT22_reader.py
│   ├── BLE_Notify_DHT22/                # BLE notify service for DHT22 data
│   │   └── BLE_Notify_DHT22_sender.py
│   ├── WiFi_DHT22_AP_Server/            # WiFi access point with web server
│   │   └── AP_webserver.py
│   ├── WiFi_Scanner/                    # WiFi network scanner
│   │   └── Wifi_antenna_tester.py
│   ├── dht22/                           # Basic DHT22 temperature/humidity reading
│   │   ├── dht22.py
│   │   └── dht22.fzz
│   ├── espnow_oled_dt22/               # ESP-NOW + DHT22 + OLED display
│   │   ├── udp_sender_dht22.py
│   │   └── udp_receiver_oled_ap.py
│   └── Cam/AP_server/                   # ESP32-CAM live streaming (Arduino)
│       └── AP_server.ino
│
├── utils/                            # Utility scripts for board testing
│   ├── GPIO_tester.py
│   ├── I2C_scanner.py
│   ├── Wifi_antenna_tester.py
│   ├── mac_scanner.py
│   └── wifi_connection_testing.py
│
├── caa2026_workshop_2025_slides.pdf      # Workshop slides
└── caa2026-workshop-open-hardware-getting_ready.pdf  # Setup guide
```

---

## Demos overview

| Demo | Topic | Hardware |
|---|---|---|
| 01 | Blinking an LED | ESP32-C3, LED, resistor |
| 02 | Reading a light sensor | ESP32-C3, LDR, resistor |
| 03 | Ultrasonic distance | ESP32-C3, HC-SR04 |
| 04 | Temperature and pressure | ESP32-C3, BMP280 (I2C) |
| 05 | ESP-NOW messaging | Two ESP32-C3 boards |
| 06 | BLE advertising | Two ESP32-C3 boards |
| 07 | BLE sensor network | Multiple ESP32-C3 boards, DHT22, BMP280 |

---

## Getting started

See `caa2026-workshop-open-hardware-getting_ready.pdf` for instructions on how to set up your
board, install MicroPython, and configure Thonny IDE.

---

## .fzz files

Some demos include `.fzz` files. These are Fritzing wiring diagrams showing how to
connect the components. You can open them with [Fritzing](https://fritzing.org/).
