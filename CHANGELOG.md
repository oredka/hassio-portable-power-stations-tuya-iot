# Changelog

## [1.0.4] - 2026-01-19

### Fixed
- Changed USB Output from switch to binary sensor - USB ports cannot be controlled, only monitored for status

### Changed
- USB Output now appears as binary sensor showing active/inactive status instead of non-functional switch

## [1.0.3] - 2026-01-19

### Fixed
- Fixed icon/logo display - removed URLs from manifest.json, Home Assistant now uses local icon.png and logo.png files

## [1.0.2] - 2026-01-19

### Added
- Added 5 timer select entities: AC Auto-Off Time, DC Auto-Off Time, LED Auto-Off Time, Standby Time, Display Auto-Off Time
- Full control over all device settings including power management timers

### Changed
- Renamed entities to match EcoFlow naming convention (e.g., "Main Battery Level", "Total In Power", "AC Enabled")
- LED Mode moved from sensor to select entity for proper control

### Fixed
- Fixed LED mode control - now properly supports all modes (Off, 10%, 30%, 50%, 100%, Breathing, SOS)

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
