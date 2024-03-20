"""
Stack to create staging-cpg bucket and associated resources.
"""

from collections.abc import Callable
from functools import partial
from typing import Optional
from pulumi import automation as auto
import pulumi_aws as aws

from cytoskel.s3_access_grants import (
    create_s3_grants_instance,
    register_s3_prefix,
    create_s3_grants_user,
    create_s3_grants_permissions,
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
        self.project_settings = project_settings or auto.ProjectSettings(
            name=project_name, runtime="python"
        )
        self.secrets_provider = secrets_provider
        self.stack_settings = stack_settings or {
            env: auto.StackSettings(secrets_provider=self.secrets_provider)
        }

    def ensure_workspace_plugins(self: "CPGStagingStack") -> None:
        ws = auto.LocalWorkspace()
        ws.install_plugin("aws", "v6.27")

    def create_staging_cpg(self: "CPGStagingStack") -> None:
        # Should we create the bucket here?
        aws.s3.Bucket("staging-cellpainting-gallery")
        instance = create_s3_grants_instance()
        create_s3_grants_permissions(str(instance.access_grants_instance_arn))

    def create_user(self: "CPGStagingStack", username: str) -> None:
        stack = self.select_stack([partial(create_s3_grants_user, username)])
        stack.up()

    def add_prefix(self: "CPGStagingStack", name: str, prefix: str) -> None:
        stack = self.select_stack([partial(register_s3_prefix, name, prefix)])
        stack.up()

    def create_grant(self: "CPGStagingStack", username: str) -> None:
        stack = self.select_stack([partial(create_s3_grant, username, location)])
        stack.up()

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
        self.ensure_workspace_plugins()
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
