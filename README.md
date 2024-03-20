# Cytoskel

Cloud infrastrcuture abstraction

## Getting Started

Step 1. Install nix package manager.

Find instructions here.

Step 2. Activate nix environment

```bash
nix develop . --impure
```

Step 3. Configure credentials for `aws` and `pulumi`

Find instructions here andhere respectively.

## Commands for CPG staging stack

Create the stack

```bash
cytoskel cpgstaging up
```

Destroy the stack

```bash
cytoskel cpgstaging down
```

Register prefix location with grants instance

```bash
cytoskel cpgstaging prefix add -n "location name" -p "s3://staging-cellpainting-gallery/"

# or more scoped
cytoskel cpgstaging prefix add -n "location name" -p "s3://staging-cellpainting-gallery/project_id/source_id"
```

Create users that can access grants instance

```bash
cytoskel cpgstaging user add "username"
```

Create grants

```bash
cytoskel cpgstaging grants add -u "username" -l "location"
```
