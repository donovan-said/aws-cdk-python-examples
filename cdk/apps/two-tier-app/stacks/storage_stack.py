#!/usr/bin/env python3
""" A CDK object for the storage stack """

import aws_cdk as cdk

from aws_cdk import (
    aws_s3 as s3,
    aws_ssm as ssm,
    Stack,
    Duration,
)
from constructs import Construct


class StorageStack(Stack):
    """
    A class to represent the CDK storage resources
    """

    def __init__(
        self, scope: Construct, construct_id: str, props, **kwargs
    ) -> None:

        super().__init__(scope, construct_id, **kwargs)

        """
        S3 Bucket used to store application and CodeDeploy binaries
        """

        config_bucket = s3.Bucket(
            self,
            "Config-S3-Bucket",
            bucket_name=(
                f"{props['account_alias'].lower()}-"
                f"{props['config_bucket_name']}-"
                f"{props['region']}"
            ),
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        """
        S3 Bucket used to store infrastructure logs
        """

        logging_bucket = s3.Bucket(
            self,
            "Logging-S3-Bucket",
            bucket_name=(
                f"{props['account_alias'].lower()}-"
                f"{props['logging_bucket_name']}-"
                f"{props['region']}"
            ),
            encryption=s3.BucketEncryption.S3_MANAGED,
            lifecycle_rules=[s3.LifecycleRule(expiration=Duration.days(30))],
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        """
        SSM Parameter store is being used to avoid circular dependencies
        inherent in CDK Outputs.
        """

        ssm_values = {
            "S3/CONFIG/ARN": config_bucket.bucket_arn,
            "S3/LOGGING/ARN": logging_bucket.bucket_arn,
        }

        for ssm_k, ssm_v in ssm_values.items():
            ssm.StringParameter(
                self,
                f"SSM-Parameter-{ssm_k}",
                parameter_name=(
                    f"/{props['account_alias']}/APP/STORAGE/STACK/{ssm_k}"
                ),
                string_value=ssm_v,
            )
