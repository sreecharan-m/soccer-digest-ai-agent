from crewai import Task

class SoccerTasks:
    def fetch_trends(self, agent, interests):
        return Task(
            description=(
                f"1. Use the 'Google News Search' (news_tool) tool with this exact query: '{interests}'. "
                "2. Use the 'Google Image Search' (image_tool) tool with this exact query: '{interests}'."
                "3. Collect at least 30 items."
                "4. Make sure to capture the IMAGE URLs. Ensure you have a mix of News (text) and Memes (Images)."
                "5. As last priority if reddit search returns any result, use it to search subreddits: {interests} (e.g. 'soccer,reddevils,realmadrid'). "
            ),
            expected_output="A raw list of 30 potential viral posts with their scores, headlines, and image URLs.",
            agent=agent
        )

    def compile_feed(self, agent):
        return Task(
            description=(
                "Filter the list down to the Top 20 items based on 'Score' or 'Viralness'. "
                "Sort them from Highest Score to Lowest. "
                "Format the output as a clean HTML list. "
                "Rules: "
                "- Display the HEADLINE as an <h3> link. "
                "- If there is an image URL (jpg/png), embed it using <img src='...' width='300'>. "
                "- Show the 'Source' (e.g., r/soccer). "
                "- DO NOT write a summary paragraph. Just the Headline + Image."
            ),
            expected_output="HTML code for a list of 20 viral items.",
            agent=agent
        )