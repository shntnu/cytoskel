"""
Stack to create staging-cpg bucket and associated resources.
"""

from collections.abc import Callable
from functools import partial
from typing import Optional
from pulumi import ResourceOptions, automation as auto
import pulumi
import pulumi_aws as aws

from cytoskel.s3_access_grants import (
    create_s3_grants_user_boto,
    create_s3_grant_boto,
    create_s3_grants_instance,
    register_s3_prefix,
    create_s3_grants_permissions,
    delete_s3_grants_user_boto,
    delete_s3_grant_boto,
    list_user_arn_boto,
    list_s3_grant_boto,
    list_s3_location_boto,
)


class CPGStagingStack:
    def __init__(
        self: "CPGStagingStack",
        project_name: str,
        stack_name: str,
        env: str,
        project_settings: Optional[auto.ProjectSettings] = None,
        stack_settings: Optional[dict[str, auto.StackSettings]] = None,
        secrets_provider: Optional[str] = None,
    ) -> None:
        self.stack: Optional[auto.Stack] = None
        self.project_name = project_name
        self.stack_name = stack_name
        self.aws_account = aws.get_caller_identity_output()
        self.project_settings = project_settings or auto.ProjectSettings(
            name=project_name, runtime="python"
        )
        self.secrets_provider = secrets_provider
        self.stack_settings = stack_settings or {
            env: auto.StackSettings(secrets_provider=self.secrets_provider)
        }

    def ensure_workspace_plugins(self: "CPGStagingStack") -> None:
        ws = auto.LocalWorkspace()
        ws.install_plugin("aws", "v6.25")

    def create_staging_cpg(self: "CPGStagingStack") -> None:
        # Should we create the bucket here?
        self.bucket = aws.s3.Bucket(
            "staging-cellpainting-gallery",
            bucket="staging-cellpainting-gallery",
            opts=ResourceOptions(protect=True),
        )
        self.grants_instance = create_s3_grants_instance()
        create_s3_grants_permissions(self.grants_instance.access_grants_instance_arn)
        grant_location = register_s3_prefix(
            "demo-staging",
            self.bucket.bucket.apply(lambda x: f"s3://{x}/"),
            self.bucket.arn,
            self.grants_instance.access_grants_instance_arn,
        )
        pulumi.export("grant_location_id", grant_location.access_grants_location_id)

    @staticmethod
    def list_user() -> list[str]:
        return list_user_arn_boto()

    @staticmethod
    def create_user(username: str) -> tuple[str, str]:
        return create_s3_grants_user_boto(username)

    @staticmethod
    def delete_user(username: str) -> None:
        delete_s3_grants_user_boto(username)

    @staticmethod
    def list_location() -> list[str]:
        return list_s3_location_boto()

    @staticmethod
    def list_grant() -> list[str]:
        return list_s3_grant_boto()

    @staticmethod
    def delete_grant(grant_id: str) -> None:
        delete_s3_grant_boto(grant_id)

    @staticmethod
    def create_grant(user_arn: str, grant_location_id: str, prefix: str = "*") -> str:
        return create_s3_grant_boto(
            grant_location_id,
            prefix,
            user_arn,
        )

    def create_pulumi_program(self: "CPGStagingStack", hooks: list = []) -> Callable:
        hooks = [self.create_staging_cpg] + hooks

        def program():
            for hook in hooks:
                hook()

        return partial(program)

    def create_stack(self: "CPGStagingStack") -> auto.Stack:
        self.ensure_workspace_plugins()
        return auto.create_or_select_stack(
            self.stack_name,
            self.project_name,
            self.create_pulumi_program(),
            opts=auto.LocalWorkspaceOptions(
                project_settings=self.project_settings,
                stack_settings=self.stack_settings,
                secrets_provider=self.secrets_provider,
            ),
        )

    def select_stack(self: "CPGStagingStack", hooks: list = []) -> auto.Stack:
        return auto.select_stack(
            self.stack_name,
            self.project_name,
            self.create_pulumi_program(hooks),
            opts=auto.LocalWorkspaceOptions(
                project_settings=self.project_settings,
                stack_settings=self.stack_settings,
                secrets_provider=self.secrets_provider,
            ),
        )
