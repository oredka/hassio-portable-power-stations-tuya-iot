# Changelog

## [1.0.1] - 2026-01-19

### Fixed
- Fixed ValueError in ac_voltage_freq sensor - now handles string values like "230V_50HZ"

## [1.0.0] - 2026-01-19

### Added
- Full integration with Tuya IoT Cloud for 2E Power Stations
- Complete support for all device Data Points (DPs)
- Sensors: Battery, Input/Output Power, AC/DC/USB Power, Temperature, AC Voltage/Frequency, Error Code
- Switches: AC/DC/USB Outputs, Buzzer, LED Mode
- Energy Dashboard support with proper device classes
- Automatic device discovery and setup via config flow
- Multi-region support (EU, US, China, India)
- Comprehensive error handling with user-friendly messages
- Support for 2E SYAYVO-BP2400_D model

### Technical Details
- Uses official tuya-connector-python SDK
- 30-second update interval (configurable)
- Proper state management and entity updates
- Full Home Assistant integration standards compliance
