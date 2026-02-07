#!/bin/bash

# Load project configuration from .env
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "Error: .env file not found."
    exit 1
fi

PROJECT_ID=${GOOGLE_CLOUD_PROJECT}
LOCATION=${GOOGLE_CLOUD_LOCATION:-us-central1}

# Agent Engine usually requires a specific region (like us-central1)
# even if models are global. If LOCATION is global, we might need a default region.
if [ "$LOCATION" == "global" ]; then
    echo "Warning: Agent Engine typically requires a regional location (e.g. us-central1)."
    echo "Setting deployment region to 'us-central1' for Agent Engine."
    DEPLOY_REGION="us-central1"
else
    DEPLOY_REGION=$LOCATION
fi

# Create a GCS bucket if needed (for staging)
# ADK deploy agent_engine might not strictly require this now, but it's good practice.
BUCKET_NAME="${PROJECT_ID}-adk-staging"

echo "Checking for staging bucket: gs://${BUCKET_NAME}..."
if ! gcloud storage buckets describe "gs://${BUCKET_NAME}" >/dev/null 2>&1; then
    echo "Creating GCS bucket: gs://${BUCKET_NAME} in ${DEPLOY_REGION}..."
    gcloud storage buckets create "gs://${BUCKET_NAME}" --location="${DEPLOY_REGION}" --project="${PROJECT_ID}"
else
    echo "Bucket gs://${BUCKET_NAME} already exists."
fi

# Deploy the agent
echo "Deploying stock_agent to Agent Engine in ${PROJECT_ID}/${DEPLOY_REGION}..."
adk deploy agent_engine \
    --project="${PROJECT_ID}" \
    --region="${DEPLOY_REGION}" \
    --display_name="Stock ADK Agent" \
    --description="A real-time stock info agent using MCP tools." \
    agents/stock_agent

echo "Deployment completed!"
