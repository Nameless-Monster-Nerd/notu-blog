#!/usr/bin/env python3
"""
Nanoleaf Smart Lighting Relay
Mohikontok Sound Lab — Local relay machine script
Runs on a machine ON THE SAME NETWORK as Nanoleaf lights.
Polls this server for lighting commands and applies them locally.
"""

import json
import os
import socket
import struct
import subprocess
import sys
import time
import urllib.request
import urllib.error
import argparse
from pathlib import Path
from typing import Optional

# ── Configuration ───────────────────────────────────────────────────────────

CONFIG_DIR = Path.home() / ".nanoleaf_relay"
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULT_POLL_URL = "https://notu.us/api/nanoleaf/command.json"
DEFAULT_POLL_INTERVAL = 10  # seconds

# ── Presets — Lab-Ready Scenes ──────────────────────────────────────────────

PRESETS = {
    "session": {
        "name": "Recording Session",
        "on": True,
        "brightness": 40,
        "ct": 4000,
        "hue": 220,
        "sat": 30,
        "desc": "Cool, focused — vocal tracking & production",
    },
    "focus": {
        "name": "Focus Mode",
        "on": True,
        "brightness": 70,
        "ct": 6500,
        "hue": 240,
        "sat": 20,
        "desc": "Bright, cool — mixing & mastering",
    },
    "warm": {
        "name": "Warm Ambient",
        "on": True,
        "brightness": 25,
        "ct": 2700,
        "hue": 30,
        "sat": 40,
        "desc": "Warm, dim — client intake & listening sessions",
    },
    "party": {
        "name": "Party Mode",
        "on": True,
        "brightness": 80,
        "ct": 5000,
        "hue": 0,
        "sat": 100,
        "desc": "Colorful — showcases & events",
    },
    "off": {
        "name": "All Off",
        "on": False,
        "desc": "Lights off",
    },
}


# ── Nanoleaf API Client ─────────────────────────────────────────────────────

NANOLEAF_PORT = 16021


def discover_nanoleaf(timeout: float = 3.0) -> list[dict]:
    """Discover Nanoleaf devices on the local network via UDP."""
    print("🔍 Scanning for Nanoleaf devices on your network...")
    devices = []

    # UDP broadcast discovery
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(timeout)

    msg = json.dumps(
        {"host": {"name": "nanoleaf_relay"}, "deviceType": "NLRelay"}
    ).encode()

    try:
        sock.sendto(msg, ("255.255.255.255", NANOLEAF_PORT))
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                print(f"  → Response from {addr}")
                devices.append({"ip": addr[0], "port": addr[1], "raw": data})
            except socket.timeout:
                break
    finally:
        sock.close()

    # Also try mDNS / avahi
    try:
        result = subprocess.run(
            ["avahi-browse", "-at", "--terminate"],
            capture_output=True, text=True, timeout=timeout,
        )
        for line in result.stdout.splitlines():
            if "nanoleaf" in line.lower():
                print(f"  → mDNS: {line.strip()}")
    except FileNotFoundError:
        pass  # avahi not installed
    except subprocess.TimeoutExpired:
        pass

    return devices


def get_device_ip() -> str:
    """Get Nanoleaf device IP from config or discovery."""
    config = load_config()
    ip = config.get("device_ip")
    if ip:
        return ip

    print("\n⚠️  No device IP configured.")
    devices = discover_nanoleaf()
    if not devices:
        print("❌ No Nanoleaf devices found via broadcast.")
        print("   Make sure your laptop is on the same Wi-Fi as the lights.")
        ip = input("   Enter Nanoleaf IP manually: ").strip()
        if not ip:
            print("❌ No IP provided. Exiting.")
            sys.exit(1)
        return ip

    print(f"\n📡 Found {len(devices)} device(s):")
    for i, d in enumerate(devices):
        print(f"  [{i}] {d['ip']}:{d['port']}")
    choice = input("   Select device number (0): ").strip()
    idx = int(choice) if choice.isdigit() else 0
    return devices[idx]["ip"]


def get_api_token(device_ip: str) -> str:
    """Get or create Nanoleaf API token."""
    config = load_config()
    token = config.get("api_token")
    if token:
        return token

    print(f"\n🔑 No API token found.")
    print(f"   Press and hold the power button on your Nanoleaf device for 5-7 seconds")
    print(f"   (the LED will start flashing) then press Enter...")
    input("   Ready? ")

    url = f"http://{device_ip}:{NANOLEAF_PORT}/api/v1/new"
    try:
        req = urllib.request.Request(url, data=b"", method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            token = result.get("auth_token")
            if token:
                print(f"✅ Token obtained: {token}")
                config["api_token"] = token
                save_config(config)
                return token
    except Exception as e:
        print(f"❌ Failed to get token: {e}")
        sys.exit(1)


def api_call(device_ip: str, token: str, path: str, method: str = "GET",
             data: Optional[dict] = None) -> dict:
    """Make a Nanoleaf API call."""
    url = f"http://{device_ip}:{NANOLEAF_PORT}/api/v1/{token}/{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        print(f"  ⚠️ API error {e.code}: {e.read().decode()}")
        raise
    except Exception as e:
        print(f"  ⚠️ Connection error: {e}")
        raise


def identify(device_ip: str, token: str):
    """Flash the lights briefly to find the device."""
    print("💡 Identifying device (lights will flash)...")
    api_call(device_ip, token, "identify", method="PUT")


def set_power(device_ip: str, token: str, on: bool):
    """Turn lights on/off."""
    api_call(device_ip, token, "state/on", method="PUT",
             data={"on": {"value": on}})
    status = "ON" if on else "OFF"
    print(f"  🔌 Lights: {status}")


def set_brightness(device_ip: str, token: str, value: int, duration: int = 5):
    """Set brightness (0-100) with smooth transition."""
    value = max(0, min(100, value))
    api_call(device_ip, token, "state/brightness", method="PUT",
             data={"brightness": {"value": value, "duration": duration}})
    print(f"  ☀️  Brightness: {value}%")


def set_color_temp(device_ip: str, token: str, ct: int, duration: int = 5):
    """Set color temperature in Kelvin (1200-6500)."""
    ct = max(1200, min(6500, ct))
    api_call(device_ip, token, "state/ct", method="PUT",
             data={"ct": {"value": ct, "duration": duration}})
    print(f"  🌡️  Color Temp: {ct}K")


def set_hue(device_ip: str, token: str, hue: int, duration: int = 5):
    """Set hue in degrees (0-360)."""
    hue = hue % 360
    api_call(device_ip, token, "state/hue", method="PUT",
             data={"hue": {"value": hue, "duration": duration}})
    print(f"  🎨 Hue: {hue}°")


def set_saturation(device_ip: str, token: str, sat: int, duration: int = 5):
    """Set saturation (0-100)."""
    sat = max(0, min(100, sat))
    api_call(device_ip, token, "state/sat", method="PUT",
             data={"sat": {"value": sat, "duration": duration}})
    print(f"  🎨 Saturation: {sat}%")


def apply_preset(device_ip: str, token: str, preset_name: str):
    """Apply a named preset."""
    preset = PRESETS.get(preset_name)
    if not preset:
        print(f"❌ Unknown preset: {preset_name}")
        print(f"   Available: {', '.join(PRESETS.keys())}")
        return False

    print(f"\n🎬 Applying preset: {preset['name']}")
    print(f"   {preset['desc']}")

    if not preset.get("on", True):
        set_power(device_ip, token, False)
        return True

    set_power(device_ip, token, True)
    time.sleep(0.5)

    if "brightness" in preset:
        set_brightness(device_ip, token, preset["brightness"])
    if "ct" in preset:
        set_color_temp(device_ip, token, preset["ct"])
    if "hue" in preset:
        set_hue(device_ip, token, preset["hue"])
    if "sat" in preset:
        set_saturation(device_ip, token, preset["sat"])

    print(f"✅ {preset['name']} — done!")
    return True


def get_device_info(device_ip: str, token: str) -> dict:
    """Get full device state."""
    return api_call(device_ip, token, "")


def list_effects(device_ip: str, token: str):
    """List available dynamic effects."""
    try:
        effects = api_call(device_ip, token, "effects/effectsList")
        print("\n✨ Available effects:")
        for e in effects:
            print(f"   • {e}")
    except Exception:
        print("  ⚠️ Could not fetch effects list")


def set_effect(device_ip: str, token: str, effect_name: str):
    """Set a dynamic effect."""
    api_call(device_ip, token, "effects", method="PUT",
             data={"select": effect_name})
    print(f"  ✨ Effect: {effect_name}")


# ── Config Management ───────────────────────────────────────────────────────

def load_config() -> dict:
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}


def save_config(config: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2))
    print(f"  💾 Config saved: {CONFIG_FILE}")


def setup_interactive():
    """First-time setup — discover device and get token."""
    print("=" * 56)
    print("  Nanoleaf Relay — Mohikontok Sound Lab Setup")
    print("=" * 56)

    device_ip = get_device_ip()
    token = get_api_token(device_ip)

    config = load_config()
    config["device_ip"] = device_ip
    config["api_token"] = token
    config["poll_url"] = config.get("poll_url", DEFAULT_POLL_URL)
    save_config(config)

    # Test connection
    print("\n🧪 Testing connection...")
    try:
        info = get_device_info(device_ip, token)
        name = info.get("name", "Unknown")
        fw = info.get("firmwareVersion", "?")
        print(f"   ✅ Connected to: {name} (FW: {fw})")
    except Exception as e:
        print(f"   ⚠️  Connection test failed: {e}")

    # Identify
    print("\n💡 Flashing lights to confirm device...")
    identify(device_ip, token)

    print("\n✅ Setup complete!")
    print(f"   Device IP: {device_ip}")
    print(f"   API Token: {token}")
    print("\n   Try: python3 nanoleaf_relay.py preset session")
    print(f"   Try: python3 nanoleaf_relay.py preset focus")
    print(f"   Try: python3 nanoleaf_relay.py preset warm")
    print(f"   Try: python3 nanoleaf_relay.py preset off")


# ── Daemon Mode (Poll Command Server) ───────────────────────────────────────

def daemon_loop():
    """Run as background daemon, polling for commands."""
    config = load_config()
    device_ip = config.get("device_ip")
    token = config.get("api_token")
    poll_url = config.get("poll_url", DEFAULT_POLL_URL)
    interval = config.get("poll_interval", DEFAULT_POLL_INTERVAL)

    if not device_ip or not token:
        print("❌ No device config found. Run 'setup' first.")
        sys.exit(1)

    print(f"\n🔄 Nanoleaf Relay Daemon — Starting...")
    print(f"   Device: {device_ip}")
    print(f"   Polling: {poll_url} every {interval}s")
    print(f"   Press Ctrl+C to stop\n")

    last_command_id = None

    while True:
        try:
            req = urllib.request.Request(poll_url)
            with urllib.request.urlopen(req, timeout=interval) as resp:
                data = json.loads(resp.read().decode())

            command_id = data.get("id")
            command = data.get("command")

            if command and command_id != last_command_id:
                print(f"\n📨 Command received: {command} (ID: {command_id})")

                if command in PRESETS:
                    apply_preset(device_ip, token, command)
                elif command == "identify":
                    identify(device_ip, token)
                elif command.startswith("brightness:"):
                    val = int(command.split(":")[1])
                    set_brightness(device_ip, token, val)
                elif command.startswith("ct:"):
                    val = int(command.split(":")[1])
                    set_color_temp(device_ip, token, val)
                elif command.startswith("hue:"):
                    val = int(command.split(":")[1])
                    set_hue(device_ip, token, val)
                else:
                    print(f"  ⚠️ Unknown command: {command}")

                last_command_id = command_id

            time.sleep(interval)

        except urllib.error.HTTPError as e:
            if e.code == 404:
                pass  # No commands yet
            time.sleep(interval)
        except urllib.error.URLError:
            print("  ⚠️ Cannot reach command server (no internet?)")
            time.sleep(interval * 2)
        except KeyboardInterrupt:
            print("\n🛑 Daemon stopped.")
            break
        except Exception as e:
            print(f"  ⚠️ Error: {e}")
            time.sleep(interval)


# ── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Nanoleaf Smart Lighting — Mohikontok Sound Lab"
    )
    parser.add_argument("action", nargs="?", default="status",
                        choices=["setup", "status", "preset", "identify",
                                 "on", "off", "brightness", "ct", "hue",
                                 "effects", "daemon"],
                        help="Action to perform")
    parser.add_argument("value", nargs="?", help="Value or preset name")

    args = parser.parse_args()

    if args.action == "setup":
        setup_interactive()
        return

    # Load config for subsequent commands
    config = load_config()
    device_ip = config.get("device_ip")
    token = config.get("api_token")

    if args.action == "daemon":
        daemon_loop()
        return

    if not device_ip or not token:
        print("❌ Not configured. Run: python3 nanoleaf_relay.py setup")
        sys.exit(1)

    if args.action == "status":
        info = get_device_info(device_ip, token)
        name = info.get("name", "Unknown")
        on = info.get("state", {}).get("on", {}).get("value", False)
        bri = info.get("state", {}).get("brightness", {}).get("value", 0)
        ct = info.get("state", {}).get("ct", {}).get("value", 0)
        hue = info.get("state", {}).get("hue", {}).get("value", 0)
        sat = info.get("state", {}).get("sat", {}).get("value", 0)

        print(f"\n📊 {name}")
        print(f"   Power:      {'ON' if on else 'OFF'}")
        print(f"   Brightness: {bri}%")
        print(f"   Color Temp: {ct}K")
        print(f"   Hue:        {hue}°")
        print(f"   Saturation: {sat}%")

    elif args.action == "preset":
        if not args.value:
            print("\n🎚️  Available presets:")
            for name, p in PRESETS.items():
                print(f"   {name:12s} — {p['name']:20s} ({p['desc']})")
            return
        if args.value == "list":
            print(json.dumps(PRESETS, indent=2))
            return
        apply_preset(device_ip, token, args.value)

    elif args.action == "identify":
        identify(device_ip, token)

    elif args.action == "on":
        set_power(device_ip, token, True)

    elif args.action == "off":
        set_power(device_ip, token, False)

    elif args.action == "brightness":
        val = int(args.value or 50)
        set_brightness(device_ip, token, val)

    elif args.action == "ct":
        val = int(args.value or 4000)
        set_color_temp(device_ip, token, val)

    elif args.action == "hue":
        val = int(args.value or 200)
        set_hue(device_ip, token, val)

    elif args.action == "effects":
        list_effects(device_ip, token)


if __name__ == "__main__":
    main()
