# How to Get a Google Gemini API Key

To use the CTF Assistant, you'll need a Google Gemini API key. Here's a step-by-step guide to obtaining one:

## Step 1: Sign up for Google AI Studio

1. Go to [Google AI Studio](https://makersuite.google.com/)
2. Sign in with your Google account
3. Accept the terms of service

## Step 2: Get an API Key

1. Click on the "Get API key" or "API key" option in the menu
2. Create a new API key by clicking "Create API key"
3. Give your key a name (e.g., "CTF Assistant")
4. Copy the API key that's generated (it will look something like "AIza...")

## Step 3: Configure Your Environment

1. Add the API key to your `.env` file:
   ```
   GEMINI_API_KEY=your_key_here
   ```

2. Or pass it as an environment variable when running with Docker:
   ```
   docker run -p 8000:8000 -e GEMINI_API_KEY=your_key_here ctf-assistant
   ```

## Step 4: Verify API Access

To make sure your API key is working, you can test it with a simple Python script:

```python
import google.generativeai as genai

# Configure the API
genai.configure(api_key="your_key_here")

# Test the API
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("Hello, Gemini!")
print(response.text)
```

## API Pricing and Quotas

- Google Gemini API has a free tier that allows for a generous number of requests
- Check the [Google AI Studio pricing page](https://ai.google.dev/pricing) for current information
- Be aware of rate limits and quotas that may apply to your API key

## Troubleshooting

If you encounter issues with your API key:

1. Make sure your key is correctly formatted and hasn't expired
2. Check if you've reached your API quota for the day
3. Ensure you're using the correct model name ('gemini-pro')
4. Verify that your internet connection can reach Google's API servers