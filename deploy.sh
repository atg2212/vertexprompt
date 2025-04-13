#!/bin/bash

# ==============================================================================
# Cloud Run Deployment Script for Vertex Prompt Playground Service
# ==============================================================================
# https://cloud.google.com/sdk/gcloud/reference/run/deploy
#
# This script builds a container image using Cloud Build and deploys it # to Cloud Run.
#
# Instructions:
# 1. Replace the placeholder values in the "Configuration Variables" section below with your actual Google Cloud project details.
# 2. Make sure you have the gcloud CLI installed and authenticated:
#    `gcloud auth login`
#    `gcloud auth application-default login`
# 3. Ensure your project structure is correct (Dockerfile, main.py, handlers, requirements.txt, are in the current directory).
# 4. Make the script executable: `chmod +x deploy.sh`
# 5. Run the script: `./deploy.sh`
#
# ==============================================================================

# --- Configuration Variables ---

# Replace with your Google Cloud Project ID
PROJECT_ID="landing-zone-demo-341118"

# Replace with your desired Google Cloud region
REGION="me-west1"

# Replace with your desired Artifact Registry repository name
REPOSITORY="vertex-prompt-playground"

# Replace with your desired container image name
IMAGE_NAME="vertex-prompt-playground"

# Replace with your desired Cloud Run service name
SERVICE_NAME="vertex-prompt-playground"

# Replace with your desired Cloud Run service account
SERVICE_ACCOUNT_EMAIL="experts-hub-demo@landing-zone-demo-341118.iam.gserviceaccount.com"

# --- Script Start ---

echo "-------------------------------------"
echo "Starting Cloud Run Deployment"
echo "-------------------------------------"
echo "Project ID: $PROJECT_ID"
echo "Region:     $REGION"
echo "Repository: $REPOSITORY"
echo "Image Name: $IMAGE_NAME"
echo "Service:    $SERVICE_NAME"
echo "-------------------------------------"

# 1. Set the active Google Cloud project
echo "\n[Step 1/5] Setting active project..."
gcloud config set project $PROJECT_ID
if [ $? -ne 0 ]; then echo "Error setting project. Aborting."; exit 1; fi

# 2. Enable necessary Google Cloud services
echo "\n[Step 2/5] Enabling required services (Cloud Build, Artifact Registry, Cloud Run)..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  aiplatform.googleapis.com
if [ $? -ne 0 ]; then echo "Error enabling services. Aborting."; exit 1; fi

# 3. Create Artifact Registry repository (if it doesn't exist)
#    The command will fail gracefully if the repository already exists.
echo "\n[Step 3/5] Ensuring Artifact Registry repository exists ($REPOSITORY)..."
gcloud artifacts repositories describe $REPOSITORY --location=$REGION > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "Repository $REPOSITORY not found. Creating..."
  gcloud artifacts repositories create $REPOSITORY \
    --repository-format=docker \
    --location=$REGION \
    --description="Docker repository for AI Learning Service"
  if [ $? -ne 0 ]; then echo "Error creating repository. Aborting."; exit 1; fi
else
  echo "Repository $REPOSITORY already exists."
fi

# Construct the full image path
IMAGE_PATH="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:latest"
echo "\nFull Image Path: $IMAGE_PATH"

# 4. Build the container image using Cloud Build
echo "\n[Step 4/5] Building container image using Cloud Build..."
gcloud builds submit --tag $IMAGE_PATH .
if [ $? -ne 0 ]; then echo "Error building image with Cloud Build. Aborting."; exit 1; fi
echo "Image build successful: $IMAGE_PATH"

# 5. Deploy the container image to Cloud Run
echo "\n[Step 5/5] Deploying image to Cloud Run service ($SERVICE_NAME)..."
gcloud run deploy $SERVICE_NAME \
  --image=$IMAGE_PATH \
  --platform=managed \
  --region=$REGION \
  --allow-unauthenticated \
  --ingress=internal-and-cloud-load-balancing \
  --min-instances=0 \
  --concurrency=20 \
  --service-account=$SERVICE_ACCOUNT_EMAIL \
  --execution-environment=gen2    \
  --cpu-boost \
  --cpu=2 \
  --memory=4Gi \

if [ $? -ne 0 ]; then echo "Error deploying to Cloud Run. Aborting."; exit 1; fi

echo "\n-------------------------------------"
echo "Deployment Successful!"
echo "-------------------------------------"
exit 0