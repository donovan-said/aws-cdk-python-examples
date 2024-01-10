#!/usr/bin/env python3
""" A CDK object for the App CodeDeploy stack """

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
    A class to represent the APP CDK CodeDeploy resources
    """

    def __init__(
        self, scope: Construct, construct_id: str, props, **kwargs
    ) -> None:

        super().__init__(scope, construct_id, **kwargs)

        """
        Roles are prevented from being created without the below Permissions
        Boundary being attached.
        """

        permissions_boundary = iam.ManagedPolicy.from_managed_policy_name(
            self,
            "Permissions-Boundary",
            f"{props['account_alias']}-TBC",
        )

        iam_role = iam.Role(
            self,
            "Role",
            role_name=(
                f"{props['account_alias'].lower()}-app-code-deploy-role"
            ),
            description=(
                "The IAM Role used by CodeDeploy for deployments to the "
                "App ASG."
            ),
            assumed_by=iam.ServicePrincipal("codedeploy.amazonaws.com"),
            permissions_boundary=permissions_boundary,
        )

        iam_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AWSCodeDeployDeployerAccess"
            )
        )

        iam_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSCodeDeployRole"
            )
        )

        cd_app = cd.ServerApplication(
            self,
            "Application",
            application_name=(
                f"{props['account_alias'].lower()}-app-code-deploy-"
                f"application"
            ),
        )

        """
        SSM Parameter store is being used to avoid circular dependencies
        inherent in CDK Outputs.
        """

        asg_name = ssm.StringParameter.from_string_parameter_name(
            self,
            "ASG-Full-Name",
            f"/{props['account_alias']}/App/AppStack/ASG/NAME",
        ).string_value

        app_asg = asg.AutoScalingGroup.from_auto_scaling_group_name(
            self, "AutoScalingGroup", asg_name
        )

        """
        We're not using the "load_balancer" attribute, as this causes the
        specified Target Group to "drain", which is what we would want if this
        was a Blue/Green deployment via a new host, though we're performing an
        in-place deployment, i.e. deploying the new revision to the existing
        host.
        """

        cd.ServerDeploymentGroup(
            self,
            "Deployment-Group",
            deployment_group_name=(
                f"{props['account_alias'].lower()}-app-code-deploy-"
                f"deployment-group"
            ),
            application=cd_app,
            role=iam_role,
            deployment_config=cd.ServerDeploymentConfig.ALL_AT_ONCE,
            auto_scaling_groups=[app_asg],
            install_agent=False,
        )
