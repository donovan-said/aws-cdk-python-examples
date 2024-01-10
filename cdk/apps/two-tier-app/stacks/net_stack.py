#!/usr/bin/env python3
""" A CDK object for the network stack """

from aws_cdk import aws_ec2 as ec2, aws_ssm as ssm, Stack
from constructs import Construct


class NetworkStack(Stack):
    """
    A class to represent the CDK Network resources
    """

    def __init__(
        self, scope: Construct, construct_id: str, props, **kwargs
    ) -> None:

        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc.from_lookup(
            self, "VPC", vpc_id=props["vpc_id"], is_default=False
        )

        """
        SSM Parameter store is being used to avoid circular dependencies
        inherent in CDK Outputs.
        """

        ssm_values = {
            "VPC/CIDR": vpc.vpc_cidr_block,
            "VPC/PRIVATE/SUBNET": vpc.private_subnets,
            "VPC/PUBLIC/SUBNET": vpc.public_subnets,
        }

        for ssm_k, ssm_v in ssm_values.items():
            ssm.StringParameter(
                self,
                f"SSM-Parameter-{ssm_k}",
                parameter_name=(
                    f"/{props['account_alias']}/APP/NET/STACK/{ssm_k}"
                ),
                string_value=ssm_v,
            )
