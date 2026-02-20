"""
Start Pipeline Lambda Handler
===============================

POST /pipeline — Starts the Step Functions interview intelligence pipeline.
GET /pipeline/{executionId} — Checks pipeline execution status.

Triggers the end-to-end pipeline: scrape → parse → analyze → generate.
Returns the execution ARN for status tracking.

POST Request Body:
    {
        "companyName": "GridFlex Energy",
        "companyUrl": "https://gridflex.com" (optional),
        "documents": ["s3://bucket/key.docx"] (optional)
    }

POST Response:
    200: {"executionArn": "arn:...", "status": "RUNNING"}

GET Response:
    200: {"executionArn": "arn:...", "status": "SUCCEEDED|RUNNING|FAILED"}
"""

import os
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

from shared.response_helpers import success_response, error_response, parse_body

import boto3


def lambda_handler(event: dict, context) -> dict:
    """
    Lambda handler for starting or checking the interview pipeline.

    Routes to start_pipeline (POST) or get_status (GET) based on
    the HTTP method.

    Args:
        event: API Gateway Lambda proxy event.
        context: Lambda context object.

    Returns:
        dict: API Gateway response with execution details.
    """
    http_method = event.get("httpMethod", "POST")

    if http_method == "GET":
        return _get_pipeline_status(event)
    else:
        return _start_pipeline(event)


def _start_pipeline(event: dict) -> dict:
    """
    Start a new Step Functions pipeline execution.

    Creates an interview session and triggers the full intelligence
    pipeline as a state machine execution.

    Args:
        event: API Gateway Lambda proxy event.

    Returns:
        dict: Response with execution ARN and status.
    """
    try:
        body = parse_body(event)
    except (ValueError, Exception) as e:
        return error_response(f"Invalid request body: {e}", 400)

    company_name = body.get("companyName")
    if not company_name:
        return error_response("companyName is required", 400)

    state_machine_arn = os.environ.get("STATE_MACHINE_ARN")
    if not state_machine_arn:
        return error_response("Pipeline not configured (STATE_MACHINE_ARN missing)", 500)

    try:
        sfn_client = boto3.client("stepfunctions")

        pipeline_input = {
            "companyName": company_name,
            "companyUrl": body.get("companyUrl", ""),
            "documents": body.get("documents", []),
        }

        response = sfn_client.start_execution(
            stateMachineArn=state_machine_arn,
            input=json.dumps(pipeline_input),
        )

        execution_arn = response["executionArn"]
        execution_id = execution_arn.split(":")[-1]

        result = {
            "executionArn": execution_arn,
            "executionId": execution_id,
            "status": "RUNNING",
            "companyName": company_name,
        }

        logger.info("Pipeline started: %s for %s", execution_id, company_name)
        return success_response(result)

    except Exception as e:
        logger.error("Failed to start pipeline: %s", e)
        return error_response("Failed to start pipeline", 500, str(e))


def _get_pipeline_status(event: dict) -> dict:
    """
    Check the status of a running pipeline execution.

    Args:
        event: API Gateway Lambda proxy event with executionId path param.

    Returns:
        dict: Response with execution status and output if complete.
    """
    execution_id = event.get("pathParameters", {}).get("executionId")
    if not execution_id:
        return error_response("executionId path parameter is required", 400)

    state_machine_arn = os.environ.get("STATE_MACHINE_ARN", "")

    try:
        sfn_client = boto3.client("stepfunctions")

        # List executions to find the one matching our ID
        # The execution ARN includes the state machine ARN + execution name
        execution_arn = f"{state_machine_arn.replace(':stateMachine:', ':execution:')}:{execution_id}"

        response = sfn_client.describe_execution(executionArn=execution_arn)

        result = {
            "executionArn": response["executionArn"],
            "executionId": execution_id,
            "status": response["status"],
            "startDate": response["startDate"].isoformat(),
        }

        if response["status"] in ("SUCCEEDED",):
            result["output"] = json.loads(response.get("output", "{}"))
        elif response["status"] in ("FAILED", "TIMED_OUT", "ABORTED"):
            result["error"] = response.get("error", "Unknown error")
            result["cause"] = response.get("cause", "")

        logger.info("Pipeline %s status: %s", execution_id, response["status"])
        return success_response(result)

    except Exception as e:
        logger.error("Failed to get pipeline status: %s", e)
        return error_response("Failed to get pipeline status", 500, str(e))
