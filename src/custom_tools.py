import requests
import json
import random
import os
from crewai.tools import BaseTool

class GoogleImageSearchTool(BaseTool):
    name: str = "Google Image Search (Targeted)"
    description: str = (
        "Searches Google Images for specific memes and viral photos based on user interests. "
        "Input should be a comma-separated string of teams/topics (e.g., 'Man Utd, Real Madrid'). "
        "Returns a list of image URLs and titles."
    )

    def _run(self, query: str) -> str:
        api_key = os.getenv("SERPER_API_KEY")
        url = "https://google.serper.dev/images"
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        
        # 1. Split interests (e.g., "Man Utd, Real Madrid" -> ["Man Utd", "Real Madrid"])
        interests = [i.strip() for i in query.split(',')]
        # Always add a generic fallback
        if "football memes" not in interests:
            interests.append("football memes")

        results_list = []

        print(f"🎨 Searching Images for: {interests}")

        # 2. Loop through each interest
        for interest in interests:
            # We add keywords to make the search viral-focused
            search_query = f"{interest} funny memes viral 2026"
            
            payload = json.dumps({"q": search_query, "num": 5}) # Get top 5 per topic

            try:
                response = requests.request("POST", url, headers=headers, data=payload)
                data = response.json()
                
                if 'images' in data:
                    for img in data['images']:
                        results_list.append(
                            f"--- IMAGE RESULT ---\n"
                            f"TOPIC: {interest}\n"
                            f"TITLE: {img.get('title')}\n"
                            f"IMAGE_URL: {img.get('imageUrl')}\n"
                            f"SOURCE: {img.get('source')}\n"
                            f"--------------------\n"
                        )
            except Exception as e:
                print(f"❌ Error searching images for {interest}: {e}")
                continue

        # 3. Shuffle so the email isn't just 5 Man Utd memes then 5 Real Madrid memes
        random.shuffle(results_list)
        return "\n".join(results_list)


class GoogleNewsSearchTool(BaseTool):
    name: str = "Google News Search (Targeted)"
    description: str = (
        "Searches Google News for specific breaking stories based on user interests. "
        "Input should be a comma-separated string of teams/topics. "
        "Returns headlines, snippets, and links."
    )

    def _run(self, query: str) -> str:
        api_key = os.getenv("SERPER_API_KEY")
        url = "https://google.serper.dev/search"
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        
        interests = [i.strip() for i in query.split(',')]
        results_list = []

        print(f"📰 Searching News for: {interests}")

        for interest in interests:
            # We look for news from the last 24 hours
            search_query = f"{interest} latest football news"
            
            # 'tbs': 'qdr:d' means "Query Date Range: Day" (Last 24 hours)
            payload = json.dumps({"q": search_query, "num": 5, "tbs": "qdr:d"})

            try:
                response = requests.request("POST", url, headers=headers, data=payload)
                data = response.json()
                
                if 'organic' in data:
                    for item in data['organic']:
                        results_list.append(
                            f"--- NEWS ITEM ---\n"
                            f"TOPIC: {interest}\n"
                            f"HEADLINE: {item.get('title')}\n"
                            f"LINK: {item.get('link')}\n"
                            f"SNIPPET: {item.get('snippet')}\n"
                            f"-----------------\n"
                        )
            except Exception as e:
                print(f"❌ Error searching news for {interest}: {e}")
                continue

        random.shuffle(results_list)
        return "\n".join(results_list)
    
class RedditSearchTool(BaseTool):
    name: str = "Reddit Trend Search"
    description: str = (
        "Scrapes top viral posts from a curated list of football subreddits. "
        "Useful for finding memes, breaking news, and fan reactions. "
        "Input should be a comma-separated string of teams or 'all' for general trends."
    )

    def _run(self, query: str = "all") -> str:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # 1. Define the "Power List" of subreddits
        # We mix serious news sources with meme/banter sources for a full picture
        default_subs = [
            "soccer",           # The main hub
            "soccercirclejerk", # The best source for viral memes/irony
            "PremierLeague",
            "LaLiga",
            "reddevils",        # Man Utd (Huge active community)
            "RealMadrid",       # Real Madrid
            "footballmemes"     # General memes
        ]

        # 2. Determine which subs to scrape based on user query
        target_subs = []
        if query.lower() == "all" or query == "":
            target_subs = default_subs
        else:
            # If the user asks for specific teams, try to map them or just use the query
            # But ALWAYS add 'soccer' and 'soccercirclejerk' for context
            target_subs = [s.strip() for s in query.split(',')]
            target_subs.extend(["soccer", "soccercirclejerk"]) 

        # 3. Scrape logic
        results = []
        unique_links = set() # To avoid duplicates
        
        print(f"🕵️  Scraping Subreddits: {target_subs}...")

        for sub in target_subs:
            url = f"https://www.reddit.com/r/{sub}/hot.json?limit=10" # Grab top 10 hot posts
            
            try:
                response = requests.get(url, headers=headers, timeout=5)
                if response.status_code != 200:
                    continue
                    
                data = response.json()
                posts = data.get('data', {}).get('children', [])
                
                for post in posts:
                    p = post['data']
                    
                    # FILTERS:
                    # 1. Score must be high (Viral check)
                    # 2. Must not be a sticky (usually mod announcements)
                    if p.get('score', 0) < 300 and not p.get('stickied'):
                        continue

                    # 3. Check for Media (We want images/videos!)
                    media_type = "Text"
                    media_url = ""
                    
                    if "i.redd.it" in p.get('url', ''):
                        media_type = "Image"
                        media_url = p['url']
                    elif "v.redd.it" in p.get('url', ''):
                        media_type = "Video"
                        media_url = p['url'] # Reddit videos are harder to embed, but we keep the link
                    elif "twitter.com" in p.get('url', '') or "x.com" in p.get('url', ''):
                        media_type = "Twitter Link"
                        media_url = p['url']
                    
                    # Avoid duplicates
                    if p['permalink'] in unique_links:
                        continue
                    unique_links.add(p['permalink'])

                    # 4. Format for the Agent
                    post_data = (
                        f"--- POST ---\n"
                        f"SOURCE: r/{sub}\n"
                        f"TYPE: {media_type}\n"
                        f"HEADLINE: {p.get('title')}\n"
                        f"UPVOTES: {p.get('score')} 🔥\n"
                        f"LINK: https://www.reddit.com{p.get('permalink')}\n"
                        f"MEDIA_URL: {media_url}\n"
                        f"------------\n"
                    )
                    results.append(post_data)

            except Exception as e:
                print(f"⚠️ Error scraping r/{sub}: {e}")
                continue

        # Shuffle results so the agent doesn't just see one subreddit at the top
        random.shuffle(results)
        
        # Return top 25 raw items for the agent to filter
        return "\n".join(results[:25])