#!/usr/bin/env python3
""" A CDK object for the application stack """

import aws_cdk as cdk

from aws_cdk import (
    aws_certificatemanager as acm,
    aws_s3 as s3,
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_autoscaling as asg,
    aws_elasticloadbalancingv2 as alb,
    aws_route53 as r53,
    aws_route53_targets as r53_targets,
    aws_ssm as ssm,
    Stack,
    Duration,
)
from constructs import Construct


class ApplicationStack(Stack):
    """
    A class to represent the CDK Application resources
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        props,
        net_props,
        hz_props,
        rds_props,
        **kwargs,
    ) -> None:

        super().__init__(scope, construct_id, **kwargs)
