#!/usr/bin/env python3
""" A CDK object for the Hosted Zone stack """

from aws_cdk import (
    aws_route53 as r53,
    aws_certificatemanager as acm,
    aws_ssm as ssm,
    Stack,
)
from constructs import Construct


class HostedZoneStack(Stack):
    """
    A class to represent the CDK Hosted Zone resources
    """

    def __init__(
        self, scope: Construct, construct_id: str, props, **kwargs
    ) -> None:

        super().__init__(scope, construct_id, **kwargs)
