# 2E Power Stations for Home Assistant

Home Assistant integration for 2E Power Stations via Tuya IoT Cloud.

## Features

- **Battery monitoring** - Real-time battery level tracking
- **Power sensors** - Input/Output power, AC/DC/USB ports monitoring
- **Temperature & Frequency** - Device temperature and AC frequency sensors
- **Output controls** - AC/DC/USB output switches
- **Additional features** - Buzzer and LED mode controls


## Supported Models

- 2E SYAYVO

## Installation

### Prerequisites

1. Create account at [Tuya IoT Platform](https://iot.tuya.com)
2. Create Cloud Project and subscribe to all APIs
3. Link your device via "Link App Account" using Smart Life credentials

### Setup

1. Add integration in Home Assistant: **Settings → Devices & Services → Add Integration**
2. Search for "2E Power Station"
3. Enter your Tuya Cloud credentials:
   - Access ID
   - Access Secret
   - Device ID
   - Region (EU/US/China/India)

## Available Entities

**Sensors:** Battery, Input Power, Output Power, AC/DC/USB Power, Temperature, AC Frequency, Error Code, Input Type
**Switches:** AC Output, DC Output, USB Output, Buzzer, LED Mode

## License

MIT
