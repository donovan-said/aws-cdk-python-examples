#!/usr/bin/env python3

""" A CDK object for the Lambda AMI stack """

from pathlib import Path

from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
)
from constructs import Construct


class AmiLambdaStack(Stack):
    """
    A class to represent the Lambda AMI CDK resources
    """

    def __init__(
        self, scope: Construct, construct_id: str, props, **kwargs
    ) -> None:

        super().__init__(scope, construct_id, **kwargs)

        lambda_function_name = (
            f"{props['account_alias'].lower()}-ami-refresh-lambda-function"
        )

        """
        Roles are prevented from being created without the below Permissions
        Boundary being attached.
        """

        permissions_boundary = iam.ManagedPolicy.from_managed_policy_name(
            self,
            "Permissions-Boundary",
            f"{props['account_alias']}-TBC",
        )

        lambda_role = iam.Role(
            self,
            "Role",
            role_name=(
                f"{props['account_alias'].lower()}-ami-refresh-lambda-role"
            ),
            description="The IAM Role used by AMI ",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            permissions_boundary=permissions_boundary,
        )

        iam.ManagedPolicy(
            self,
            "Policy",
            managed_policy_name=(
                f"{props['account_alias'].lower()}-ami-refresh-lambda-policy"
            ),
            description="Adhoc access for the service.",
            statements=[
                iam.PolicyStatement(
                    sid="Ec2Describe",
                    actions=[
                        "ec2:DescribeInstances",
                        "ec2:DescribeImages",
                        "ec2:DescribeTags",
                        "ec2:DescribeSnapshots",
                    ],
                    resources=["*"],
                ),
                iam.PolicyStatement(
                    sid="SsmDescribe",
                    actions=["ssm:DescribeParameters"],
                    resources=["*"],
                ),
                iam.PolicyStatement(
                    sid="SsmPerform",
                    actions=[
                        "ssm:PutParameter",
                        "ssm:DeleteParameter",
                        "ssm:GetParameterHistory",
                        "ssm:GetParametersByPath",
                        "ssm:GetParameters",
                        "ssm:GetParameter",
                        "ssm:DeleteParameters",
                        "ssm:AddTagsToResource",
                    ],
                    resources=[
                        f"arn:aws:ssm:eu-west-2:{props['account_id']}:"
                        f"parameter/{props['account_alias']}/"
                        f"IMAGE/RHEL8/LATEST/AMI_ID",
                    ],
                ),
                iam.PolicyStatement(
                    sid="CloudWatchLogGroup",
                    actions=["logs:CreateLogGroup"],
                    resources=[
                        f"arn:aws:logs:{props['region']}:"
                        f"{props['account_id']}:*"
                    ],
                ),
                iam.PolicyStatement(
                    sid="CloudWatchLogStream",
                    actions=["logs:CreateLogStream", "logs:PutLogEvents"],
                    resources=[
                        f"arn:aws:logs:{props['region']}:{props['account_id']}:"
                        f"log-group:/aws/lambda/{lambda_function_name}:*"
                    ],
                ),
            ],
            roles=[lambda_role],
        )

        with open(
            Path.cwd() / "stacks/src/lambda_handler.py", encoding="utf8"
        ) as fp:
            handler_code = fp.read()

        lambda_function = _lambda.Function(
            self,
            "AMI-Lambda-Function",
            function_name=lambda_function_name,
            description=(
                "A lambda function to query for the latest RHEL8 AMI and "
                "update the SSM parameter."
            ),
            role=lambda_role,
            code=_lambda.InlineCode(handler_code),
            handler="index.lambda_handler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            timeout=Duration.seconds(180),
            environment={
                "ACCOUNT_ALIAS": f"{props['account_alias']}",
                "AMI_NAME": "TBC",
                "REGION": f"{props['region']}",
            },
        )

        """
        Run every day at 11PM UTC
        Cron "0 23 * * ? *"
        """

        rule = events.Rule(
            self,
            "Rule",
            schedule=events.Schedule.cron(
                minute="0", hour="23", month="*", year="*"
            ),
        )
        rule.add_target(targets.LambdaFunction(lambda_function))
