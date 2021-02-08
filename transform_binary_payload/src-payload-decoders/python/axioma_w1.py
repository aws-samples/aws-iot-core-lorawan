# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import base64
import datetime


def int_from_bytes_at_offset(bytes, block_offset, block_size):
    # accomodate LSB order
    offset = block_offset + block_size - 1
    bit_shift = 8 * (block_size - 1)

    int_value = 0
    while offset >= block_offset:
        byte = bytes[offset]
        offset -= 1
        int_value |= byte << bit_shift
        bit_shift -= 8

    return int_value


def timestamp_from_bytes_at_offset(bytes, offset):
    milliseconds = int_from_bytes_at_offset(bytes, offset, 4)
    return datetime.datetime.fromtimestamp(milliseconds, tz=datetime.timezone.utc)


def decode_primary_data(bytes, offset, decoded_payload):

    size = 4
    decoded_payload["timestamp"] = timestamp_from_bytes_at_offset(
        bytes, offset).isoformat()
    offset += size

    size = 1
    decoded_payload["status"] = bytes[offset]
    offset += size

    size = 4
    decoded_payload["total_volume"] = int_from_bytes_at_offset(
        bytes, offset, size)
    offset += size

    return offset


def decode_log_data(bytes, offset, decoded_payload):

    # Get all available log data - variable number up to 15 deltas
    decoded_payload["log_data"] = {}

    size = 4
    # Log data is always taken at the start of the storage period - 1hr by default
    cumulative_timestamp = timestamp_from_bytes_at_offset(
        bytes, offset).replace(minute=0, second=0, microsecond=0)
    decoded_payload["log_data"]["timestamp_0"] = cumulative_timestamp.isoformat()
    offset += size

    size = 4
    decoded_payload["log_data"]["volume_0"] = int_from_bytes_at_offset(
        bytes, offset, size)
    offset += size

    cumulative_volume = decoded_payload["log_data"]["volume_0"]

    log_index = 1
    payload_size = len(bytes)
    while offset < payload_size:
        # Add an hour - Change this to match the meter log storage period, default is 1 hour
        cumulative_timestamp += datetime.timedelta(hours=1)

        size = 2
        cumulative_volume += int_from_bytes_at_offset(bytes, offset, size)
        offset += size

        decoded_payload["log_data"][f"timestamp_{log_index}"] = cumulative_timestamp.isoformat()
        decoded_payload["log_data"][f"volume_{log_index}"] = cumulative_volume

        log_index += 1

    return offset


def decode_individual_alarm(alarm_status, alarm_test_value, higher_alarm):
    alarm = (alarm_status == alarm_test_value) and not higher_alarm
    higher_alarm = alarm or higher_alarm
    return alarm, higher_alarm


def decode_alarm_data(decoded_payload):
    # Decode alarms from status byte - higher in the list takes precedence
    higher_alarm = False
    alarm_status = decoded_payload["status"]

    decoded_payload["alarm_low_temperature"], higher_alarm = decode_individual_alarm(
        alarm_status, 0x90, higher_alarm)
    decoded_payload["alarm_leakage"], higher_alarm = decode_individual_alarm(
        alarm_status, 0x30, higher_alarm)
    decoded_payload["alarm_burst"], higher_alarm = decode_individual_alarm(
        alarm_status, 0xB0, higher_alarm)
    decoded_payload["alarm_backflow"], higher_alarm = decode_individual_alarm(
        alarm_status, 0x70, higher_alarm)
    decoded_payload["alarm_dry"], higher_alarm = decode_individual_alarm(
        alarm_status, 0x10, higher_alarm)
    decoded_payload["alarm_manipulation"], higher_alarm = decode_individual_alarm(
        alarm_status, 0xD0, higher_alarm)
    decoded_payload["alarm_permanent"], higher_alarm = decode_individual_alarm(
        alarm_status, 0x08, higher_alarm)
    decoded_payload["alarm_battery"], higher_alarm = decode_individual_alarm(
        alarm_status, 0x04, higher_alarm)


def dict_from_payload(payload, fport: int = None):
    bytes = base64.b64decode(payload)

    decoded_payload = {}
    offset = 0

    offset = decode_primary_data(bytes, offset, decoded_payload)
    offset = decode_log_data(bytes, offset, decoded_payload)
    decode_alarm_data(decoded_payload)

    return decoded_payload


if __name__ == "__main__":
    # This payload is taken from Axioma_Lora_Payload_W1_F1_V2.0 (1).pdf - doc is a little wrong
    hex_bytes = "0ea0355d302935000054c0345de7290000b800b900b800b800b800b900b800b800b800b800b800b800b900b900b900"
    base_64_bytes = base64.b64encode(bytes.fromhex(hex_bytes)).decode()

    # Actual meter reading
    # base_64_bytes = "eoFaXxADAAAAwKRZXwMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="

    decoded_dict = dict_from_payload(base_64_bytes)

    import json
    print(json.dumps(decoded_dict, indent=4))
