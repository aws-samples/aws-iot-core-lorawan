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


initial_state_name = "Initial"


def get_states(self):
    states = [
        {
            "stateName": "Initial",
            "onInput": {
                "events": [
                    {
                        "eventName": "CountInputs",
                        "condition": "true",
                        "actions": [
                            {
                                "setVariable": {
                                    "variableName": "input_message_count",
                                    "value": "$variable.input_message_count + 1"
                                }
                            }
                        ]
                    },
                    {
                        "eventName": "SetGatewayId",
                        "condition": "true",
                        "actions": [
                            {
                                "setVariable": {
                                    "variableName": "gatewayid",
                                    "value": "$input.LoRaWANGatewayConnectivityStatusInput.gatewayid"
                                }
                            }
                        ]
                    }
                ],
                "transitionEvents": [
                    {
                        "eventName": "IsConnected",
                        "condition": "$input.LoRaWANGatewayConnectivityStatusInput.last_connection_status == 'Connected'",
                        "actions": [],
                        "nextState": "Connected"
                    },
                    {
                        "eventName": "IsDisconnected",
                        "condition": "$input.LoRaWANGatewayConnectivityStatusInput.last_connection_status == 'Disconnected'",
                        "actions": [],
                        "nextState": "Disconnected"
                    }
                ]
            },
            "onEnter": {
                "events": [
                    {
                        "eventName": "Initialize",
                        "condition": "true",
                        "actions": [
                            {
                                "setVariable": {
                                    "variableName": "input_message_count",
                                    "value": "0"
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
            "stateName": "Connected",
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
                                    "variableName": "lastupdate_timestamp_iso8601",
                                    "value": "$input.LoRaWANGatewayConnectivityStatusInput.timestamp_iso8601"
                                }
                            }
                        ]
                    },
                    {
                        "eventName": "IsDisconnected",
                        "condition": "$input.LoRaWANGatewayConnectivityStatusInput.last_connection_status == 'Disconnected'",
                        "actions": [
                            {
                                "setTimer": {
                                    "timerName": "DisconnectedTimer",
                                    "seconds": 300,
                                }
                            },
                            {
                                "setVariable": {
                                    "variableName": "disconnected_timer_pending",
                                    "value": "true"
                                }
                            }
                        ]
                    },
                    {
                        "eventName": "IsConnected",
                        "condition": "$input.LoRaWANGatewayConnectivityStatusInput.last_connection_status == 'Connected'",
                        "actions": [
                            {
                                "destroyTimer": {
                                    "timerName": "DisconnectedTimer"
                                }
                            },
                            {
                                "setVariable": {
                                    "variableName": "disconnected_timer_pending",
                                    "value": "false"
                                }
                            }
                        ]
                    }
                ],
                "transitionEvents": [
                    {
                        "eventName": "DisconnetedTimerTimeout",
                        "condition": "timeout('DisconnectedTimer')",
                        "actions": [
                            {
                                "setVariable": {
                                    "variableName": "disconnected_timer_pending",
                                    "value": "false"
                                }
                            }
                        ],
                        "nextState": "Disconnected"
                    }
                ]
            },
            "onEnter": {
                "events": [
                    {
                        "eventName": "PublishPresenceMessage",
                        "condition": "true",
                        "actions": [
                            {
                                "iotTopicPublish": {
                                    "mqttTopic": "'awsiotcorelorawan/events/presence/connected/'+$variable.gatewayid",
                                    "payload": {
                                        "contentExpression": "'{\"eventType\":\"connected\",\"gatewayid\":\"'+$variable.gatewayid+'\"}'",
                                        "type": "STRING"
                                    }
                                }
                            },
                            {
                                "sns": {
                                    "targetArn": "arn:aws:sns:" + self.region + ":" + self.account + ":LoRaWANGatewayNotificationTopic",
                                    "payload": {
                                        "contentExpression": "'RECONNECTED: Gateway ' + $variable.gatewayid + ' has established a connection to AWS IoT Core for LoRaWAN'",
                                        "type": "STRING"
                                    }
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
            "stateName": "Disconnected",
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
                                    "variableName": "lastupdate_timestamp_iso8601",
                                    "value": "$input.LoRaWANGatewayConnectivityStatusInput.timestamp_iso8601"
                                }
                            }
                        ]
                    }
                ],
                "transitionEvents": [
                    {
                        "eventName": "IsConnected",
                        "condition": "$input.LoRaWANGatewayConnectivityStatusInput.last_connection_status == 'Connected'",
                        "actions": [],
                        "nextState": "Connected"
                    }
                ]
            },
            "onEnter": {
                "events": [
                    {
                        "eventName": "Publish",
                        "condition": "true",
                        "actions": [
                            {
                                "iotTopicPublish": {
                                    "mqttTopic": "'awsiotcorelorawan/events/presence/disconnected/'+$variable.gatewayid",
                                    "payload": {
                                        "contentExpression": "'{\"eventType\":\"disconnected\",\"gatewayid\":\"'+$variable.gatewayid+'\"}'",
                                        "type": "JSON"
                                    }
                                }
                            },
                            {
                                "sns": {
                                    "targetArn": "arn:aws:sns:" + self.region + ":" + self.account + ":LoRaWANGatewayNotificationTopic",
                                    "payload": {
                                        "contentExpression": "'DISCONNECTED: Gateway ' + $variable.gatewayid + ' is disconnected from AWS IoT Core for LoRaWAN'",
                                        "type": "STRING"
                                    }
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
    ]

    return states
