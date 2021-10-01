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


from aws_cdk import core as cdk
from aws_cdk import aws_iam as iam
from aws_cdk import aws_iotevents as iotevents
import aws_cdk.aws_sns as sns
import aws_cdk.aws_sns_subscriptions as subscriptions
import lorawan_device_heartbeat_detectormodel


class LorawanConnectivityWatchdogStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ####################################################################################
        # IoT Events

        # IoT Events: Execution role
        iot_events_execution_role = iam.Role(self, "IoTEventsExecutionRole", assumed_by=iam.ServicePrincipal("iotevents.amazonaws.com"))
        iot_events_execution_role.add_to_policy(iam.PolicyStatement(
            resources=["*"],
            actions=["iot:Publish"]
        ))

        # iot_events_execution_role.add_to_policy(iam.PolicyStatement(
        #     resources=["*"],
        #     actions=["SNS:Publish"]
        # ))

        # IoT Events: Input
        inputDefinitionProperty = iotevents.CfnInput.InputDefinitionProperty(
            attributes=[{"jsonPath": "deviceid"},
                        {"jsonPath": "timestamp_ms"}]
        )

        iot_events_input = iotevents.CfnInput(self, "LoRaWANDeviceWatchdogInput",
                                              input_definition=inputDefinitionProperty,
                                              input_name="LoRaWANDeviceWatchdogInput",
                                              input_description="Input for connectivity status updates for LoRaWAN devices"

                                              )
        # IoT Events: Detector Model
        lorawan_device_heartbeat_detectormodel_definition = iotevents.CfnDetectorModel.DetectorModelDefinitionProperty(
            initial_state_name=lorawan_device_heartbeat_detectormodel.initial_state_name,
            states=lorawan_device_heartbeat_detectormodel.get_states(self))


        iot_events_model_1 = iotevents.CfnDetectorModel(self, "LoRaWANDeviceHeartbeatWatchdogModel",
                                                      detector_model_definition=lorawan_device_heartbeat_detectormodel_definition,
                                                      detector_model_name="LoRaWANDeviceHeartbeatWatchdogModel",
                                                      detector_model_description="Detector model for LoRaWAN device heartbeat",
                                                      key="deviceid",
                                                      evaluation_method="BATCH",
                                                      role_arn=iot_events_execution_role.role_arn)

        

    
        ####################################################################################
        # SNS topic
        sns_topic = sns.Topic(self, "LoRaWANDeviceNotificationTopic",
                              display_name="Topic to use for notifications about LoRaWAN device events",
                              topic_name="LoRaWANDeviceNotificationTopic"
                              )

        email_address = cdk.CfnParameter(self, "emailforalarms")
        sns_topic.add_subscription(subscriptions.EmailSubscription(email_address.value_as_string))

        ####################################################################################
        # CloudFormation Stack outputs

        # cdk.CfnOutput(
        #     self, "StateMachineARN",
        #     value=gateway_watchdog_state_machine.state_machine_arn,
        #     description="Please run 'aws stepfunctions start-execution --state-machine-arn  <LorawanConnectivityWatchdogStack.StateMachineARN>' to start the monitoring of LoRaWAN gateway connectivity",

        # )

        # cdk.CfnOutput(
        #     self, "StateMachineStartCommand",
        #     value='aws stepfunctions start-execution --state-machine-arn ' + gateway_watchdog_state_machine.state_machine_arn,
        #     description="Please run this command to start the monitoring of LoRaWAN gateway connectivity",
        # )

        # cdk.CfnOutput(
        #     self, "StateMachineStopommand",
        #     value='aws stepfunctions stop-execution --state-machine-arn ' + gateway_watchdog_state_machine.state_machine_arn,
        #     description="Please run this command to stop the monitoring of LoRaWAN gateway connectivity",
        # )
