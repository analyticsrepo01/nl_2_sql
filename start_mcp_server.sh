#!/bin/bash
# Start Toolbox MCP Server for BigQuery tools

# Set version if not already set
VERSION=${VERSION:-0.5.2}

# Check if toolbox binary exists
if [ ! -f "./toolbox" ]; then
    echo "Downloading toolbox binary..."
    curl -L -o toolbox "https://storage.googleapis.com/genai-toolbox/v${VERSION}/linux/amd64/toolbox"
    chmod +x toolbox
    echo "✓ Toolbox downloaded"
fi

# Check if tools.yaml exists
if [ ! -f "tools.yaml" ]; then
    echo "ERROR: tools.yaml not found in current directory"
    echo "Please ensure tools.yaml exists before starting the server"
    exit 1
fi

echo "Starting Toolbox MCP Server..."
echo "Config file: tools.yaml"
echo "Server will run on: http://127.0.0.1:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================================"

# Start the toolbox MCP server
./toolbox --tools-file "tools.yaml" --port 5000
