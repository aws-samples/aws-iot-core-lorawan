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

import boto3
import json
import os
import logging

# Define the allowed values of SEARCH_TYPE environment variable
# Lookup the Thing associated to Wireless Device
# https://docs.aws.amazon.com/iot-wireless/2020-11-22/apireference/API_AssociateWirelessDeviceWithThing.html
SEARCH_TYPE_ASSOCIATED_THING = "ASSOCIATED_THING"
# Lookup the Thing by search of IoT thing index
# https://docs.aws.amazon.com/iot/latest/developerguide/managing-index.html
SEARCH_TYPE_THING_INDEX = "THING_INDEX"


# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Ipnut parameter validaton
if not "SEARCH_TYPE" in os.environ:
    raise Exception("Missing environment variable 'SEARCH_TYPE'")

PARAM_SEARCH_TYPE = os.environ.get('SEARCH_TYPE')

if not PARAM_SEARCH_TYPE in [SEARCH_TYPE_ASSOCIATED_THING, SEARCH_TYPE_THING_INDEX]:
    raise Exception("Environment varialble 'SEARCH_TYPE' can only have values %s or %s, but received %s" % (
        SEARCH_TYPE_ASSOCIATED_THING, SEARCH_TYPE_THING_INDEX, PARAM_SEARCH_TYPE))

if PARAM_SEARCH_TYPE == SEARCH_TYPE_THING_INDEX:
    if not "SEARCH_THING_ATTRIBUTENAME" in os.environ:
        raise Exception(
            "Missing environment variable 'SEARCH_THING_ATTRIBUTENAME'")

    PARAM_SEARCH_THING_ATTRIBUTE = os.environ.get('SEARCH_THING_ATTRIBUTENAME')

PARAM_OUTPUT_ATTRIBUTE_NAME = "ThingName"

client_iot = boto3.client("iot")
client_iotwireless = boto3.client("iotwireless")


# In this example, we will implement a caching of AWS IoT index searches
# in a prototypical and non production-ready way for a sake of simplicity.
# For a production environment it should be rearchitected.
thing_name_cache = {}


def lambda_handler(event, context):
    """ Determines a thing name based on an attribute of LoRAWAN message (e.g. WirelessDeviceId)
        Parameters (as event attributes)
        ----------
        searchvalue : str
            value that will be used for a lookup of thing name

        Environment variable
        ----------------
        SEARCH_TYPE : str
            Can have values "ASSOCIATED_THING" or "THING_INDEX"

            If value "ASSOCIATED_THING" is provided, input must be a AWS IoT Core for LoRaWAN WirelessDeviceId The function will return the name of the thing associated to a specified WirelessDeviceId.

            If value "THING_INDEX" is provided, an additional environment variable SEARCH_THING_ATTRIBUTENAME must be specified. This function will perform a search in the IoT registry for an attribute named as SEARCH_THING_ATTRIBUTENAME, and match for the value of the input "searchvalue".


        Returns
        -------
        This function returns a JSON object with the following keys:

        ThingName : str
            Name of AWS IoT Thing

        Error handling
        -------
        This function will raise an Exception in case of an error

    """

    global thing_name_cache
    logger.info("Received event: %s" % json.dumps(event))

    # Get the search value (for example, if using 'WirelessDeviceId' as a search attribute,
    # the search value would be like 8b00de4a-0fac-407b-93e6-8c59fd411f16")
    if not "searchvalue" in event:
        raise Exception("Missing event attribute 'searchvalue'")
    search_value = event.get("searchvalue")
    thing_name = None

    # If thing name is cached, return the value stored in cache
    if thing_name_cache.get(search_value, None) != None:
        thing_name = thing_name_cache.get(search_value)
        logger.info("Found value [%s] for key [%s] in cache" % (
            thing_name, search_value))
    # If search type is ASSOCIATED_THING, invoke AWS IoT Core for LoRaWAN API to retrieve a thing associated
    # with this device (see https://docs.aws.amazon.com/iot-wireless/2020-11-22/apireference/API_AssociateWirelessDeviceWithThing.html)
    elif PARAM_SEARCH_TYPE == SEARCH_TYPE_ASSOCIATED_THING:

        logger.info("Query associated thing for id: %s" % search_value)

        thing_name = client_iotwireless.get_wireless_device(
            Identifier=search_value,
            IdentifierType='WirelessDeviceId'
        ).get("ThingName")

        thing_name_cache[search_value] = thing_name
    # If search type is THING_INDEX, invoke AWS IoT Core API to retrieve a Thing based on attribute name
    # (see https://docs.aws.amazon.com/iot/latest/apireference/API_SearchIndex.html)
    elif PARAM_SEARCH_TYPE == SEARCH_TYPE_THING_INDEX:
        # Build a query string
        # (see details at https://docs.aws.amazon.com/iot/latest/developerguide/example-queries.html)
        query_string = "attributes."+PARAM_SEARCH_THING_ATTRIBUTE+":" + search_value
        logger.info("Query string: %s" % query_string)

        # Invoke the index search
        search_result = client_iot.search_index(
            indexName='AWS_Things',
            queryString=query_string
        ).get("things")

        # Error handling
        if (len(search_result) == 0):
            raise Exception(
                "Error, query [%s] did not return any results" % query_string)

        if (len(search_result) > 1):
            raise Exception(
                "Error, query [%s] returned more the one result" % query_string)

        # Extract the name of AWS IoT Thing
        thing_name = search_result[0].get("thingName")
        thing_name_cache[search_value] = thing_name
    else:
        raise Exception("Unsupported search type: [%s]" % PARAM_SEARCH_TYPE)

    logger.info("Thing name is: %s" % thing_name)

    return {PARAM_OUTPUT_ATTRIBUTE_NAME: thing_name}
