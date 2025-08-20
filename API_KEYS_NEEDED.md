# 🔑 API Keys Required for OmniFunnel AI Visibility Platform

## Immediate Priority (Tracker Service)

### 1. OpenAI API Key
- **Where to get**: https://platform.openai.com/api-keys
- **Variable**: `OPENAI_API_KEY`
- **Format**: `sk-...` (starts with sk-)
- **Used for**: ChatGPT engine with browsing capability
- **Cost**: Pay-per-token usage (typically $0.01-0.03 per 1K tokens)

### 2. Anthropic API Key  
- **Where to get**: https://console.anthropic.com/
- **Variable**: `ANTHROPIC_API_KEY`
- **Format**: `sk-ant-...` (starts with sk-ant-)
- **Used for**: Claude engine analysis and responses
- **Cost**: Pay-per-token usage (similar to OpenAI)

### 3. Google API Key (Gemini)
- **Where to get**: https://makersuite.google.com/app/apikey
- **Variable**: `GOOGLE_API_KEY`
- **Format**: Standard Google API key
- **Used for**: Gemini AI search and responses
- **Cost**: Free tier available, then pay-per-use

## Optional (Enhanced Features)

### 4. Pinecone API Key
- **Where to get**: https://app.pinecone.io/
- **Variable**: `PINECONE_API_KEY`
- **Used for**: Vector embeddings and entity similarity
- **Cost**: Free tier available (1M vectors), then $70/month

## Setup Instructions

1. **Copy template**: `cp .env.template .env`
2. **Fill in your keys**: Edit `.env` file with actual API keys
3. **Restart services**: `docker-compose down && docker-compose up -d`

## Security Notes

- ⚠️ Never commit `.env` files to git
- ✅ Use test/development keys initially
- ✅ Rotate keys regularly in production
- ✅ Monitor usage and set billing alerts

## Without These Keys

The tracker service will run but AI engines will return mock responses. You'll see:
- ✅ API endpoints work
- ✅ Database operations function  
- ✅ Prompt variants generate
- ⚠️ Engine responses are simulated
- ⚠️ No real AI analysis occurs

## Next Phase Keys (Coming Soon)

- **Stripe** (billing): Required for user subscriptions
- **JWT Secret**: Required for authentication 
- **CMS APIs**: Required for WordPress/Webflow integration