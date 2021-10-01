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


initial_state_name = "Healthy"


def get_states(self):
    states = [
            {
                "stateName": "Healthy",
                "onInput": {
                    "events": [
                        {
                            "eventName": "CollectInputMetrics",
                            "condition": "true",
                            "actions": [
                                {
                                    "setVariable": {
                                        "variableName": "input_message_count",
                                        "value": "$variable.input_message_count + 1"
                                    }
                                },
                                {
                                    "setVariable": {
                                        "variableName": "lastupdate_timestamp_ms",
                                        "value": "$input.LoRaWANDeviceWatchdogInput.timestamp_ms"
                                    }
                                }
                            ]
                        },
                        {
                            "eventName": "ResetDisconnectedTimer",
                            "condition": "true",
                            "actions": [
                                {
                                    "resetTimer": {
                                        "timerName": "DisconnectedTimer"
                                    }
                                },
                                {
                                    "setVariable": {
                                        "variableName": "timestamp_last_uplink"
                                    }
                                }
                            ]
                        },
                        {
                            "eventName": "PublishPresenceMessage",
                            "condition": "true",
                            "actions": [
                                {
                                    "iotTopicPublish": {
                                        "mqttTopic": "awsiotcorelorawan/events/uplink",
                                        "payload": {
                                            "contentExpression": "'{\"deviceid\":\"'+$variable.deviceid + '\", \"type\":\"uplink\"}'",
                                            "type": "JSON"
                                        }
                                    }
                                }
                            ]
                        }
                    ],
                    "transitionEvents": [
                        {
                            "eventName": "onDisconnetedTimerTimeout",
                            "condition": "timeout('DisconnectedTimer')",
                            "actions": [],
                            "nextState": "Unhealthy"
                        }
                    ]
                },
                "onEnter": {
                    "events": [
                        {
                            "eventName": "InitializeVariables",
                            "condition": "isUndefined($variable.initalization_complete)",
                            "actions": [
                                {
                                    "setVariable": {
                                        "variableName": "input_message_count",
                                        "value": "0"
                                    }
                                },
                                {
                                    "setVariable": {
                                        "variableName": "lastupdate_timestamp_ms",
                                        "value": "0"
                                    }
                                },
                                {
                                    "setVariable": {
                                        "variableName": "deviceid",
                                        "value": "$input.LoRaWANDeviceWatchdogInput.deviceid"
                                    }
                                },
                                {
                                    "setVariable": {
                                        "variableName": "initalization_complete",
                                        "value": "true"
                                    }
                                }
                            ]
                        },
                        {
                            "eventName": "CreateDisconnectedTimer",
                            "condition": "true",
                            "actions": [
                                {
                                    "setTimer": {
                                        "timerName": "DisconnectedTimer",
                                        "seconds": 60
                                        
                                    }
                                }
                            ]
                        }
                    ]
                },
                "onExit": {
                    "events": []
                }
            },
            {
                "stateName": "Unhealthy",
                "onInput": {
                    "events": [
                        {
                            "eventName": "CollectInputMetrics",
                            "condition": "true",
                            "actions": [
                                {
                                    "setVariable": {
                                        "variableName": "input_message_count",
                                        "value": "$variable.input_message_count + 1"
                                    }
                                },
                                {
                                    "setVariable": {
                                        "variableName": "lastupdate_timestamp_ms",
                                        "value": "$input.LoRaWANDeviceWatchdogInput.timestamp_ms"
                                    }
                                }
                            ]
                        }
                    ],
                    "transitionEvents": [
                        {
                            "eventName": "onIncomingTelemetry",
                            "condition": "$input.LoRaWANDeviceWatchdogInput.deviceid != \"\"",
                            "actions": [],
                            "nextState": "Healthy"
                        }
                    ]
                },
                "onEnter": {
                    "events": [
                        {
                            "eventName": "NotifyAboutUnhealthyDevice",
                            "condition": "true",
                            "actions": [
                                {
                                    "iotTopicPublish": {
                                        "mqttTopic": "'awsiotcorelorawan/events/presence/missingheartbeat/'+$variable.deviceid",
                                        "payload": {
                                            "contentExpression": "'{\"deviceid\":\"'+$variable.deviceid + '\", \"type\":\"missingheartbeat\"}'",
                                            "type": "JSON"
                                        }
                                    }
                                }
                            ]
                        },
                        {
                            "eventName": "DisableTimer",
                            "condition": "true",
                            "actions": [
                                {
                                    "clearTimer": {
                                        "timerName": "DisconnectedTimer"
                                    }
                                }
                            ]
                        }
                    ]
                },
                "onExit": {
                    "events": []
                }
            }
        ];
    return states
