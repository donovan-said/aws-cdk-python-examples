#!/usr/bin/env python3
""" A CDK object for the App hosted zone stack """

from aws_cdk import (
    aws_route53 as r53,
    aws_certificatemanager as acm,
    aws_ssm as ssm,
    Stack,
)
from constructs import Construct


class HostedZoneStack(Stack):
    """
    A class to represent the App CDK hosted zone resources
    """

    def __init__(
        self, scope: Construct, construct_id: str, props, **kwargs
    ) -> None:

        super().__init__(scope, construct_id, **kwargs)

        hosted_zone = r53.HostedZone.from_lookup(
            self, "Hosted-Zone", domain_name=props["domain_name"]
        )

        """
        The L1 CFN construct is used here, as an L2 construct doesn't exist
        for AWS Budgets.

        AWS Supported Algorithms:
        https://docs.aws.amazon.com/acm/latest/userguide/acm-certificate.html#algorithms
        """

        rsa_cert = acm.CfnCertificate(
            self,
            "RSA-CERT",
            domain_name=f"app.{props['domain_name']}",
            domain_validation_options=[
                acm.CfnCertificate.DomainValidationOptionProperty(
                    domain_name=f"app.{props['domain_name']}",
                    hosted_zone_id=hosted_zone.hosted_zone_id,
                )
            ],
            key_algorithm="RSA_2048",
            subject_alternative_names=[f"*.app.{props['domain_name']}"],
            validation_method="DNS",
        )

        ecdsa_cert = acm.CfnCertificate(
            self,
            "ECDSA-CERT",
            domain_name=f"app.{props['domain_name']}",
            domain_validation_options=[
                acm.CfnCertificate.DomainValidationOptionProperty(
                    domain_name=f"app.{props['domain_name']}",
                    hosted_zone_id=hosted_zone.hosted_zone_id,
                )
            ],
            key_algorithm="EC_prime256v1",
            subject_alternative_names=[f"*.app.{props['domain_name']}"],
            validation_method="DNS",
        )

        """
        SSM Parameter store is being used to avoid circular dependencies
        inherent in CDK Outputs.
        """

        ssm_values = {
            "CERT/ECDSA/ARN": ecdsa_cert.ref,
            "CERT/RSA/ARN": rsa_cert.ref,
        }

        for ssm_k, ssm_v in ssm_values.items():
            ssm.StringParameter(
                self,
                f"SSM-Parameter-{ssm_k}",
                parameter_name=(
                    f"/{props['account_alias']}/App/HzStack/{ssm_k}"
                ),
                string_value=ssm_v,
            )
