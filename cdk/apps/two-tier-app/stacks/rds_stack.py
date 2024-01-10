#!/usr/bin/env python3
""" A CDK object for the RDS stack """

import aws_cdk as cdk

from aws_cdk import (
    aws_kms as kms,
    aws_secretsmanager as secret,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_iam as iam,
    aws_ssm as ssm,
    RemovalPolicy,
    Stack,
    Duration,
)
from constructs import Construct


class RDSStack(Stack):
    """
    A class to represent the CDK RDS resources
    """

    def __init__(
        self, scope: Construct, construct_id: str, props, net_props, **kwargs
    ) -> None:

        super().__init__(scope, construct_id, **kwargs)

        """
        The "removal_policy" defaults to retain, i.e. "retain access to data
        that was encrypted with a key that is being retired".
        """

        rds_key = kms.Key(
            self,
            "RDS-KMS",
            alias=f"{props['account_alias'].lower()}-app-rds-key",
            description=(
                "A KMS key to be used by the RDS instance for encryption"
            ),
            enable_key_rotation=True,
        )

        rds_mysql_secret = secret.Secret(
            self,
            "Secret",
            secret_name=f"{props['account_alias'].lower()}-app-rds-secret",
            description=(
                "This secret contains all the RDS attributes required to "
                "connect to the RDS database."
            ),
            generate_secret_string=secret.SecretStringGenerator(
                exclude_characters="\"@/\\ '",
                generate_string_key="password",
                password_length=30,
                secret_string_template='{"username":"admin"}',
            ),
        )

        rds_mysql_credentials = rds.Credentials.from_secret(
            rds_mysql_secret, "admin"
        )

        rds_sg = ec2.SecurityGroup(
            self,
            "RDS-SG",
            vpc=net_props["vpc"],
            description=(
                "A security group to manage traffic for the RDS instance"
            ),
            security_group_name=(
                f"{props['account_alias'].lower()}-app-rds-sg"
            ),
        )

        """
        Adding the tag here, as the Security Group "Name" in the console is
        derived from the tag "Name".
        """

        cdk.Tags.of(rds_sg).add(
            "Name", f"{props['account_alias'].lower()}-app-rds-sg"
        )

        """
        Adds an ingress rule which allows resources in the VPCs CIDR to access
        the database.
        """

        rds_sg.add_ingress_rule(
            peer=ec2.Peer.ipv4(net_props["vpc_cidr_block"]),
            connection=ec2.Port.tcp(3306),
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

        # An IAM Role to be used by RDS for Enhance Monitoring.
        rds_role = iam.Role(
            self,
            "Mon-Role",
            role_name=(
                f"{props['account_alias'].lower()}-"
                f"app-rds-enhanced-monitoring-role"
            ),
            description="The IAM Role used by RDS for enhanced monitoring",
            assumed_by=iam.ServicePrincipal("monitoring.rds.amazonaws.com"),
            permissions_boundary=permissions_boundary,
        )

        # AWS Managed policy required by RDS Enhanced Monitoring
        rds_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AmazonRDSEnhancedMonitoringRole"
            )
        )

        """
        * Password is generated and stored in AWS Secrets Manager
        * performance_insight_retention: Default: 7 this is the free tier
        """

        rds_mysql = rds.DatabaseInstance(
            self,
            "RDS-Instance",
            engine=rds.DatabaseInstanceEngine.mysql(
                version=rds.MysqlEngineVersion.VER_8_0_33
            ),
            database_name="db_name",
            credentials=rds_mysql_credentials,
            instance_identifier=(
                f"{props['account_alias'].lower()}-app-rds-instance"
            ),
            vpc=net_props["vpc"],
            vpc_subnets=ec2.SubnetSelection(
                subnets=net_props["private_subnets"]
            ),
            port=3306,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.MEMORY4,
                ec2.InstanceSize.LARGE,
            ),
            storage_encryption_key=rds_key,
            security_groups=[rds_sg],
            max_allocated_storage=200,
            backup_retention=cdk.Duration.days(7),
            enable_performance_insights=True,
            performance_insight_encryption_key=rds_key,
            # User for Enhanced Monitoring
            monitoring_interval=Duration.seconds(15),
            monitoring_role=rds_role,
            ca_certificate=rds.CaCertificate.of("rds-ca-rsa2048-g1"),
            removal_policy=RemovalPolicy.SNAPSHOT,
        )

        if props["environment"] == "dev":

            ssm_role = iam.Role(
                self,
                "Role",
                role_name=(
                    f"{props['account_alias'].lower()}-app-ssm-rds-"
                    f"management-role"
                ),
                description=(
                    "The IAM Role used by SSM State Manager to Start and Stop "
                    "App RDS instances."
                ),
                assumed_by=iam.ServicePrincipal("ssm.amazonaws.com"),
                permissions_boundary=permissions_boundary,
            )

            ssm_role.add_to_policy(
                iam.PolicyStatement(
                    actions=[
                        "rds:Describe*",
                        "rds:Start*",
                        "rds:Stop*",
                        "rds:Reboot*",
                    ],
                    resources=["arn:aws:rds:eu-west-2:*:db:*"],
                )
            )

            ssm_stop = ssm.CfnAssociation(
                self,
                "SSM-STOP-RDS-Association",
                association_name="App-STOP-RDS-Instance",
                name="AWS-StopRdsInstance",
                apply_only_at_cron_interval=True,
                schedule_expression="cron(30 19 ? * * *)",
            )

            """
            SSM Properties are add via "add_override" as an escape hatch due to
            an issue raised here: https://github.com/aws/aws-cdk/issues/4057
            """

            ssm_stop.add_override(
                "Properties.Parameters.InstanceId",
                [rds_mysql.instance_identifier],
            )
            ssm_stop.add_override(
                "Properties.Parameters.AutomationAssumeRole",
                [ssm_role.role_arn],
            )

            ssm_start = ssm.CfnAssociation(
                self,
                "SSM-START-RDS-Association",
                association_name="App-START-RDS-Instance",
                name="AWS-StartRdsInstance",
                apply_only_at_cron_interval=True,
                schedule_expression="cron(0 6 ? * * *)",
            )

            ssm_start.add_override(
                "Properties.Parameters.InstanceId",
                [rds_mysql.instance_identifier],
            )
            ssm_start.add_override(
                "Properties.Parameters.AutomationAssumeRole",
                [ssm_role.role_arn],
            )

        """
        SSM Parameter store is being used to avoid circular dependencies
        inherent in CDK Outputs.
        """

        ssm_values = {
            "ARN": rds_mysql.instance_arn,
            "SECRET": rds_mysql_secret.secret_name,
        }

        for ssm_k, ssm_v in ssm_values.items():
            ssm.StringParameter(
                self,
                f"SSM-Parameter-{ssm_k}",
                parameter_name=(
                    f"/{props['account_alias']}/APP/RDS/STACK/{ssm_k}"
                ),
                string_value=ssm_v,
            )
