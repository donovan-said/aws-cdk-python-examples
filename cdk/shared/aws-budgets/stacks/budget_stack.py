#!/usr/bin/env python3
""" A CDK object for the Budget stack """

from aws_cdk import (
    aws_sns as sns,
    aws_iam as iam,
    aws_budgets as budgets,
    Stack,
)
from constructs import Construct


class BudgetStack(Stack):
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
            topic_name=f"{props['account_alias'].lower()}-budget-sns-topic",
            display_name=(f"{props['account_alias'].lower()}-budget-sns-topic"),
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
        Budget:

        The following is a Budget and Alarm that monitor the cost associated
        with an account. Once the budget crosses the 80% threshold an alert will
        be raised.

        N.b The L1 CFN construct is used here, as an L2 construct doesn't exist
        for AWS Budgets.
        """

        budgets.CfnBudget(
            self,
            "Budget",
            budget=budgets.CfnBudget.BudgetDataProperty(
                budget_name=(
                    f"{props['account_alias']}-monthly-budget-notification"
                ),
                budget_type="COST",
                time_unit="MONTHLY",
                budget_limit=budgets.CfnBudget.SpendProperty(
                    amount=props["budget_threshold"], unit="USD"
                ),
            ),
            notifications_with_subscribers=[
                budgets.CfnBudget.NotificationWithSubscribersProperty(
                    notification=budgets.CfnBudget.NotificationProperty(
                        comparison_operator="GREATER_THAN",
                        notification_type="ACTUAL",
                        threshold=80,
                        threshold_type="PERCENTAGE",
                    ),
                    subscribers=[
                        budgets.CfnBudget.SubscriberProperty(
                            address=app_sns.topic_arn, subscription_type="SNS"
                        )
                    ],
                )
            ],
        )
