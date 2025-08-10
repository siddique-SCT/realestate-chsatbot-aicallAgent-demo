# Deploying to Render

## One-Click Deployment

If you've forked this repository, you can deploy it to Render with one click using the button below:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## Manual Deployment

### 1. Create a Render Account

Sign up for a free account at [render.com](https://render.com).

### 2. Connect Your GitHub Repository

1. In the Render dashboard, click on "New" and select "Web Service".
2. Connect your GitHub account if you haven't already.
3. Select the repository containing your AI Call Agent demo.

### 3. Configure Your Web Service

Fill in the following details:

- **Name**: Choose a name for your service (e.g., "ai-call-agent-demo")
- **Environment**: Python 3
- **Region**: Choose the region closest to your users
- **Branch**: main (or your preferred branch)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --chdir flask_app app:create_app()`

### 4. Set Environment Variables

Expand the "Advanced" section and add any required environment variables for your application.

### 5. Deploy

Click "Create Web Service" to deploy your application. Render will build and deploy your app automatically.

## Updating Your Deployment

When you push changes to your GitHub repository, Render will automatically rebuild and deploy your application.

## Monitoring

You can monitor your application's logs and performance in the Render dashboard.

## Free Tier Limitations

- Your service may spin down after periods of inactivity
- Limited compute resources
- Free databases are destroyed after 90 days

## Troubleshooting

If your deployment fails:

1. Check the build logs in the Render dashboard
2. Verify that your application works locally
3. Ensure all dependencies are listed in requirements.txt
4. Check that your Procfile and render.yaml are correctly configured