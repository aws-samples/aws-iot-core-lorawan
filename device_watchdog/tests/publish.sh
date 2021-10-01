aws iotevents-data batch-put-message \
    --cli-input-json file://event.json


# {"deviceid":"1","timestamp_ms":1234} eyJkZXZpY2VpZCI6IjEiLCJ0aW1lc3RhbXBfbXMiOjEyMzR9
# Run this command to generate payload:
# echo "{"deviceid":"126","timestamp_ms":1234}" | base64 -