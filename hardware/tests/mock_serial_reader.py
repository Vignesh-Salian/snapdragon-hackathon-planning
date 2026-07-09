#!/usr/bin/env python3
"""
mock_serial_reader.py
HemaGrid AI - Serial Packet Validation Test Script

Reads the output stream of the Smart Cold Box Arduino via USB Serial,
validates syntax structure, parses sensor fields, and checks values against
the clinical JSON telemetry schema.
"""

import argparse
import json
import sys
import time

try:
    import serial
except ImportError:
    print("Error: 'pyserial' package is required to run this script.")
    print("Install it using: pip install pyserial")
    sys.exit(1)

# ANSI Terminal Coloring
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_CYAN = "\033[96m"
COLOR_RESET = "\033[0m"

def log_info(msg):
    print(f"[{COLOR_CYAN}INFO{COLOR_RESET}] {msg}")

def log_success(msg):
    print(f"[{COLOR_GREEN}PASS{COLOR_RESET}] {msg}")

def log_warn(msg):
    print(f"[{COLOR_YELLOW}WARN{COLOR_RESET}] {msg}")

def log_error(msg):
    print(f"[{COLOR_RED}FAIL{COLOR_RESET}] {msg}")

def validate_packet(packet):
    """
    Validates packet structure against HemaGrid telemetry specs.
    """
    required_keys = ["device_id", "uptime_ms", "telemetry", "status"]
    for key in required_keys:
        if key not in packet:
            return False, f"Missing required root key: '{key}'"

    telemetry = packet["telemetry"]
    required_telemetry = ["temperature_c", "humidity_pct", "acceleration_g", "max_impact_g"]
    for key in required_telemetry:
        if key not in telemetry:
            return False, f"Missing telemetry key: '{key}'"

    status = packet["status"]
    required_status = ["state", "flags"]
    for key in required_status:
        if key not in status:
            return False, f"Missing status key: '{key}'"

    flags = status["flags"]
    required_flags = ["temp_breached", "impact_breached"]
    for key in required_flags:
        if key not in flags:
            return False, f"Missing flag key: '{key}'"

    state = status["state"]
    if state not in ["SAFE", "WARNING", "COMPROMISED"]:
        return False, f"Invalid state value: '{state}'"

    return True, "Valid"

def read_serial_stream(port, baud, timeout):
    log_info(f"Opening port {port} at {baud} baud (timeout={timeout}s)...")
    try:
        ser = serial.Serial(port, baud, timeout=timeout)
        time.sleep(2)  # Allow Arduino bootloader reset to settle
        ser.reset_input_buffer()
        log_success("Serial link established. Monitoring stream... Press Ctrl+C to stop.")
    except Exception as e:
        log_error(f"Failed to connect to serial port: {e}")
        return

    try:
        while True:
            if ser.in_waiting > 0:
                raw_line = ser.readline()
                try:
                    decoded_line = raw_line.decode('utf-8').strip()
                except UnicodeDecodeError:
                    log_warn("Received malformed bytes. Skipping frame.")
                    continue

                if not decoded_line:
                    continue

                # Print raw packet for reference
                print(f"\n{COLOR_CYAN}--> RAW:{COLOR_RESET} {decoded_line}")

                try:
                    packet = json.loads(decoded_line)
                    is_valid, reason = validate_packet(packet)
                    
                    if is_valid:
                        state = packet["status"]["state"]
                        color = COLOR_GREEN
                        if state == "WARNING":
                            color = COLOR_YELLOW
                        elif state == "COMPROMISED":
                            color = COLOR_RED
                            
                        log_success("JSON Telemetry Frame matches spec schema.")
                        print(f"    Device:      {packet['device_id']}")
                        print(f"    Uptime:      {packet['uptime_ms']} ms")
                        print(f"    State:       {color}{state}{COLOR_RESET}")
                        print(f"    Temperature: {packet['telemetry']['temperature_c']} C")
                        print(f"    Humidity:    {packet['telemetry']['humidity_pct']} %")
                        print(f"    Acc Force:   {packet['telemetry']['acceleration_g']} g")
                        print(f"    Max Impact:  {packet['telemetry']['max_impact_g']} g")
                    else:
                        log_error(f"Schema Validation Failure: {reason}")
                except json.JSONDecodeError:
                    log_error("Failed to parse line as JSON string.")
            time.sleep(0.01)
    except KeyboardInterrupt:
        log_info("Exiting test execution by operator interrupt.")
    finally:
        ser.close()
        log_info("Serial port connection closed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HemaGrid AI Serial Telemetry Validator")
    parser.add_argument("--port", type=str, default="COM3", help="Target serial port name (e.g. COM3 or /dev/ttyACM0)")
    parser.add_argument("--baud", type=int, default=115200, help="Baud rate (default: 115200)")
    parser.add_argument("--timeout", type=float, default=1.0, help="Serial read timeout (default: 1.0)")
    args = parser.parse_args()

    read_serial_stream(args.port, args.baud, args.timeout)
