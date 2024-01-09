#!/usr/bin/env python3
""" A CDK object for the CodeDeploy stack """

from aws_cdk import (
    aws_codedeploy as cd,
    aws_iam as iam,
    aws_ssm as ssm,
    aws_autoscaling as asg,
    Stack,
)
from constructs import Construct


class CodeDeployStack(Stack):
    """
    A class to represent the CDK CodeDeploy resources
    """

    def __init__(
        self, scope: Construct, construct_id: str, props, **kwargs
    ) -> None:

        super().__init__(scope, construct_id, **kwargs)
