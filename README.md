# Cytoskel

Cloud infrastructure abstraction for managing AWS S3 Access Grants, IAM users, and permissions for the `staging-cellpainting-gallery` S3 bucket.

## Getting Started

### Prerequisites

- **AWS CLI** installed and configured with appropriate permissions.
  - Instructions: [AWS CLI Configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)
- **Pulumi** installed and configured.
  - Instructions: [Pulumi Configuration](https://www.pulumi.com/docs/concepts/config/)
- **Python 3.7+**
- **[jq](https://stedolan.github.io/jq/)** installed (required for parsing JSON in shell scripts)
- **Optional:** Nix package manager (for advanced environment management)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/cytoskel.git
   cd cytoskel
   ```

2. **Install the package:**

   ```bash
   pip install -e .
   ```

### Optional: Using Nix (Advanced Users)

If you prefer using the Nix package manager, follow these steps:

1. **Install Nix:**

   Instructions: [Nix Installation](https://nixos.org/download/)

2. **Activate Nix environment:**

   ```bash
   nix develop . --impure
   ```

## Usage

Make sure your AWS credentials have the required permissions and set the `AWS_PROFILE` environment variable.

### Setting Up the Stack

Initialize the Pulumi stack to create the necessary AWS resources:

```bash
pulumi login --cloud-url https://api.pulumi.com
AWS_PROFILE=<your_aws_profile> pulumi up
```

Alternatively, use the provided CLI command:

```bash
AWS_PROFILE=<your_aws_profile> cytoskel cpgstaging up
```

This will:

- Create the `staging-cellpainting-gallery` S3 bucket (if it doesn't exist)
- Set up the S3 Access Grants instance
- Register the bucket location for access grants
- Create necessary IAM roles and policies

### Listing Locations and Users

**List existing locations (registered S3 prefixes):**

```bash
AWS_PROFILE=<your_aws_profile> cytoskel cpgstaging list location
```

Example output:

```
Location: s3://staging-cellpainting-gallery/, ID: e70e7092-7889-42fd-a72b-59b9106a4c51
```

**List existing users:**

```bash
AWS_PROFILE=<your_aws_profile> cytoskel cpgstaging list user
```

Example output:

```
arn:aws:iam::XXXXXXXXXXXX:user/harry
arn:aws:iam::XXXXXXXXXXXX:user/hermione
arn:aws:iam::XXXXXXXXXXXX:user/ron
...
```

### Creating a User

Create a new IAM user:

```bash
AWS_PROFILE=<your_aws_profile> cytoskel cpgstaging create user <username>
```

Replace `<username>` with the desired username (e.g., `test_user`).

**Example:**

```bash
AWS_PROFILE=cpg cytoskel cpgstaging create user test_user
```

**Example output:**

```
Created user ARN: arn:aws:iam::XXXXXXXXXXXX:user/test_user
Creds: {'UserName': 'test_user', 'AccessKeyID': 'XXXX', 'Status': 'Active', 'SecretAccessKey': 'XXXX+XXXX', 'CreateDate': datetime.datetime(2024, 10, 3, 15, 54, 16, tzinfo=tzutc())}
```

**Note:** Store the `AccessKeyID` and `SecretAccessKey` securely and share them with the user.

### Creating a Grant

Grant the user access to a specific prefix in the S3 bucket:

```bash
AWS_PROFILE=<your_aws_profile> cytoskel cpgstaging create grant "<user_arn>" "<location_id>" "<prefix>"
```

- `<user_arn>`: The ARN of the user created in the previous step.
- `<location_id>`: The ID of the location (from the `list location` command).
- `<prefix>`: The prefix within the bucket to which the user will have access (e.g., `mydata/*`).

**Example:**

```bash
AWS_PROFILE=cpg cytoskel cpgstaging create grant "arn:aws:iam::XXXXXXXXXXXX:user/test_user" "e70e7092-7889-42fd-a72b-59b9106a4c51" "cpgxxxx-xxxx/*"
```

**Example output:**

```
Created grant with ARN: arn:aws:s3:us-east-1:XXXXXXXXXXXX:access-grants/default/grant/8e383f90-3881-4842-82cc-b8e83dd91eb6
```

### Accessing the S3 Bucket

The user can now access the specified prefix in the S3 bucket by obtaining temporary session credentials.
See [cytoskel/docs/access_cpg_staging.md](./cytoskel/docs/access_cpg_staging.md) for details.

### Deleting a Grant

Revoke the user's access by deleting the grant.

1. **List Grants to Find the Grant ID**

   ```bash
   AWS_PROFILE=<your_aws_profile> cytoskel cpgstaging list grant
   ```

   Example output:

   ```
   ag-8e383f90-3881-1234-82cc-b8e83dd91eb6
   ag-12345678-90ab-1234-1234-567890abcdef
   ...
   ```

2. **Delete the Grant**

   ```bash
   AWS_PROFILE=<your_aws_profile> cytoskel cpgstaging delete grant ag-8e383f90-3881-1234-82cc-b8e83dd91eb6
   ```

   **Example output:**

   ```
   Deleted grant with ID: ag-8e383f90-3881-1234-82cc-b8e83dd91eb6
   ```

### Deleting a User

Delete the IAM user when they no longer need access:

```bash
AWS_PROFILE=<your_aws_profile> cytoskel cpgstaging delete user <username>
```

**Example:**

```bash
AWS_PROFILE=cpg cytoskel cpgstaging delete user test_user
```

**Example output:**

```
User with username: test_user is deleted
```


## Notes

- **Location:** The S3 bucket registered for access grants.
- **Scope/Prefix:** The specific path within the bucket to which the user is granted access.
- **Permissions:** Users have no permissions until linked to a grant.

## Testing Access

To verify the user's access:

1. **Ensure the user's initial credentials are set in `~/.aws/credentials` under `[cpg_staging]`.**

2. **Use the `s3_credentials.sh` script to obtain temporary credentials.**

   ```bash
   source s3_credentials.sh
   ```

3. **Perform S3 Operations within the Allowed Prefix**

   **List Objects:**

   ```bash
   aws s3 ls s3://staging-cellpainting-gallery/<prefix_without_asterisk>/
   ```

   **Upload a File:**

   ```bash
   aws s3 cp localfile.txt s3://staging-cellpainting-gallery/<prefix_without_asterisk>/
   ```

## Cleanup

Remember to delete grants and users when they are no longer needed to maintain security and manage resources efficiently.

## Optional: Using Nix (Advanced Users)

If you prefer using Nix for environment management, you can use the provided `flake.nix` file.

### `flake.nix`

The `flake.nix` file sets up a development environment with the necessary tools.

**Instructions:**

1. **Activate Nix environment:**

   ```bash
   nix develop . --impure
   ```

2. **Enter the shell:**

   The shell will automatically set up the environment, including installing dependencies and activating the virtual environment.

## Additional Information

- **AWS CLI Configuration:** [AWS CLI Configuration Guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)
- **Pulumi Configuration:** [Pulumi Configuration Guide](https://www.pulumi.com/docs/concepts/config/)
- **Access Grants Documentation:** [AWS S3 Access Points and Grants](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-points.html)

---

*For more detailed information, refer to the code documentation and comments within the source files.*

