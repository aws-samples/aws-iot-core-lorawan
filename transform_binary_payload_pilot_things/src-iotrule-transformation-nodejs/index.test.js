const lambda = require('./index')

test_definition = [
    {
        "description": "Test 1",
        "input": "F2XUdQ4=",
        "PayloadDecoderProductId": "69714577-5c18-4931-866a-1026b55c603d",
        "expected_status": 200,
        "expected_output": {
            "temperature": 23.05,
            "humidity": 51.16
        }
    },
    {
        "description": "Test 2",
        "input": "F2XUdQ4=",
        "PayloadDecoderProductId": "not a guid",
        "expected_status": 500,
        "expected_error_message": "PayloadDecoderProductId must be a GUID"
    },

    {
        "description": "Test 3",
        "input": "F2XUdQ4=",
        "PayloadDecoderProductId": "69714577-5c18-4931-866a-1026b55c603z",
        "expected_status": 500,
        "expected_error_message": "PayloadDecoderProductId must be a GUID"
    }


]


for (var i = 0; i < test_definition.length; i++) {

    test_event = {
        "PayloadData": test_definition[i].input,
        "PayloadDecoderProductId": test_definition[i].PayloadDecoderProductId
    }

    console.log(test_event)
    console.log("Running test " + test_definition[i].description)

    async function app(test_definition, i) {

        var actual_output = await lambda.handler(test_event, {})

        // console.log("Binary decoding output=" + JSON.stringify(actual_output, null, " "))
        console.log("---------" + test_definition[i].description + "--------------------------")
        if (actual_output.status != test_definition[i].expected_status) {
            throw ("ERROR: status " + actual_output.status + " received, but " + test_definition[i].expected_status + " expected")
        } else {
            console.log("OK: status code " + actual_output.status)
        }

        if (actual_output.status != 200) {
            if (actual_output.errorMessage != test_definition[i].expected_error_message) {
                throw ("ERROR: error message '" + actual_output.errorMessage + "' received, but '" + test_definition[i].expected_error_message + "' expected")
            } else {
                console.log("OK: error message  " + actual_output.errorMessage)
            }
        }

        for (var key in test_definition[i].expected_output) {
            if (test_definition[i].expected_output[key] == null) {
                console.log("ERROR: attribute " + key + " is undefined in test definition")
                throw "ERROR: attribute " + key + " is undefined in test definition";
            }
            if (test_definition[i].expected_output[key] == actual_output.transformed_payload[key]) {
                console.log("OK: attribute " + key + " has an expected value of " + actual_output.transformed_payload[key])
            } else {
                console.log("ERROR: for attribute " + key + ": expected " + test_definition[i].expected_output[key] + " but received " + actual_output.transformed_payload[key] + ". Dump of actual output:" + JSON.stringify(actual_output) + ", dump of expected output: " + JSON.stringify(test_definition[i].expected_output))
            }

        }
    }


    app(test_definition, i)


}



