import os
from crewai import Agent, LLM
from crewai_tools import SerperDevTool
from custom_tools import RedditSearchTool, GoogleImageSearchTool, GoogleNewsSearchTool

# 1. Setup LLM
api_key_ref = os.getenv("OPENAI_API_KEY")
print(f"API Key loaded: {api_key_ref[:10]}..." if api_key_ref else "API Key NOT found!")
openai_llm = LLM(
    model="openai/gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)

# 2. Setup Tools
news_tool = GoogleNewsSearchTool() # Good for general news
reddit_search = RedditSearchTool() # Good for memes/culture
image_tool = GoogleImageSearchTool()

class SoccerAgents:
    def trend_hunter_agent(self):
        return Agent(
            role='Viral Content Hunter',
            goal='Scrape the top trending viral content. Find memes, breaking news, and viral images. You MUST find valid image URLs.',
            backstory=(
                "You are a digital trend hunter. You don't care about boring match reports. You do not search for generic 'football news'."
                "You use the user's specific interests to find targeted memes and breaking news."
                "You care about what is 'blowing up' on the internet right now, and 'Breaking' tags on news."
                "You MUST use the Google Image Tool to find visual content."
                "If reddit search works look for high upvote counts on Reddit"
            ),
            tools=[reddit_search, news_tool, image_tool], # Giving it both tools
            llm=openai_llm,
            verbose=True
        )

    def curator_agent(self):
        return Agent(
            role='Viral Feed Curator',
            goal='Compile the top 20 viral items into a raw, visual email format.',
            backstory=(
                "You are NOT a writer. You are a Curator. Your email MUST be visual."
                "Your job is to pick the top 20 most interesting items (highest viral score first). "
                "You DO NOT summarize. You preserve the original headlines and image URLs. "
                "prioritize in a way that least 50 percent of items have an 'IMAGE_URL'. The more the better, if they fit the viral score and trending condition"
                "You balance the content covering maximum user's interests, not just one team or topic"
            ),
            llm=openai_llm,
            verbose=True
        )