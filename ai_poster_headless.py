#!/usr/bin/env python3
"""
Headless AI X Poster for Artificial Wearables

Posts promotional content for Artificial Wearables to X (Twitter) using OpenRouter API
"""
import os
import json
import random
from datetime import datetime
import logging
import re
from pathlib import Path
import requests
import tweepy
from apscheduler.schedulers.blocking import BlockingScheduler
from openai import OpenAI
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ai_poster.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ArtificialWearablesPoster")

# Load environment variables
load_dotenv()



# OpenRouter API key
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "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")

# App configuration
POST_SCHEDULE = os.environ.get("POST_SCHEDULE", "0 */6 * * *")  # Default: every 6 hours
AI_MODEL = os.environ.get("AI_MODEL", "anthropic/claude-3-haiku")

# Brand features
BRAND_FEATURES = [
    "minimalist design",
    "clean aesthetic",
    "unique patterns",
    "comfortable fabrics",
    "simple color palette",
    "attention to detail",
    "everyday wear",
    "quality materials",
    "thoughtful design",
    "geometric patterns",
    "visual simplicity"
]

# Product mentions
PRODUCT_MENTIONS = [
    "our black tees",
    "the minimal hoodie",
    "our pattern collection",
    "the monochrome series",
    "our new tshirt design",
    "the geometric print",
    "our basic tee",
    "the new collection"
]

# File to store post history
HISTORY_FILE = "post_history.json"

# Initialize OpenRouter client
try:
    openrouter_client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY
    )
    logger.info("OpenRouter client initialized successfully")
except Exception as e:
    logger.error(f"Error initializing OpenRouter client: {str(e)}")
    openrouter_client = None

def load_post_history():
    """Load post history from file"""
    history_path = Path(HISTORY_FILE)
    if history_path.exists():
        try:
            with open(history_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading post history: {str(e)}")
            return []
    else:
        return []

def save_post_history(history):
    """Save post history to file"""
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
        logger.info("Post history saved successfully")
    except Exception as e:
        logger.error(f"Error saving post history: {str(e)}")

def clean_tweet_content(content):
    """Remove any meta-commentary or invalid formatting from tweet content"""
    # Remove any "here's a tweet" type meta-commentary
    meta_prefixes = [
        "here's a tweet", "here's a thoughtful tweet", "here is a tweet", 
        "as the artificial wearables account", "tweet:", "post:", 
        "here's what", "artificial wearables:"
    ]
    
    cleaned = content
    for prefix in meta_prefixes:
        if cleaned.lower().startswith(prefix):
            remaining = cleaned[len(prefix):].strip()
            match = re.search(r'[.:!?]\s+(\w)', remaining)
            if match:
                start_pos = match.start() + 2
                cleaned = remaining[start_pos:]
            else:
                cleaned = remaining
    
    # Remove "from the artificial wearables account" and similar phrases
    clean_phrases = [
        "from the artificial wearables account", 
        "from artificial wearables",
        "as artificial wearables"
    ]
    for phrase in clean_phrases:
        cleaned = cleaned.replace(phrase, "")
    
    # Remove trailing ellipses and whitespace
    cleaned = cleaned.rstrip(". \t\n")
    
    # Make sure it's not empty after cleaning
    if not cleaned.strip():
        return "we're focused on minimal designs that maximize aesthetic appeal."
    
    return cleaned.strip()

def generate_content():
    """Generate content for X post"""
    try:
        # Get post history to avoid repetition
        post_history = load_post_history()
        past_posts = [post["content"] for post in post_history]
        
        system_prompt = (
            "You are the Artificial Wearables Twitter account. Write the exact tweet text - nothing more. "
            "Focus on design, aesthetics, and style - NOT sustainability. "
            "Use simple, short words. Avoid technical terms or jargon. "
            "Write short observations about design, style, or creative process. "
            "Occasionally mention a specific product like a tee, hoodie, or collection. "
            "Never sound like you're selling something, even when mentioning products. "
            "Keep it very brief - one short sentence is ideal. Use lowercase. "
            "NEVER exceed 100 characters total. Shorter is better. "
            "Speak as 'we' when referring to the brand. Keep it casual and simple. "
        )
        
        user_prompt = f"Write a single short tweet from Artificial Wearables. "
        
        # Decide whether to mention a product directly (30% chance)
        if random.random() < 0.3:
            product = random.choice(PRODUCT_MENTIONS)
            user_prompt += f"Briefly mention {product} in a natural way. "
        else:
            user_prompt += f"Focus on one of these aspects: {', '.join(random.sample(BRAND_FEATURES, k=1))}. "
            
        user_prompt += (
            f"Keep it under 100 characters, be authentic and understated. "
            f"Examples for style reference:\n"
            f"'we like how our new patterns look simple from far away but complex up close'\n"
            f"'sometimes the best designs come from happy accidents'\n"
            f"'black and white never goes out of style'\n"
            f"'our minimal tees feel better after washing them a few times'"
        )
        
        if past_posts:
            user_prompt += f"\n\nDo NOT repeat these previous posts: {past_posts[-5:]}"
        
        if openrouter_client:
            # Generate content using OpenRouter client
            response = openrouter_client.chat.completions.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            content = response.choices[0].message.content.strip()
        else:
            # Fallback content if OpenRouter client fails
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": AI_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                }
            )
            json_response = response.json()
            content = json_response["choices"][0]["message"]["content"].strip()
        
        # Clean the content
        content = clean_tweet_content(content)
        
        # Check if content length exceeds Twitter's limit
        if len(content) > 280:
            logger.warning("Generated content exceeds 280 characters. Truncating...")
            content = content[:277] + "..."
            
        logger.info(f"Generated content: {content}")
        return content
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        # Return a fallback message in case of error
        fallback_options = [
            "simple designs just work better. less to distract from the details that matter.",
            "black is still our favorite color. it goes with everything.",
            "new patterns inspired by old graph paper sketches. sometimes analog is best.",
            "trying out new stitching techniques. small details make big differences.",
            "our best ideas usually happen while walking. movement creates clarity.",
            "the new tees are softer than we expected. sometimes suppliers surprise you.",
            "our minimal hoodies pair with literally everything. that's the goal."
        ]
        return random.choice(fallback_options)

def post_to_x(content):
    """Post content to X (Twitter)"""
    try:
        # Create a Tweepy Client for API v2
        client = tweepy.Client(
            bearer_token=TWITTER_BEARER_TOKEN,
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
        )
        
        # Post the tweet
        response = client.create_tweet(text=content)
        
        # Extract the tweet ID from the response
        tweet_id = response.data["id"]
        
        logger.info(f"Successfully posted to X: {content}")
        logger.info(f"Tweet ID: {tweet_id}")
        
        return response
    except Exception as e:
        logger.error(f"Error posting to X: {str(e)}")
        return None

def store_post(content, success=True):
    """Store post in history file"""
    history = load_post_history()
    
    # Add new post to history
    history.append({
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "success": success
    })
    
    # Save updated history
    save_post_history(history)
    logger.info(f"Added post to history. Total posts: {len(history)}")

def run_automation():
    """Run the automated posting process"""
    logger.info("Running automated posting job...")
    
    # Generate content
    content = generate_content()
    
    if content:
        # Post to X
        result = post_to_x(content)
        
        # Store the post in history
        store_post(content, result is not None)
        
        return result
    else:
        logger.error("No content was generated. Skipping this posting cycle.")
        return None

def main():
    """Main function to run the scheduler"""
    logger.info("Artificial Wearables X Poster initialized")
    logger.info(f"Posting schedule: {POST_SCHEDULE}")
    
    # Run once immediately
    logger.info("Running initial post...")
    run_automation()
    
    # Schedule future posts
    scheduler = BlockingScheduler()
    
    # Parse cron expression
    parts = POST_SCHEDULE.strip('"').split()
    if len(parts) == 5:
        minute, hour, day, month, day_of_week = parts
        scheduler.add_job(
            run_automation, 
            'cron', 
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week
        )
        
        logger.info("Scheduler started. Press Ctrl+C to exit.")
        scheduler.start()
    else:
        logger.error(f"Invalid cron expression: {POST_SCHEDULE}")
        return

if __name__ == "__main__":
    main() 
