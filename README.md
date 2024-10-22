# Cytoskel

Cloud infrastructure tool for managing AWS S3 Access Grants, IAM users, and permissions for `staging-cellpainting-gallery` S3 bucket.

## Prerequisites

- AWS CLI with configured permissions
- Pulumi
- Python 3.7+
- `jq`
- (Optional) Nix package manager

## Quick Start

```bash
# Install
git clone https://github.com/broadinstitute/cytoskel.git
cd cytoskel
pip install -e .

# Alternatively, use Nix
nix develop . --impure
```

## Core Operations

All commands require `AWS_PROFILE=<your_aws_profile>` prefix (or set `AWS_PROFILE` environment variable).
`your_aws_profile` should have admin access to `cellpainting-gallery` AWS account.

### Initialize Infrastructure (One-Time Setup)

This needs to be done just once to:

- Create the `staging-cellpainting-gallery` S3 bucket (if it doesn't exist)
- Set up the S3 Access Grants instance
- Register the bucket location for access grants
- Create necessary IAM roles and policies

Skip over this step if the infrastructure has already been initialized.

```bash
cytoskel cpgstaging up
```

### List Resources

```bash
# List locations
cytoskel cpgstaging list location
# Output: Location: s3://staging-cellpainting-gallery/, ID: e70e7092-7889-42fd-a72b-59b9106a4c51

# List users
cytoskel cpgstaging list user
# Output: arn:aws:iam::XXXXXXXXXXXX:user/harry
```

### User Management

```bash
# Create user
cytoskel cpgstaging create user test_user
# Output:
# Created user ARN: arn:aws:iam::XXXXXXXXXXXX:user/test_user
# Creds: {'UserName': 'test_user', 'AccessKeyID': 'XXXX', 'SecretAccessKey': 'XXXX+XXXX', ...}

# Delete user
cytoskel cpgstaging delete user test_user
# Output: User with username: test_user is deleted
```

### Grant Management

```bash
# Create grant: specify user ARN, location ID, and bucket prefix
cytoskel cpgstaging create grant "arn:aws:iam::XXXXXXXXXXXX:user/test_user" "e70e7092-7889-42fd-a72b-59b9106a4c51" "cpgxxxx-xxxx/*"
# Output: Created grant with ARN: arn:aws:s3:us-east-1:XXXXXXXXXXXX:access-grants/default/grant/8e383f90-3881-4842-82cc-b8e83dd91eb6

# List grants
cytoskel cpgstaging list grant
# Output: ag-8e383f90-3881-1234-82cc-b8e83dd91eb6

# Delete grant
cytoskel cpgstaging delete grant ag-8e383f90-3881-1234-82cc-b8e83dd91eb6
# Output: Deleted grant with ID: ag-8e383f90-3881-1234-82cc-b8e83dd91eb6
```

## Testing Access

1. Set user credentials in `~/.aws/credentials` under `[cpg_staging]`
2. Get temporary credentials (see instructions [here](/cytoskel/docs/access_cpg_staging.md) for details):

   ```bash
   source s3_credentials.sh
   ```

3. Test access:

   ```bash
   # List objects
   aws s3 ls s3://staging-cellpainting-gallery/cpgxxxx-xxxx/

   # Upload file
   aws s3 cp localfile.txt s3://staging-cellpainting-gallery/cpgxxxx-xxxx/
   ```

## Notes

- Users have no permissions until linked to a grant
- Always clean up unused grants and users
- Store AccessKeyID and SecretAccessKey securely

## Resources

- [Access Grants Docs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-points.html)
