# See https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-cdk-getting-started.html 
# for guidelines to install aws-sam-cli-beta-cdk.
# Mac OS:
# brew install aws-sam-cli-beta-cdk.
sam-beta-cdk local invoke LorawanConnectivityWatchdogStack/GetWirelessGatewayStatisticsLambda -e $1