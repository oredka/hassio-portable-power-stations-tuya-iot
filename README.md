# Portable Power Stations (Tuya IoT) for Home Assistant

Home Assistant integration for Portable Power Stations via Tuya IoT Cloud.

## Features

- **Battery monitoring** - Real-time battery level tracking with Energy Dashboard support
- **Power sensors** - Input/Output power, AC/DC/USB ports monitoring
- **Temperature & Frequency** - Device temperature and AC frequency sensors
- **Output controls** - AC/DC/USB output switches
- **Timer controls** - Auto-off timers for AC/DC/LED, standby and display settings
- **Additional features** - Buzzer and LED mode controls

## Supported Devices

Currently tested and working with:
- **2E SYAYVO** - 2400Wh portable power station

The integration uses Tuya Standard Instruction Set and should work with other Tuya-based portable power stations that support the same data points.

## Installation

### Prerequisites

1. Create account at [Tuya IoT Platform](https://iot.tuya.com)
2. Create Cloud Project and subscribe to all APIs (Authorization, Smart Home Devices Management, IoT Core)
3. Link your device via "Link App Account" using Smart Life or Tuya Smart app credentials

### Setup

1. Add integration in Home Assistant: **Settings → Devices & Services → Add Integration**
2. Search for "Portable Power Stations"
3. Enter your Tuya Cloud credentials:
   - Access ID
   - Access Secret
   - Device ID
   - Region (EU/US/China/India)

## Available Entities

### Sensors
Battery Level, Input Power, Output Power, AC/DC/USB Power, Temperature, AC Frequency, Error Code, Input Type, Battery Power (for Energy Dashboard)

### Switches
AC Output, DC Output, Buzzer

### Select Controls
LED Mode, AC Auto-Off Timer, DC Auto-Off Timer, LED Auto-Off Timer, Standby Timer, Display Auto-Off Timer

### Binary Sensors
USB Output Status

## License

MIT
