"""
AWS S3 access grant related functions.
"""

import json
from typing import Tuple

import boto3
import pulumi_aws as aws


def create_s3_grants_instance(
    name: str = "grant_instance",
) -> aws.s3control.AccessGrantsInstance:
    access_grants_instance = aws.s3control.AccessGrantsInstance(
        name, tags={"pulumi_managed": "true"}
    )
    return access_grants_instance


def register_s3_prefix(name: str, prefix: str) -> aws.s3control.AccessGrantsLocation:
    return aws.s3control.AccessGrantsLocation(name, location_scope=prefix)


def create_s3_grants_permissions(grant_instance_arn: str) -> aws.iam.Group:
    policy = aws.iam.Policy(
        "policy_name",
        policy=json.dumps(
            {
                "version": "2012-10-17",
                "statement": [
                    {
                        "sid": "",
                        "effect": "Allow",
                        "action": "s3:GetDataAccess",
                        "resource": grant_instance_arn,
                    }
                ],
            }
        ),
    )
    group = aws.iam.Group(
        "staging_cpg_uploaders",
    )
    aws.iam.GroupPolicyAttachment(
        "s3_access_grants_group_policy_attach",
        group=group.name,
        policy_arn=policy.arn,
    )
    return group


def create_s3_grants_user(name: str) -> Tuple[aws.iam.User, aws.iam.AccessKey]:
    user = aws.iam.User(name)
    access_key = aws.iam.AccessKey(name, user=user.name)
    aws.iam.UserGroupMembership(
        f"{name}_staging_cpg_uploaders_membership",
        user=user.name,
        groups=["staging_cpg_uploaders"],
    )
    return (user, access_key)


def create_s3_grant(
    username: str, location_id: str, prefix: str, grantee_arn: str
) -> aws.s3control.AccessGrant:
    return aws.s3control.AccessGrant(
        f"{username}_access_grant",
        access_grants_location_id=location_id,
        access_grants_location_configuration=aws.s3control.AccessGrantAccessGrantsLocationConfigurationArgs(
            s3_sub_prefix=prefix
        ),
        permission="READWRITE",
        grantee=aws.s3control.AccessGrantGranteeArgs(
            grantee_type="IAM", grantee_identifier=grantee_arn
        ),
    )
