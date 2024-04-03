"""
AWS S3 access grant related functions.
"""

import json
from typing import Tuple

import boto3
import pulumi
import pulumi_aws as aws


def create_s3_grants_instance(
    name: str = "grant_instance",
) -> aws.s3control.AccessGrantsInstance:
    access_grants_instance = aws.s3control.AccessGrantsInstance(
        name, tags={"pulumi_managed": "true"}
    )
    return access_grants_instance


def register_s3_prefix(
    name: str,
    location_scope: pulumi.Output,
    bucket_arn: pulumi.Output,
    access_grants_instance_arn: pulumi.Output,
) -> aws.s3control.AccessGrantsLocation:
    aws_account = aws.get_caller_identity_output()
    iam_role = aws.iam.Role(
        "cpg_staging_access_grant",
        name="cpg_staging_access_grant_location_role",
        max_session_duration=43200,
        assume_role_policy=pulumi.Output.all(
            account_id=aws_account.account_id,
            access_grants_instance_arn=access_grants_instance_arn,
        ).apply(
            lambda args: json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "AccessGrantsTrustPolicy",
                            "Effect": "Allow",
                            "Principal": {"Service": "access-grants.s3.amazonaws.com"},
                            "Action": ["sts:AssumeRole", "sts:SetSourceIdentity"],
                            "Condition": {
                                "StringEquals": {
                                    "aws:SourceArn": args["access_grants_instance_arn"],
                                    "aws:SourceAccount": args["account_id"],
                                }
                            },
                        },
                        {
                            "Sid": "AccessGrantsTrustPolicyWithIDCContext",
                            "Effect": "Allow",
                            "Principal": {"Service": "access-grants.s3.amazonaws.com"},
                            "Action": "sts:SetContext",
                            "Condition": {
                                "StringEquals": {
                                    "aws:SourceArn": args["access_grants_instance_arn"],
                                    "aws:SourceAccount": args["account_id"],
                                },
                                "ForAnyValue:StringEquals": {
                                    "aws:RequestContextProvider": "arn:aws:iam:::contextProvider/IdentityCenter"
                                },
                            },
                        },
                    ],
                }
            )
        ),
        inline_policies=[
            aws.iam.RoleInlinePolicyArgs(
                name="cpg_staging_access_grant_location_policy",
                policy=pulumi.Output.all(
                    bucket_arn=bucket_arn,
                    account_id=aws_account.account_id,
                    access_grants_instance_arn=access_grants_instance_arn,
                ).apply(
                    lambda args: json.dumps(
                        {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Sid": "ObjectLevelReadPermissions",
                                    "Effect": "Allow",
                                    "Action": [
                                        "s3:GetObject",
                                        "s3:GetObjectVersion",
                                        "s3:GetObjectAcl",
                                        "s3:GetObjectVersionAcl",
                                        "s3:ListMultipartUploadParts",
                                    ],
                                    "Resource": [f"{args['bucket_arn']}*"],
                                    "Condition": {
                                        "StringEquals": {
                                            "aws:ResourceAccount": args["account_id"]
                                        },
                                        "ArnEquals": {
                                            "s3:AccessGrantsInstanceArn": [
                                                args["access_grants_instance_arn"]
                                            ]
                                        },
                                    },
                                },
                                {
                                    "Sid": "ObjectLevelWritePermissions",
                                    "Effect": "Allow",
                                    "Action": [
                                        "s3:PutObject",
                                        "s3:PutObjectAcl",
                                        "s3:PutObjectVersionAcl",
                                        "s3:DeleteObject",
                                        "s3:DeleteObjectVersion",
                                        "s3:AbortMultipartUpload",
                                    ],
                                    "Resource": [f"{args['bucket_arn']}*"],
                                    "Condition": {
                                        "StringEquals": {
                                            "aws:ResourceAccount": args["account_id"]
                                        },
                                        "ArnEquals": {
                                            "s3:AccessGrantsInstanceArn": [
                                                args["access_grants_instance_arn"]
                                            ]
                                        },
                                    },
                                },
                                {
                                    "Sid": "BucketLevelReadPermissions",
                                    "Effect": "Allow",
                                    "Action": ["s3:ListBucket"],
                                    "Resource": [args["bucket_arn"]],
                                    "Condition": {
                                        "StringEquals": {
                                            "aws:ResourceAccount": args["account_id"]
                                        },
                                        "ArnEquals": {
                                            "s3:AccessGrantsInstanceArn": [
                                                args["access_grants_instance_arn"]
                                            ]
                                        },
                                    },
                                },
                            ],
                        }
                    )
                ),
            )
        ],
    )
    return aws.s3control.AccessGrantsLocation(
        name, location_scope=location_scope, iam_role_arn=iam_role.arn
    )


def create_s3_grants_permissions(grant_instance_arn: pulumi.Output) -> aws.iam.Group:
    policy_json = pulumi.Output.all(grant_instance_arn=grant_instance_arn).apply(
        lambda args: json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": ["s3:GetDataAccess"],
                        "Effect": "Allow",
                        "Resource": [args["grant_instance_arn"]],
                    }
                ],
            }
        )
    )
    policy = aws.iam.Policy(
        "staging_cpg_creds_data_access",
        name="staging_cpg_creds_data_access",
        path="/",
        description="Policy for staging_cpg_uploaders",
        policy=policy_json,
    )
    group = aws.iam.Group(
        "staging_cpg_uploaders",
        name="staging_cpg_uploaders",
    )
    aws.iam.GroupPolicyAttachment(
        "s3_access_grants_group_policy_attach",
        group=group.name,
        policy_arn=policy.arn,
    )
    return group


def create_s3_grants_user_boto(username: str) -> tuple[str, str]:
    iam_client = boto3.client("iam")
    response = iam_client.create_user(
        UserName=username,
    )
    res = iam_client.create_access_key(UserName=username)
    iam_client.add_user_to_group(GroupName="staging_cpg_uploaders", UserName=username)
    return response["User"]["Arn"], f"{res['AccessKey']}"


def delete_s3_grants_user_boto(username: str) -> None:
    client = boto3.client("iam")
    client.remove_user_from_group(GroupName="staging_cpg_uploaders", UserName=username)
    res = client.list_access_keys(UserName=username)
    for aid in [obj["AccessKeyId"] for obj in res["AccessKeyMetadata"]]:
        client.delete_access_key(UserName=username, AccessKeyId=aid)
    client.delete_user(UserName=username)


def _create_s3_grants_user(name: str) -> Tuple[aws.iam.User, aws.iam.AccessKey]:
    user = aws.iam.User(name)
    access_key = aws.iam.AccessKey(name, user=user.name)
    aws.iam.UserGroupMembership(
        f"{name}_staging_cpg_uploaders_membership",
        user=user.name,
        groups=["staging_cpg_uploaders"],
    )
    return (user, access_key)


def list_user_arn_boto() -> list[str]:
    client = boto3.client("iam")
    res = client.list_users()
    return [user["Arn"] for user in res["Users"]]


def create_s3_grant_boto(location_id: str, prefix: str, grantee_arn: str) -> str:
    account_id = boto3.client("sts").get_caller_identity().get("Account")
    client = boto3.client("s3control")
    res = client.create_access_grant(
        AccountId=account_id,
        AccessGrantsLocationId=location_id,
        AccessGrantsLocationConfiguration={"S3SubPrefix": prefix},
        Grantee={"GranteeType": "IAM", "GranteeIdentifier": grantee_arn},
        Permission="READWRITE",
    )
    return res["AccessGrantArn"]


def delete_s3_grant_boto(grant_id: str) -> None:
    account_id = boto3.client("sts").get_caller_identity().get("Account")
    client = boto3.client("s3control")
    client.delete_access_grant(AccountId=account_id, AccessGrantId=grant_id)


def list_s3_location_boto() -> list[str]:
    account_id = boto3.client("sts").get_caller_identity().get("Account")
    client = boto3.client("s3control")
    res = client.list_access_grants_locations(AccountId=account_id)
    return [
        f'Location: {location["LocationScope"]}, Id: {location["AccessGrantsLocationId"]}'
        for location in res["AccessGrantsLocationsList"]
    ]


def list_s3_grant_boto() -> list[str]:
    account_id = boto3.client("sts").get_caller_identity().get("Account")
    client = boto3.client("s3control")
    res = client.list_access_grants(AccountId=account_id)
    return [grant["AccessGrantId"] for grant in res["AccessGrantsList"]]


def _create_s3_grant(
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
