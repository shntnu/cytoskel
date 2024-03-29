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
cytoskel cpgstaging destroy
```

Create user

```bash
cytoskel cpgstaging create user "username"
```

Get grant location ids

```bash
cytoskel cpgstaging list location
```

Create access grants

```bash
cytoskel cpgstaging create grant "username" "location_is" "prefix"
```
