#!/usr/bin/env python3

import os

import aws_cdk as cdk

from stacks.budget_stack import BudgetStack


app = cdk.App()

# Get environment variables
PIPELINE_RUN_ID = os.getenv("PIPELINE_RUN_ID")
BRANCH_NAME = os.getenv("BRANCH_NAME")
COMMIT_ID = os.getenv("COMMIT_ID")
ENVIRONMENT = os.getenv("CDK_ENVIRONMENT")

props = {
    "environment": ENVIRONMENT,
    "account_alias": app.node.try_get_context("account")[ENVIRONMENT][
        "account_alias"
    ],
    "account_id": app.node.try_get_context("account")[ENVIRONMENT][
        "account_id"
    ],
    "region": app.node.try_get_context("account")[ENVIRONMENT]["region"],
    "budget_stack_name": app.node.try_get_context("stack")["budget_stack"][
        "name"
    ],
    "budget_stack_description": app.node.try_get_context("stack")[
        "budget_stack"
    ]["description"],
    "asset_bucket_name": app.node.try_get_context("s3")["asset_bucket_name"],
    "budget_threshold": app.node.try_get_context("budget_threshold")[
        ENVIRONMENT
    ]["threshold"],
    "slack_email": app.node.try_get_context("slack_config")[ENVIRONMENT][
        "email"
    ],
    "tags": app.node.try_get_context("tags"),
}

# Setting CDK Environment
cdk_account_info = cdk.Environment(
    account=props["account_id"], region=props["region"]
)

budget_stack = BudgetStack(
    app,
    props["budget_stack_name"],
    props,
    env=cdk_account_info,
    description=props["budget_stack_description"],
    stack_name=f"{props['account_alias'].lower()}-{props['budget_stack_name']}",
    synthesizer=cdk.DefaultStackSynthesizer(
        qualifier="{INSERT_QUALIFIER_NAME}",
        file_assets_bucket_name=(
            f"{props['account_alias'].lower()}-{props['asset_bucket_name']}"
        ),
    ),
)

# The static tags are stored in the cdk.context.json file, though here we are
# appending dynamic values to the cdk stack.
tags = app.node.try_get_context("tags")

tags["ado_pipeline_run_id"] = PIPELINE_RUN_ID
tags["branch_name"] = BRANCH_NAME
tags["commit_id"] = COMMIT_ID
tags["environment"] = ENVIRONMENT

# Add a tag to all constructs in all stacks
tagged_stacks = [budget_stack]

for stacks in tagged_stacks:
    for key, value in tags.items():
        cdk.Tags.of(stacks).add(key, value)

app.synth()
