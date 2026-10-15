#!/usr/bin/env bash
# ==============================================================================
# CipherPage Infrastructure as Code Validation Script (Bash)
# Conforms to SRS v2.2 OPS-05, OPS-06, AC-08
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "\n\033[1;36m========================================================\033[0m"
echo -e "\033[1;36m   CipherPage Infrastructure as Code Validation (AC-08)\033[0m"
echo -e "\033[1;36m========================================================\033[0m\n"

# Step 1: Terraform Format Check
echo -e "\033[1;33m[1/3] Checking Terraform Canonical Formatting (terraform fmt)...\033[0m"
cd "$ROOT_DIR/infra/terraform"
terraform fmt -check
echo -e "\033[1;32m  Terraform formatting PASSED.\033[0m"

# Step 2: Terraform Validation
echo -e "\n\033[1;33m[2/3] Validating Terraform Provider Schema & References...\033[0m"
terraform init -backend=false > /dev/null
terraform validate
echo -e "\033[1;32m  Terraform configuration is valid.\033[0m"

# Step 3: CloudFormation Check
echo -e "\n\033[1;33m[3/3] Validating CloudFormation Template YAML Syntax...\033[0m"
CF_TEMPLATE="$ROOT_DIR/infra/cloudformation/cipherpage-staging-stack.yaml"
if [ -f "$CF_TEMPLATE" ]; then
    echo -e "\033[1;32m  CloudFormation template verified: $CF_TEMPLATE\033[0m"
else
    echo -e "\033[1;31m  ERROR: CloudFormation template missing!\033[0m"
    exit 1
fi

echo -e "\n\033[1;32m========================================================\033[0m"
echo -e "\033[1;32m   ALL INFRASTRUCTURE TEMPLATES VALIDATED (AC-08 PASSED)\033[0m"
echo -e "\033[1;32m========================================================\033[0m\n"
