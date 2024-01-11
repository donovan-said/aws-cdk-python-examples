#!/bin/bash

# This script has been tested on MacOS (M1 Chip).

########################################################################################################################
#################################################### User Input ########################################################
########################################################################################################################

usage="$(basename "$0") [-h] [-a ACTION] [-e ENVIRONMENT] [-t TYPE] [-s STACK]
A script to manage the deployment of the cdk stacks:
    -a cdk action
    -e environment
    -t cdk stack type (shared or app)
    -s cdk stack
    -h Show the usage text"

while getopts :a:e:t:s:h opt; do
    case "${opt}" in
        a)
          action=${OPTARG}
          echo "Option -a (cdk action) has been specified with argument: $action"
          ;;
        e)
          environ=${OPTARG}
          echo "Option -e (environment) has been specified with argument: $environ"
          ;;
        t)
          type=${OPTARG}
          echo "Option -s (stack type) has been specified with argument: $stack"
          ;;
        s)
          stack=${OPTARG}
          echo "Option -s (cdk stack) has been specified with argument: $stack"
          ;;
        h)
          echo "Script usage: $usage" >&2
          exit 0
          ;;
        \?)
          echo "Script usage: $usage" >&2
          exit 1
          ;;
    esac
done

########################################################################################################################
############################################## Environment Variables ###################################################
########################################################################################################################

export PIPELINE_RUN_ID="run_manually"
export BRANCH_NAME=$(git symbolic-ref --short HEAD)
export COMMIT_ID=$(git rev-parse --verify HEAD)
export CDK_ENVIRONMENT="$environ"

if [[ "$environ" == "dev" ]]
then
  AWS_PROFILE="{INSERT_AWS_PROFILE}"
elif [[ "$environ" == "uat" ]]
then
  AWS_PROFILE="{INSERT_AWS_PROFILE}"
elif [[ "$environ" == "prod" ]]
then
  AWS_PROFILE="{INSERT_AWS_PROFILE}"
fi

ALIAS_UPPER=${AWS_PROFILE:0:7}
ALIAS_LOWER=$(echo "$ALIAS_UPPER" | tr '[:upper:]' '[:lower:]')
REGION="eu-west-2"

# Shared and app resources are stored in different paths.
if [[ "$type" == "shared" ]]
then
  CDK_RESOURCE_PATH="shared/$stack"
else
  CDK_RESOURCE_PATH="apps/$stack"
fi

########################################################################################################################
############################################ Deploy CDK Bootstrap stack ################################################
########################################################################################################################

S3_BOOTSTRAP_BUCKET="$ALIAS_LOWER"-cdk-bootstrap-templates-"$REGION"

echo ""
echo "##############################################"
echo ">> Checking if the AWS CDK bootstrap S3 bucket exists"

if [[ -z $(aws s3api head-bucket --bucket "$ALIAS_LOWER"-cdk-bootstrap-templates-"$REGION" --profile "$AWS_PROFILE" 2>&1) ]];
  then
    echo ">> The AWS CDK bootstrap bucket \"$ALIAS_LOWER-cdk-bootstrap-templates-$REGION\" exists"
  else
    echo ">> The AWS CDK bootstrap bucket \"$ALIAS_LOWER-cdk-bootstrap-templates-$REGION\" does not exist"
    echo ">> Proceeding to create the S3 bucket: \"$S3_BOOTSTRAP_BUCKET\""
    aws s3api create-bucket \
      --bucket "$S3_BOOTSTRAP_BUCKET" \
      --profile "$AWS_PROFILE" \
      --region eu-west-2 \
      --create-bucket-configuration LocationConstraint="$REGION" 1> /dev/null
fi

echo ""
echo "##############################################"
echo ">> Checking for updates to the AWS CDK bootstrap template"

cd cdk/cdk-bootstrap

aws cloudformation deploy \
  --stack-name "$ALIAS_UPPER"-CDKToolkit-{INSERT_APP_NAME} \
  --template-file bootstrap-template.yaml \
  --parameter-overrides file://"$environ"-params.json \
  --s3-bucket "$ALIAS_LOWER"-cdk-bootstrap-templates-eu-west-2 \
  --region "$REGION" \
  --capabilities CAPABILITY_NAMED_IAM \
  --profile "$AWS_PROFILE"

########################################################################################################################
################################################# Deploy CDK stack #####################################################
########################################################################################################################

echo ""
echo "##############################################"
echo ">> Performing CDK action: $action on $stack"
cd ../"$CDK_RESOURCE_PATH"
cdk "$action" --profile "$AWS_PROFILE" --all
