#!/usr/bin/env python3

"""
A Lambda function to query the latest AMI and update an SSM Parameter for
consumption by the Launch Templates of the services.
"""

import os
import boto3
from botocore.exceptions import ClientError

# Setting up logging
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Lambda function environment variables
ACCOUNT_ALIAS = os.environ["ACCOUNT_ALIAS"]
AMI_NAME = os.environ["AMI_NAME"]
REGION = os.environ["REGION"]


def query_latest_ami():
    """
    A function to query for the latest AMI ID of a given AMI name prefix.

    :return: The AMI ID
    """

    ec2 = boto3.client("ec2", region_name=REGION)

    try:
        response = ec2.describe_images(
            Filters=[
                {"Name": "name", "Values": [AMI_NAME]},
                {"Name": "state", "Values": ["available"]},
                {"Name": "image-type", "Values": ["machine"]},
            ]
        )

        images = response["Images"]

        sorted_images = sorted(images, key=lambda k: k["Name"])

        # The latest AMI will be the last object in the list as it has a
        # timestamp associated with it.
        latest_image = sorted_images[-1]

        ami_id = latest_image["ImageId"]

        logger.info(f">> The latest AMI ID is: {ami_id}.")
    except ClientError as err:
        logger.error(f">> Error describing images: {err}")
        raise

    return ami_id


def ssm_parameter_create(ami):
    """
    A function to update the SSM parameter with the latest AMI ID value
    provided.

    :param ami: An AMI ID
    :return: null
    """

    ssm_param = f"/{ACCOUNT_ALIAS}/IMAGE/RHEL8/LATEST/AMI_ID"

    logger.info(
        f">> Updating SSM Parameter: {ssm_param} with latest AMI ID: {ami}."
    )

    ssm = boto3.client("ssm", region_name=REGION)

    try:
        ssm.put_parameter(
            Name=ssm_param,
            Description=(
                "An SSM Parameter to store the latest RHEL8 AMI ID supplied by "
                "the Lambda stack."
            ),
            Overwrite=True,
            Value=ami,
            Type="String",
            DataType="aws:ec2:image",
        )
        logger.info(
            f">> Successfully updated SSM Parameter: {ssm_param} with latest AMI "
            f"ID: {ami}."
        )
    except ClientError as err:
        logger.error(f"Error putting parameter: {err}")
        raise


def lambda_handler(event, context):
    """
    Lambda entrypoint
    """

    logger.info(f">> Lambda function has been invoked by: {event}")

    ami_id = query_latest_ami()
    ssm_parameter_create(ami_id)
