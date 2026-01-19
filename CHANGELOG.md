# Changelog

## [0.3.7] - 2026-01-19

### Fixed
- Fixed permission denied error (code 1106) handling with detailed instructions
- Improved error messages for device authorization issues
- Added helper script to list all available devices

### Added
- Added list_devices.py utility script
- Enhanced API error handling with specific error codes

## [0.3.6] - 2026-01-19

### Added
- GitHub Actions workflow for automatic releases
- create_github_release.py script for release automation

## [0.3.3] - 2026-01-19

### Fixed
- Fixed "token invalid" error - added connect() call for Tuya Cloud API authentication
