"""
Cytoskel CLI.
"""

from pprint import pprint

import click


from cytoskel.stacks.staging_cpg import CPGStagingStack

# CPGS Stack


@click.command(name="up")
def cpgs_up() -> None:
    stack = CPGStagingStack("CPG-Staging", "S3GrantsAccess", "test")
    stack = stack.create_stack()
    stack.up(on_output=pprint)


@click.command(name="destroy")
def cpgs_destroy() -> None:
    stack = CPGStagingStack("CPG-Staging", "S3GrantsAccess", "test")
    stack = stack.select_stack()
    stack.destroy(on_output=pprint)


# CPGS User
@click.command(name="user")
@click.argument("username")
def cpgs_create_user(username: str) -> None:
    user_arn, creds = CPGStagingStack.create_user(username)
    click.echo(f"Created user Arn: {user_arn}\nCreds: {creds}")


@click.command(name="user")
@click.argument("username")
def cpgs_delete_user(username: str) -> None:
    CPGStagingStack.delete_user(username)
    click.echo(f"User with username: {username} is deleted")


@click.command("user")
def cpgs_list_user() -> None:
    user_arns = CPGStagingStack.list_user()
    sep = "\n"
    click.echo(f"{sep.join(user_arns)}")


@click.command("location")
def cpgs_list_location() -> None:
    location_ids = CPGStagingStack.list_location()
    sep = "\n"
    click.echo(f"{sep.join(location_ids)}")


# CPGS Grant
@click.command("grant")
def cpgs_list_grant() -> None:
    grant_ids = CPGStagingStack.list_grant()
    sep = "\n"
    click.echo(f"{sep.join(grant_ids)}")


@click.command("grant")
@click.argument("userarn")
@click.argument("location_id")
@click.argument("prefix", default="*")
def cpgs_create_grant(userarn: str, location_id: str, prefix: str) -> None:
    grant_arn = CPGStagingStack.create_grant(userarn, location_id, prefix)
    click.echo(f"Created grant with ARN: {grant_arn}")


@click.command(name="grant")
@click.argument("grant_id")
def cpgs_delete_grant(grant_id: str) -> None:
    CPGStagingStack.delete_grant(grant_id)
    click.echo(f"Delted grant with Id: {grant_id}")


@click.group(name="create")
def cpgstagingcreate() -> None:
    """CPG Staging create stack console."""
    pass


cpgstagingcreate.add_command(cpgs_create_user)
cpgstagingcreate.add_command(cpgs_create_grant)


@click.group(name="delete")
def cpgstagingdelete() -> None:
    """CPG Staging delete stack console."""
    pass


cpgstagingdelete.add_command(cpgs_delete_user)
cpgstagingdelete.add_command(cpgs_delete_grant)


@click.group(name="list")
def cpgstaginglist() -> None:
    """CPG Staging list stack console."""
    pass


cpgstaginglist.add_command(cpgs_list_user)
cpgstaginglist.add_command(cpgs_list_grant)
cpgstaginglist.add_command(cpgs_list_location)


@click.group
def cpgstaging() -> None:
    """CPG Staging stack console."""
    pass


cpgstaging.add_command(cpgs_up)
cpgstaging.add_command(cpgs_destroy)
cpgstaging.add_command(cpgstagingcreate)
cpgstaging.add_command(cpgstagingdelete)
cpgstaging.add_command(cpgstaginglist)


@click.group
def main() -> None:
    """Cytoskel console."""
    pass


main.add_command(cpgstaging)
