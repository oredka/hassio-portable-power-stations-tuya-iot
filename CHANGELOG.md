# Changelog

## [1.4.1] - 2026-01-19

### Fixed
- Fixed timer select entities with correct Tuya enum values from IoT Platform specifications
- AC/DC/LED Auto-Off Time now accepts: 2hour, 4hour, 8hour, 12hour, do_not_close
- Standby Time now accepts: 3min, 5min, 15min, 60min, do_not_close
- Display Auto-Off Time now accepts: 2min, 5min, 10min, 20min, do_not_close
- Eliminated "command or value not support" (error 2008) for all timer settings

### Changed
- Restored timer select entities (writable via Tuya API with correct enum values)
- Removed timer sensors (no longer needed now that selects work correctly)

## [1.4.0] - 2026-01-19

### Breaking Changes
- Removed timer select entities (AC/DC/LED auto-off, Standby, Display off) - they are read-only via Tuya API
- Timers now available as sensors (read-only) - can only be changed via device buttons or Tuya app

### Fixed
- Eliminated "command or value not support" errors for timer settings
- Fixed lamp_flash not in options map warning

### Added
- Timer sensors for monitoring: AC Auto-Off Time, DC Auto-Off Time, LED Auto-Off Time, Standby Time, Display Auto-Off Time

## [1.3.1] - 2026-01-19

### Fixed
- Updated LED Mode options to match Tuya app exactly
- Added missing "Strobe" mode (lamp_flash)

### Changed
- Renamed LED modes to match Tuya app: High Light, Low, Half Bright, Strobe, SOS, Off
- Removed duplicate and unsupported brightness levels

## [1.3.0] - 2026-01-19

### Fixed
- Removed unsupported "Breathing" mode from LED Mode options (causes Tuya API error)
- LED Mode now works correctly with all supported modes (Off, 10%, 30%, 50%, 100%, SOS)

### Changed
- Cleaned up debug logging after diagnosing LED Mode issue
- Updated TROUBLESHOOTING.md with LED Mode information

## [1.2.2] - 2026-01-19

### Added
- TROUBLESHOOTING.md with solutions for common issues (icon display, LED Mode)

### Fixed
- Documentation for icon display issues and browser cache clearing

## [1.2.1] - 2026-01-19

### Added
- Debug logging for LED Mode to diagnose configuration issues
- Detailed error logging for select entity command failures

### Changed
- Improved diagnostic logging for Tuya data points

## [1.2.0] - 2026-01-19

### Added
- High-resolution icon support (icon@2x.png) for better display quality

### Fixed
- Fixed connection test error handling in initialization
- Improved error messages with detailed Tuya Cloud connection failures

### Changed
- Code cleanup and final refactoring for stable release

## [1.1.2] - 2026-01-19

### Changed
- Improved entity display order: switches first, then selects, then sensors

## [1.1.1] - 2026-01-19

### Changed
- Fixed GitHub Actions release workflow to use native actions
- Removed Energy Dashboard documentation file

## [1.1.0] - 2026-01-19

### Added
- Battery Power sensor for Energy Dashboard integration (sensor.battery_power)
- Support for Home Assistant Energy Dashboard battery configuration

### Changed
- Code refactoring: improved API client readability and removed unused methods
- Removed unnecessary utility scripts and files
- Simplified error handling and logging

### Removed
- GitLab CI/CD files (.gitlab-ci.yml, create_gitlab_release.py)
- Unused utility scripts (create_github_release.py, list_devices.py)
- Unused sensor data processor file
- Installation documentation (moved to README)

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
