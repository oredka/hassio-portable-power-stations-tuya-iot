# Changelog

## [1.0.1] - 2026-01-19

### Fixed
- Fixed HACS integration name display - now shows "Portable Power Stations (Tuya IoT)" instead of "2E Power Stations"
- Updated hacs.json with complete domain list (sensor, switch, select, binary_sensor)

## [1.0.0] - 2026-01-19

### Initial Release

Complete Home Assistant integration for Portable Power Stations via Tuya IoT Cloud.

#### Features
- **Battery Monitoring** - Real-time battery level tracking with Energy Dashboard support
- **Power Sensors** - Comprehensive monitoring of Input/Output power, AC/DC/USB ports
- **Temperature & Frequency** - Device temperature and AC frequency sensors
- **Output Controls** - Switches for AC/DC outputs and buzzer
- **Timer Controls** - Configurable auto-off timers for AC/DC/LED, standby and display
- **LED Mode Control** - 6 brightness levels: Off, High Light, Strobe, Half Bright, Low, SOS
- **Error Monitoring** - Comprehensive error code reporting

#### Supported Devices
- 2E SYAYVO-BP2400_D (2400Wh portable power station)
- Compatible with other Tuya-based portable power stations using standard instruction set

#### Technical Details
- Uses Tuya Standard Instruction Set for broad device compatibility
- Official tuya-connector-python SDK integration
- 30-second update interval (configurable)
- Full Home Assistant integration standards compliance
- Multi-region support (EU, US, China, India)

#### Available Entities
- **Sensors**: Battery Level, Input/Output Power, AC/DC/USB Power, Temperature, AC Frequency, Error Code, Input Type, Battery Power (Energy Dashboard)
- **Switches**: AC Output, DC Output, Buzzer
- **Select Controls**: LED Mode, AC/DC/LED Auto-Off Timers, Standby Timer, Display Auto-Off Timer
- **Binary Sensors**: USB Output Status
