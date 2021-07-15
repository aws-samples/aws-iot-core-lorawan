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
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_iotevents as iotevents
from aws_cdk import aws_stepfunctions as sfn
from aws_cdk import aws_stepfunctions_tasks as tasks
import aws_cdk.aws_sns as sns
import aws_cdk.aws_sns_subscriptions as subscriptions
import lorawan_gateway_monitoring_detectormodel


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
        iot_events_execution_role.add_to_policy(iam.PolicyStatement(
            resources=["*"],
            actions=["SNS:Publish"]
        ))

        # IoT Events: Input
        inputDefinitionProperty = iotevents.CfnInput.InputDefinitionProperty(
            attributes=[{"jsonPath": "gatewayid"},
                        {"jsonPath": "last_uplink_received_timestamp_ms"},
                        {"jsonPath": "last_connection_status"},
                        {"jsonPath": "timestamp_iso8601"}]
        )

        iot_events_input = iotevents.CfnInput(self, "LoRaWANGatewayConnectivityStatusInput",
                                              input_definition=inputDefinitionProperty,
                                              input_name="LoRaWANGatewayConnectivityStatusInput",
                                              input_description="Input for connectivity status updates for LoRaWAN gateways"

                                              )
        # IoT Events: Detector Model
        detector_model_definition = iotevents.CfnDetectorModel.DetectorModelDefinitionProperty(
            initial_state_name=lorawan_gateway_monitoring_detectormodel.initial_state_name,
            states=lorawan_gateway_monitoring_detectormodel.get_states(self))

        iot_events_model = iotevents.CfnDetectorModel(self, "LoRaWANGatewayConnectivityModel",
                                                      detector_model_definition=detector_model_definition,
                                                      detector_model_name="LoRaWANGatewayConnectivityModel",
                                                      detector_model_description="Detector model for LoRaWAN gateway connectivity status",
                                                      key="gatewayid",
                                                      evaluation_method="BATCH",
                                                      role_arn=iot_events_execution_role.role_arn)

        ####################################################################################
        # Lambda function GetWirelessGatewayStatisticsLambda

        # Lambda function GetWirelessGatewayStatisticsLambda: Execution Role
        get_wireless_gateway_statistics_lambda_role = iam.Role(self, "GetWirelessGatewayStatisticsLambdaExecutionRole", assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"))
        get_wireless_gateway_statistics_lambda_role.add_to_policy(iam.PolicyStatement(
            resources=["arn:aws:iotwireless:" + self.region + ":" + self.account + ":WirelessGateway/*"],
            actions=["iotwireless:ListWirelessGateways", "iotwireless:GetWirelessGatewayStatistics"]
        ))
        get_wireless_gateway_statistics_lambda_role.add_to_policy(iam.PolicyStatement(
            resources=["arn:aws:iotevents:" + self.region + ":" + self.account + ":input/LoRaWANGatewayConnectivityStatusInput"],
            actions=["iotevents:BatchPutMessage"]
        ))

        # Lambda function GetWirelessGatewayStatisticsLambda: Lambda function configuration
        get_wireless_gateway_statistics_lambda = lambda_.Function(self, "GetWirelessGatewayStatisticsLambda",
                                                                  code=lambda_.Code.asset("src_get_wireless_gateway_statistics_lambda"),
                                                                  runtime=lambda_.Runtime.PYTHON_3_7,
                                                                  handler="lambda.handler",
                                                                  role=get_wireless_gateway_statistics_lambda_role,
                                                                  timeout=cdk.Duration.seconds(25)
                                                                  )

        get_wireless_gateway_statistics_lambda.add_environment("TEST_MODE", "true")

        get_wireless_gateway_statistics_lambda.add_environment("IOT_EVENTS_INPUT_NAME", "LoRaWANGatewayConnectivityStatusInput")

        ####################################################################################
        # SNS topic
        sns_topic = sns.Topic(self, "LoRaWANGatewayNotificationTopic",
                              display_name="Topic to use for notifications about LoRaWAN gateway events like connect or disconnect",
                              topic_name="LoRaWANGatewayNotificationTopic"
                              )

        email_address = cdk.CfnParameter(self, "emailforalarms")
        sns_topic.add_subscription(subscriptions.EmailSubscription(email_address.value_as_string))

        ####################################################################################
        # Step Function

        # State 'Fail'
        failure_state = sfn.Fail(self, "Fail")

        # State 'Wait'
        wait_state = sfn.Wait(self, "Sleep",
                              time=sfn.WaitTime.duration(cdk.Duration.minutes(1))
                              )

        # State 'Ingest gateway connectivity status into IoT Events input'
        lambda_invoke_state = tasks.LambdaInvoke(self,
                                                 "Ingest gateway connectivity status into IoT Events input",
                                                 result_path="$.wireless_gateway_stats",
                                                 lambda_function=get_wireless_gateway_statistics_lambda
                                                 # payload=task_input_payload
                                                 )

        # Stat 'Did IoT events ingestion run successfull?'
        choice_lambda_state = sfn.Choice(self, "Did IoT events ingestion run successfull?")
        choice_lambda_state.when(sfn.Condition.number_equals("$.wireless_gateway_stats.Payload.status", 200), wait_state)
        choice_lambda_state.otherwise(failure_state)

        # Define transitions
        wait_state.next(lambda_invoke_state)
        lambda_invoke_state.next(choice_lambda_state)

        # Crreate a state machine
        gateway_watchdog_state_machine = sfn.StateMachine(
            self,
            "LoRaWANGatewayWatchdogStatemachine",
            definition=lambda_invoke_state,
            state_machine_name="LoRaWANGatewayWatchdogStatemachine"
        )
        ####################################################################################
        # CloudFormation Stack outputs

        cdk.CfnOutput(
            self, "StateMachineARN",
            value=gateway_watchdog_state_machine.state_machine_arn,
            description="Please run 'aws stepfunctions start-execution --state-machine-arn  <LorawanConnectivityWatchdogStack.StateMachineARN>' to start the monitoring of LoRaWAN gateway connectivity",

        )

        cdk.CfnOutput(
            self, "StateMachineStartCommand",
            value='aws stepfunctions start-execution --state-machine-arn ' + gateway_watchdog_state_machine.state_machine_arn,
            description="Please run this command to start the monitoring of LoRaWAN gateway connectivity",
        )

        cdk.CfnOutput(
            self, "StateMachineStopommand",
            value='aws stepfunctions stop-execution --state-machine-arn ' + gateway_watchdog_state_machine.state_machine_arn,
            description="Please run this command to stop the monitoring of LoRaWAN gateway connectivity",
        )
