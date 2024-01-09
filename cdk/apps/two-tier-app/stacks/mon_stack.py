#!/usr/bin/env python3
""" A CDK object for the monitoring stack """

import aws_cdk as cdk

from aws_cdk import (
    aws_sns as sns,
    aws_iam as iam,
    aws_ssm as ssm,
    aws_cloudwatch as cw,
    aws_cloudwatch_actions as cw_actions,
    aws_events as events,
    aws_events_targets as targets,
    Stack,
)
from constructs import Construct


class MonitoringStack(Stack):
    """
    A class to represent the CDK monitoring resources
    """

    def __init__(
        self, scope: Construct, construct_id: str, props, **kwargs
    ) -> None:

        super().__init__(scope, construct_id, **kwargs)
