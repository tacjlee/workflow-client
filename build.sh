#!/bin/bash
# Build script for workflow-client package

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Building workflow-client ==="

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info workflow_client.egg-info

# Ensure build tool is installed
if ! python -m pip show build &>/dev/null; then
    echo "Installing build tool..."
    python -m pip install build
fi

# Build the package
echo "Building package..."
python -m build

echo ""
echo "=== Build complete ==="
echo "Output files:"
ls -la dist/

echo ""
echo "To install locally:"
echo "  pip install dist/workflow_client-*.whl"
echo ""
echo "To install in another project:"
echo "  pip install /path/to/workflow-client/dist/workflow_client-*.whl"
