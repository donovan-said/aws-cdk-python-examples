#!/usr/bin/env python3
""" A CDK object for the storage stack """

import aws_cdk as cdk

from aws_cdk import (
    aws_kms as kms,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_iam as iam,
    aws_ssm as ssm,
    RemovalPolicy,
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
