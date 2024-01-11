#!/usr/bin/env python3
""" A CDK object for the App monitoring stack """

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
    A class to represent the App CDK monitoring resources
    """

    def __init__(
        self, scope: Construct, construct_id: str, props, **kwargs
    ) -> None:

        super().__init__(scope, construct_id, **kwargs)

        """
        SNS Topic:

        The follow is the SNS Topic which will be used by the various alerts
        defined in this stack.
        """

        app_sns = sns.Topic(
            self,
            "SNS",
            topic_name=f"{props['account_alias'].lower()}-app-sns-topic",
            display_name=(f"{props['account_alias'].lower()}-app-sns-topic"),
        )

        topic_policy = sns.TopicPolicy(self, "TopicPolicy", topics=[app_sns])

        topic_policy.document.add_statements(
            iam.PolicyStatement(
                sid="AllowAllInAccount",
                actions=[
                    "SNS:GetTopicAttributes",
                    "SNS:SetTopicAttributes",
                    "SNS:AddPermission",
                    "SNS:RemovePermission",
                    "SNS:Subscribe",
                    "SNS:ListSubscriptionsByTopic",
                    "SNS:Publish",
                ],
                principals=[iam.AnyPrincipal()],
                resources=[app_sns.topic_arn],
            )
        )

        sns.Subscription(
            self,
            "Subscription",
            topic=app_sns,
            endpoint=props["slack_email"],
            protocol=sns.SubscriptionProtocol.EMAIL,
        )

        """
        ALB Target Group Alerts:

        The following is a CloudWatch Alarm that monitors for unhealthy hosts
        associated with an ALB Target Group.
        """

        alb_full_name = ssm.StringParameter.from_string_parameter_name(
            self,
            f"SSM-ALB-Full-Name",
            f"/{props['account_alias']}/" f"App/AppStack/ALB/NAME",
        ).string_value

        tg_full_name = ssm.StringParameter.from_string_parameter_name(
            self,
            "HTTP-TG-Full-Name",
            f"/{props['account_alias']}/" f"App/AppStack/TG/HTTP/NAME",
        ).string_value

        http_tg_cw_alarm = cw.Alarm(
            self,
            "TG_HTTP_Host_Unhealthy",
            alarm_name=(f"{props['account_alias'].lower()}-app-http-tg-alarm"),
            alarm_description="The HTTP Target Group is in an unhealthy state.",
            metric=cw.Metric(
                metric_name="HealthyHostCount",
                namespace="AWS/ApplicationELB",
                dimensions_map={
                    "LoadBalancer": alb_full_name,
                    "TargetGroup": tg_full_name,
                },
                statistic="Average",
                period=cdk.Duration.minutes(1),
            ),
            comparison_operator=cw.ComparisonOperator.LESS_THAN_THRESHOLD,
            threshold=1,
            evaluation_periods=1,
        )

        http_tg_cw_alarm.add_alarm_action(cw_actions.SnsAction(app_sns))

        """
        Certificate Alerts:

        The following are a collection of EventBridge Rules that listen for
        specific events relating to the ECDSA and RSA certificates.
        """

        rsa_cert_arn = ssm.StringParameter.from_string_parameter_name(
            self,
            "RSA-Cert-ARN",
            f"/{props['account_alias']}/" f"App/HzStack/CERT/RSA/ARN",
        ).string_value

        ecdsa_cert_arn = ssm.StringParameter.from_string_parameter_name(
            self,
            "ECDSA-Cert-ARN",
            f"/{props['account_alias']}/App/HzStack/CERT/ECDSA/ARN",
        ).string_value

        events.Rule(
            self,
            "Cert-Renewal-Approaching-Expiration",
            rule_name=(
                f"{props['account_alias'].lower()}-app-acm-approaching-"
                f"expiration"
            ),
            description=(
                "This rule listens for ACM events indicating an approaching "
                "certificate expiration."
            ),
            targets=[targets.SnsTopic(app_sns)],
            event_pattern=events.EventPattern(
                source=["aws.acm"],
                detail_type=["ACM Certificate Approaching Expiration"],
                resources=[rsa_cert_arn, ecdsa_cert_arn],
            ),
        )

        events.Rule(
            self,
            "Cert-Renewal-Expired",
            rule_name=(f"{props['account_alias'].lower()}-app-acm-expired"),
            description=(
                "This rule listens for ACM events indicating a certificate "
                "expiration."
            ),
            targets=[targets.SnsTopic(app_sns)],
            event_pattern=events.EventPattern(
                source=["aws.acm"],
                detail_type=["ACM Certificate Expired"],
                resources=[rsa_cert_arn, ecdsa_cert_arn],
            ),
        )

        events.Rule(
            self,
            "Cert-Renewal-Action-Required",
            rule_name=(
                f"{props['account_alias'].lower()}-app-acm-action-required"
            ),
            description=(
                "This rule listens for ACM events indicating that a user "
                "action is required."
            ),
            targets=[targets.SnsTopic(app_sns)],
            event_pattern=events.EventPattern(
                source=["aws.acm"],
                detail_type=["ACM Certificate Renewal Action Required"],
                resources=[rsa_cert_arn, ecdsa_cert_arn],
            ),
        )
