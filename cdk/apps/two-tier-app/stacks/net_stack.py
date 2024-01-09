#!/usr/bin/env python3
""" A CDK object for the network stack """

from aws_cdk import aws_ec2 as ec2, CfnOutput, Stack
from constructs import Construct


class NetworkStack(Stack):
    """
    A class to represent the CDK Network resources
    """

    def __init__(
        self, scope: Construct, construct_id: str, props, **kwargs
    ) -> None:

        super().__init__(scope, construct_id, **kwargs)
