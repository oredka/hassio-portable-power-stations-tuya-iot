#!/usr/bin/env python3
"""
List all devices available in Tuya Cloud Project
Helps to find correct Device ID
"""

import sys
from tuya_connector import TuyaOpenAPI


def list_devices(access_id: str, access_secret: str, endpoint: str = "https://openapi.tuyaeu.com"):
    """List all devices in Tuya Cloud Project"""

    print(f"Connecting to Tuya Cloud: {endpoint}")
    api = TuyaOpenAPI(endpoint, access_id, access_secret)
    api.connect()
    print("✓ Connected successfully\n")

    # Get user info
    print("Fetching user info...")
    user_response = api.get("/v1.0/token", {"grant_type": 1})
    print(f"User info: {user_response}\n")

    # Try to get devices through different endpoints
    print("=" * 80)
    print("Method 1: Get devices by user ID")
    print("=" * 80)

    # First, get user/app info to find UID
    user_info = api.get("/v1.0/users/1/infos")
    print(f"User info response: {user_info}\n")

    # Try direct device list
    print("=" * 80)
    print("Method 2: Get all devices (if admin)")
    print("=" * 80)
    devices_response = api.get("/v1.0/devices")

    if devices_response.get("success"):
        devices = devices_response.get("result", [])
        print(f"✓ Found {len(devices)} devices\n")

        for i, device in enumerate(devices, 1):
            print(f"Device {i}:")
            print(f"  Name: {device.get('name')}")
            print(f"  Device ID: {device.get('id')}")
            print(f"  Product ID: {device.get('product_id')}")
            print(f"  Category: {device.get('category')}")
            print(f"  Model: {device.get('model')}")
            print(f"  Online: {device.get('online')}")
            print(f"  Status: {device.get('status')}")
            print()
    else:
        print(f"✗ Failed to get devices: {devices_response}")
        print("\nTrying alternative method...")

        # Try getting devices via asset
        print("\n" + "=" * 80)
        print("Method 3: Get devices via asset")
        print("=" * 80)

        # Get asset list
        assets_response = api.get("/v2.0/cloud/thing/asset")
        print(f"Assets response: {assets_response}\n")

        if assets_response.get("success"):
            assets = assets_response.get("result", {}).get("list", [])
            for asset in assets:
                asset_id = asset.get("asset_id")
                print(f"Checking asset: {asset.get('asset_name')} (ID: {asset_id})")

                # Get devices in this asset
                asset_devices = api.get(f"/v2.0/cloud/thing/asset/{asset_id}/device")
                if asset_devices.get("success"):
                    devices = asset_devices.get("result", {}).get("list", [])
                    print(f"  Found {len(devices)} devices")

                    for device in devices:
                        print(f"    - {device.get('name')} (ID: {device.get('id')})")
                print()


def main():
    if len(sys.argv) < 3:
        print("Usage: python list_devices.py <ACCESS_ID> <ACCESS_SECRET> [ENDPOINT]")
        print("\nEndpoints:")
        print("  Europe: https://openapi.tuyaeu.com (default)")
        print("  US: https://openapi.tuyaus.com")
        print("  China: https://openapi.tuyacn.com")
        print("  India: https://openapi.tuyain.com")
        sys.exit(1)

    access_id = sys.argv[1]
    access_secret = sys.argv[2]
    endpoint = sys.argv[3] if len(sys.argv) > 3 else "https://openapi.tuyaeu.com"

    try:
        list_devices(access_id, access_secret, endpoint)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
