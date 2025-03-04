# AI X Poster for Artificial Wearables

A headless Python script that automatically posts to X (Twitter) about Artificial Wearables, a minimalist apparel brand.

## Features

- Automatically generates content for posts about Artificial Wearables
- Posts to X on a scheduled basis (default: every 6 hours)
- Maintains history of posts to prevent repetition
- Runs in headless mode without a web interface

## Requirements

- Python 3.6+
- OpenRouter API key
- Twitter Developer API credentials

## Setup

1. Create a virtual environment:
   ```
   python3 -m venv venv
   ```

2. Activate the virtual environment:
   ```
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API credentials:
   ```
   # Twitter API Credentials
   TWITTER_API_KEY=your_api_key
   TWITTER_API_SECRET=your_api_secret
   TWITTER_ACCESS_TOKEN=your_access_token
   TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
   TWITTER_BEARER_TOKEN=your_bearer_token

   # OpenRouter API
   OPENROUTER_API_KEY=your_openrouter_api_key

   # Configuration
   POST_SCHEDULE="0 */6 * * *"  # Every 6 hours
   AI_MODEL="anthropic/claude-3-haiku"  # Or another model of your choice
   ```

## Usage

Run the script:
```
python ai_poster_headless.py
```

The script will:
1. Post immediately when first run
2. Continue posting on the schedule defined in your `.env` file (default: every 6 hours)
3. Run until interrupted with Ctrl+C

## Logs and History

- Logs are saved to `ai_poster.log`
- Post history is saved to `post_history.json`

## Content Style

The posts focus on:
- Minimalist design and aesthetics
- Unique patterns and design elements
- Brand products like tees and hoodies
- Design philosophy and process

Posts are kept brief, authentic, and non-promotional while occasionally mentioning specific products in a natural way. 