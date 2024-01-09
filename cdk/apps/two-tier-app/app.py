#!/usr/bin/env python3

import os

import aws_cdk as cdk

from stacks.net_stack import NetworkStack
from stacks.hz_stack import HostedZoneStack
from stacks.rds_stack import RDSStack
from stacks.storage_stack import StorageStack
from stacks.app_stack import ApplicationStack
from stacks.mon_stack import MonitoringStack
from stacks.cd_stack import CodeDeployStack

app = cdk.App()

# Get environment variables
PIPELINE_RUN_ID = os.getenv("PIPELINE_RUN_ID")
BRANCH_NAME = os.getenv("BRANCH_NAME")
COMMIT_ID = os.getenv("COMMIT_ID")
ENVIRONMENT = os.getenv("CDK_ENVIRONMENT")

props = {
    "environment": ENVIRONMENT,
    "dev_account_alias": app.node.try_get_context("account")["dev"][
        "account_alias"
    ],
    "uat_account_alias": app.node.try_get_context("account")["uat"][
        "account_alias"
    ],
    "prod_account_alias": app.node.try_get_context("account")["prod"][
        "account_alias"
    ],
    "dev_account_id": app.node.try_get_context("account")["dev"]["account_id"],
    "uat_account_id": app.node.try_get_context("account")["uat"]["account_id"],
    "prod_account_id": app.node.try_get_context("account")["prod"][
        "account_id"
    ],
    "account_alias": app.node.try_get_context("account")[ENVIRONMENT][
        "account_alias"
    ],
    "account_id": app.node.try_get_context("account")[ENVIRONMENT][
        "account_id"
    ],
    "region": app.node.try_get_context("account")[ENVIRONMENT]["region"],
    "net_stack_name": app.node.try_get_context("stack")["net_stack"]["name"],
    "net_stack_description": app.node.try_get_context("stack")["net_stack"][
        "description"
    ],
    "hz_stack_name": app.node.try_get_context("stack")["hz_stack"]["name"],
    "hz_stack_description": app.node.try_get_context("stack")["hz_stack"][
        "description"
    ],
    "rds_stack_name": app.node.try_get_context("stack")["rds_stack"]["name"],
    "rds_stack_description": app.node.try_get_context("stack")["rds_stack"][
        "description"
    ],
    "storage_stack_name": app.node.try_get_context("stack")["storage_stack"][
        "name"
    ],
    "storage_stack_description": app.node.try_get_context("stack")[
        "storage_stack"
    ]["description"],
    "app_stack_name": app.node.try_get_context("stack")["app_stack"]["name"],
    "app_stack_description": app.node.try_get_context("stack")["app_stack"][
        "description"
    ],
    "mon_stack_name": app.node.try_get_context("stack")["mon_stack"]["name"],
    "mon_stack_description": app.node.try_get_context("stack")["mon_stack"][
        "description"
    ],
    "cd_stack_name": app.node.try_get_context("stack")["cd_stack"]["name"],
    "cd_stack_description": app.node.try_get_context("stack")["cd_stack"][
        "description"
    ],
    "asset_bucket_name": app.node.try_get_context("s3")["asset_bucket_name"],
    "vpc_id": app.node.try_get_context("vpc")[ENVIRONMENT]["vpc_id"],
    "domain_name": app.node.try_get_context("dns")[ENVIRONMENT]["domain_name"],
    "config_bucket_name": app.node.try_get_context("s3")["config_bucket_name"],
    "logging_bucket_name": app.node.try_get_context("s3")[
        "logging_bucket_name"
    ],
    "asg_max_capacity": app.node.try_get_context("asg")[ENVIRONMENT][
        "max_capacity"
    ],
    "asg_min_capacity": app.node.try_get_context("asg")[ENVIRONMENT][
        "min_capacity"
    ],
    "binary_temp_path": app.node.try_get_context("app_config")["bin_temp_path"],
    "binary_path": app.node.try_get_context("app_config")["bin_path"],
    "slack_email": app.node.try_get_context("slack_config")[ENVIRONMENT][
        "email"
    ],
    "tags": app.node.try_get_context("tags"),
}


# Setting CDK Environment
cdk_account_info = cdk.Environment(
    account=props["account_id"], region=props["region"]
)

net_stack = NetworkStack(
    app,
    props["net_stack_name"],
    props,
    env=cdk_account_info,
    description=props["net_stack_description"],
    stack_name=f"{props['account_alias'].lower()}-{props['net_stack_name']}",
    synthesizer=cdk.DefaultStackSynthesizer(
        qualifier="{INSERT_QUALIFIER_NAME}",
        file_assets_bucket_name=(
            f"{props['account_alias'].lower()}-{props['asset_bucket_name']}"
        ),
    ),
)

hz_stack = HostedZoneStack(
    app,
    props["hz_stack_name"],
    props,
    env=cdk_account_info,
    description=props["hz_stack_description"],
    stack_name=f"{props['account_alias'].lower()}-{props['hz_stack_name']}",
    synthesizer=cdk.DefaultStackSynthesizer(
        qualifier="{INSERT_QUALIFIER_NAME}",
        file_assets_bucket_name=(
            f"{props['account_alias'].lower()}-{props['asset_bucket_name']}"
        ),
    ),
)

rds_stack = RDSStack(
    app,
    props["rds_stack_name"],
    props,
    net_stack.outputs,
    env=cdk_account_info,
    description=props["rds_stack_description"],
    stack_name=f"{props['account_alias'].lower()}-{props['rds_stack_name']}",
    synthesizer=cdk.DefaultStackSynthesizer(
        qualifier="{INSERT_QUALIFIER_NAME}",
        file_assets_bucket_name=(
            f"{props['account_alias'].lower()}-{props['asset_bucket_name']}"
        ),
    ),
)
rds_stack.add_dependency(net_stack)

storage_stack = StorageStack(
    app,
    props["storage_stack_name"],
    props,
    env=cdk_account_info,
    description=props["rds_stack_description"],
    stack_name=f"{props['account_alias'].lower()}-{props['rds_stack_name']}",
    synthesizer=cdk.DefaultStackSynthesizer(
        qualifier="{INSERT_QUALIFIER_NAME}",
        file_assets_bucket_name=(
            f"{props['account_alias'].lower()}-{props['asset_bucket_name']}"
        ),
    ),
)

app_stack = ApplicationStack(
    app,
    props["app_stack_name"],
    props,
    net_stack.outputs,
    hz_stack.outputs,
    rds_stack.outputs,
    env=cdk_account_info,
    description=props["app_stack_description"],
    stack_name=f"{props['account_alias'].lower()}-{props['app_stack_name']}",
    synthesizer=cdk.DefaultStackSynthesizer(
        qualifier="{INSERT_QUALIFIER_NAME}",
        file_assets_bucket_name=(
            f"{props['account_alias'].lower()}-{props['asset_bucket_name']}"
        ),
    ),
)
app_stack.add_dependency(net_stack)
app_stack.add_dependency(hz_stack)
app_stack.add_dependency(rds_stack)
app_stack.add_dependency(storage_stack)

mon_stack = MonitoringStack(
    app,
    props["mon_stack_name"],
    props,
    env=cdk_account_info,
    description=props["mon_stack_description"],
    stack_name=f"{props['account_alias'].lower()}-{props['mon_stack_name']}",
    synthesizer=cdk.DefaultStackSynthesizer(
        qualifier="{INSERT_QUALIFIER_NAME}",
        file_assets_bucket_name=(
            f"{props['account_alias'].lower()}-{props['asset_bucket_name']}"
        ),
    ),
)
mon_stack.add_dependency(app_stack)

cd_stack = CodeDeployStack(
    app,
    props["cd_stack_name"],
    props,
    env=cdk_account_info,
    description=props["cd_stack_description"],
    stack_name=f"{props['account_alias'].lower()}-{props['cd_stack_name']}",
    synthesizer=cdk.DefaultStackSynthesizer(
        qualifier="{INSERT_QUALIFIER_NAME}",
        file_assets_bucket_name=(
            f"{props['account_alias'].lower()}-{props['asset_bucket_name']}"
        ),
    ),
)
cd_stack.add_dependency(app_stack)

# The static tags are stored in the cdk.context.json file, though here we are
# appending dynamic values to the cdk stack.
tags = app.node.try_get_context("tags")

tags["ado_pipeline_run_id"] = PIPELINE_RUN_ID
tags["branch_name"] = BRANCH_NAME
tags["commit_id"] = COMMIT_ID
tags["environment"] = ENVIRONMENT

# Add a tag to all constructs in all stacks
tagged_stacks = [
    net_stack,
    hz_stack,
    rds_stack,
    storage_stack,
    app_stack,
    mon_stack,
    cd_stack,
]

for stacks in tagged_stacks:
    for key, value in tags.items():
        cdk.Tags.of(stacks).add(key, value)

app.synth()
