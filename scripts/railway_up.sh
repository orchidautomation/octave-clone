#!/bin/bash

# Use this script to deploy Playbook AI on Railway
# Prerequisites:
# - Railway CLI installed
# - Railway account logged in via `railway login`
# - Environment variables set: OPENAI_API_KEY, FIRECRAWL_API_KEY

set -e  # Exit on any error

echo -e "🚂 Starting Railway deployment...\n"

# Initialize a new project on Railway
railway init -n "playbook-ai"

echo -e "📦 Deploying PgVector database...\n"
railway deploy -t 3jJFCA

echo -e "⏳ Waiting 10 seconds for database to be created...\n"
sleep 10

echo -e "🔧 Creating application service with environment variables...\n"
railway add --service playbook_ai \
  --variables "DB_DRIVER=postgresql+psycopg" \
  --variables 'DB_USER=${{pgvector.PGUSER}}' \
  --variables 'DB_PASS=${{pgvector.PGPASSWORD}}' \
  --variables 'DB_HOST=${{pgvector.PGHOST}}' \
  --variables 'DB_PORT=${{pgvector.PGPORT}}' \
  --variables 'DB_DATABASE=${{pgvector.PGDATABASE}}' \
  --variables "OPENAI_API_KEY=${OPENAI_API_KEY}" \
  --variables "FIRECRAWL_API_KEY=${FIRECRAWL_API_KEY}"

echo -e "🚀 Deploying application...\n"
railway up --service playbook_ai -d

echo -e "🔗 Creating domain...\n"
railway domain --service playbook_ai

echo -e "Note: It may take up to 5 minutes for the domain to reach ready state while the application is deploying.\n"

echo -e "✅ Deployment complete!\n"
echo -e "💡 Tip: Run 'railway logs --service playbook_ai' to view your application logs.\n"
