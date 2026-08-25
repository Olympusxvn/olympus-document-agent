#Requires -Version 5.1
param(
  [string]$ProjectId = "olympus-vat-agent",
  [string]$Region = "asia-southeast1",
  [string]$Service = "olympus-vat-agent",
  [string]$Topic = "gmail-vat"
)

$ErrorActionPreference = "Stop"

function Require-Gcloud {
  $gcloud = Get-Command gcloud -ErrorAction SilentlyContinue
  if (-not $gcloud) {
    Write-Host @"
gcloud is not on PATH. Install Google Cloud SDK, then re-run:

  https://cloud.google.com/sdk/docs/install

Sign in with the same Google Cloud account you already have:

  gcloud auth login
  gcloud config set project $ProjectId
"@
    exit 1
  }
}

Require-Gcloud
gcloud config set project $ProjectId | Out-Null

$apis = @(
  "run.googleapis.com",
  "pubsub.googleapis.com",
  "firestore.googleapis.com",
  "gmail.googleapis.com",
  "aiplatform.googleapis.com",
  "secretmanager.googleapis.com",
  "cloudscheduler.googleapis.com",
  "cloudbuild.googleapis.com"
)
gcloud services enable $apis

gcloud firestore databases describe --database="(default)" 2>$null
if ($LASTEXITCODE -ne 0) {
  gcloud firestore databases create --location=$Region --database="(default)"
}

gcloud pubsub topics describe $Topic 2>$null
if ($LASTEXITCODE -ne 0) {
  gcloud pubsub topics create $Topic
}

# Gmail push publisher (required by users.watch)
gcloud pubsub topics add-iam-policy-binding $Topic `
  --member="serviceAccount:gmail-api-push@system.gserviceaccount.com" `
  --role="roles/pubsub.publisher"

Write-Host @"

Next:
  1. Cloud Run env: GOOGLE_CLOUD_PROJECT, GMAIL_ADDRESS, GMAIL_PUBSUB_TOPIC, INGEST_TOKEN
     (ADC — do not set GMAIL_CLIENT_ID / SECRET / REFRESH_TOKEN)
  2. Deploy via GitHub Cloud Build or:

     gcloud run deploy $Service --source . --region $Region --allow-unauthenticated --set-env-vars GOOGLE_CLOUD_PROJECT=$ProjectId

     For production, prefer --no-allow-unauthenticated and a Pub/Sub push invoker SA.

  3. Create a push subscription to https://SERVICE_URL/pubsub
  4. POST /internal/watch-renew with INGEST_TOKEN (and schedule it daily — watch expires in ~7 days)
  5. Optional fallback: Cloud Scheduler POST /internal/poll every 1 minute with INGEST_TOKEN
"@
