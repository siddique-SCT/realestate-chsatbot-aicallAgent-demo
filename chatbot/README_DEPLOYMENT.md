# Deployment Guide for AI Call Agent Demo

## Overview

This document provides instructions for deploying the AI Call Agent demo application to Render, a cloud platform that offers free hosting for web services.

## Prerequisites

- GitHub account
- Render account (sign up at [render.com](https://render.com))

## Deployment Steps

### 1. Push to GitHub

1. Create a new repository on GitHub
2. Initialize Git in your local project (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

### 2. Deploy to Render

1. Log in to your Render account
2. Click on "New" and select "Web Service"
3. Connect your GitHub repository
4. Configure the web service:
   - **Name**: Choose a name for your service
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --chdir flask_app app:create_app()`
5. Click "Create Web Service"

### 3. Environment Variables

If your application requires environment variables, add them in the Render dashboard under the "Environment" section of your web service.

### 4. Database (if needed)

If your application requires a database, you can create one in Render and connect it to your web service.

## Updating Your Deployment

When you push changes to your GitHub repository, Render will automatically rebuild and deploy your application.

## Limitations of Free Tier

- Limited compute resources
- Free services may spin down after periods of inactivity
- Free databases are destroyed after 90 days

## Troubleshooting

If you encounter issues with your deployment:

1. Check the build logs in the Render dashboard
2. Verify that your application works locally
3. Ensure all dependencies are listed in requirements.txt
4. Check that your Procfile is correctly configured

## Additional Resources

- [Render Documentation](https://render.com/docs)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/3.0.x/deploying/)