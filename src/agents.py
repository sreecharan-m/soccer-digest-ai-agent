import os
from crewai import Agent, LLM
from crewai_tools import SerperDevTool
from custom_tools import RedditSearchTool

# 1. Setup LLM
api_key_ref = os.getenv("OPENAI_API_KEY")
print(f"API Key loaded: {api_key_ref[:10]}..." if api_key_ref else "API Key NOT found!")
openai_llm = LLM(
    model="openai/gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)

# 2. Setup Tools
google_search = SerperDevTool() # Good for general news
reddit_search = RedditSearchTool() # Good for memes/culture

class SoccerAgents:
    def trend_hunter_agent(self):
        return Agent(
            role='Viral Content Hunter',
            goal='Scrape the top trending content from Reddit and Google News. Find memes, breaking news, and viral images.',
            backstory=(
                "You are a digital trend hunter. You don't care about boring match reports. "
                "You care about what is 'blowing up' on the internet right now. "
                "You look for high upvote counts on Reddit and 'Breaking' tags on news."
            ),
            tools=[reddit_search, google_search], # Giving it both tools
            llm=openai_llm,
            verbose=True
        )

    def curator_agent(self):
        return Agent(
            role='Viral Feed Curator',
            goal='Compile the top 20 viral items into a raw, visual email format.',
            backstory=(
                "You are NOT a writer. You are a Curator. "
                "Your job is to pick the top 20 most interesting items (highest viral score first). "
                "You DO NOT summarize. You preserve the original headlines and image URLs. "
                "You want the reader to see exactly what the internet sees."
            ),
            llm=openai_llm,
            verbose=True
        )