# Mānava 🐋 - The Deep Sea Health Companion

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![Hardware](https://img.shields.io/badge/hardware-Raspberry%20Pi-C51A4A.svg)](https://www.raspberrypi.org/)
[![Machine Learning](https://img.shields.io/badge/ML-scikit--learn-orange.svg)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Mānava** (meaning *breath* and *heartbeat* in Tongan) is a physical AI health companion that bridges your biometric data with the physical world. By sensing your Oura Ring data (sleep, stress, and activity), Mānava acts as a humpback whale from the Tongan waters, delivering poetic, deep-sea-themed health advice through an ambient, screen-minimalist hardware interface. 

Instead of overwhelming the user with raw numbers and charts, Mānava transforms biometric metrics into a calming, emotional daily ritual, accompanied by zero-latency, audio-reactive NeoPixel light tides.

## 🌊 Core Architecture (Hybrid AI Engine)

Mānava operates on a highly optimized, asynchronous **Edge + Cloud Hybrid Architecture** to guarantee 0-latency physical interactions:

1. **Morning Contemplation & Baking (`manava_butler.py`)**: 
   Every morning at 9:00 AM, the "Butler" daemon silently executes heavy computational tasks:
   * **Cloud LLM Routing:** Uses the Duke LiteLLM API to generate poetic, humpback-whale-themed intros and stories.
   * **Edge ML Routing:** Injects the latest Oura data into a custom, locally-trained Scikit-Learn classification model (`manava_health_model.pkl`) to determine the user's current health state (0, 1, or 2) and generate highly specific, non-metaphorical health data reports.
   * **Audio Synthesis & Envelope Extraction:** Generates TTS audio files via Edge-TTS and utilizes a **zero-dependency native Python parser** (`wave` + `struct` + `ffmpeg`) to extract Audio Envelope RMS data. This circumvents the `pydub`/`audioop` deprecation issues in Python 3.13, saving the visual light data as lightweight `.json` arrays.

2. **Zero-Latency Tactile Interaction (`manava_interface.py`)**: 
   Throughout the day, the physical interface operates purely as an execution layer. When a button is pressed, it instantly pairs the pre-rendered audio with the pre-baked `.json` light envelope, producing perfectly synced, high-saturation audio-reactive NeoPixel breathing effects with absolutely 0 processing delay.

## 🔮 Future Roadmap: V2 Real-Time Voice Interaction

This repository currently hosts **V1 (The Tactile & Ambient Edition)**. In the upcoming **V2 (The Conversational Edition)** upgrade, Mānava will evolve into a fully screenless, voice-activated companion:
* **Capacitive Touch Awakening**: Replacing mechanical buttons with a seamless touch sensor hidden beneath a ceramic shell.
* **Microphone Integration**: Allowing users to speak directly to Mānava for real-time, open-ended health conversations.
* **Ambient Soundscapes**: Playing deep-sea sonar and water flow sounds to naturally bridge the LLM processing latency.

---

## 🧰 Hardware Bill of Materials (BOM)

| Component | Description |
| :--- | :--- |
| **Compute Core** | Raspberry Pi 3B / 4B (running Raspberry Pi OS Bookworm) |
| **Biometric Sensor** | Oura Ring (Gen 3) |
| **Display** | I2C LCD Display (PCF8574, 16x2) |
| **Input** | 2x Tactile Push Buttons |
| **Lighting** | WS2812B NeoPixel LED Strip (10 Pixels) |
| **Audio** | 3.5mm External Speaker or Bluetooth/USB Audio |

### Wiring Guide

| Peripheral | Component Pin | Raspberry Pi GPIO (Physical Pin) |
| :--- | :--- | :--- |
| **LCD Display** | VCC | 5V (Pin 2 or 4) |
| | GND | GND (Pin 6, 9, 14, etc.) |
| | SDA | GPIO 2 (Pin 3) |
| | SCL | GPIO 3 (Pin 5) |
| **NeoPixel Strip** | +5V | 5V (Pin 2 or 4) |
| | GND | GND (Pin 6) |
| | Din | **GPIO 18 / PWM0 (Pin 12)** *[Strict requirement for WS281x]* |
| **Scroll Button**| Terminal 1 | GPIO 17 (Pin 11) |
| | Terminal 2 | GND |
| **Select Button**| Terminal 1 | GPIO 27 (Pin 13) |
| | Terminal 2 | GND |

## ⚙️ Installation & Setup

### 1. System Dependencies
Install the required system-level packages for audio playback, font rendering, and native audio decoding:
```bash
sudo apt-get update
sudo apt-get install mpg123 fonts-dejavu ffmpeg