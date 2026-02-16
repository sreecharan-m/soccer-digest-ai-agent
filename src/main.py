import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from crewai import Crew, Process
from agents import SoccerAgents
from tasks import SoccerTasks
import smtplib
from email.mime.multipart import MIMEMultipart

# Load environment variables
load_dotenv()

def send_email_blast(html_content):
    """
    Sends the newsletter to a list of recipients using Gmail SMTP.
    """
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")
    recipients_raw = os.getenv("EMAIL_RECIPIENTS")

    if not sender or not password or not recipients_raw:
        print("❌ Error: Missing Gmail credentials or recipients in .env")
        return

    # Convert string "a@b.com, c@d.com" -> list ["a@b.com", "c@d.com"]
    recipients = [r.strip() for r in recipients_raw.split(',')]
    
    print(f"📧 Preparing to send email to {len(recipients)} recipients...")

    try:
        # 1. Connect to Gmail Server ONCE (Efficiency Hack)
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender, password)

        # 2. Loop through recipients and send individually
        for receiver in recipients:
            
            # Create a fresh message object for each person
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "🔥 Your Daily Football Viral Feed"
            msg['From'] = f"The Kickoff Bot <{sender}>" # Custom Sender Name
            msg['To'] = receiver

            # Wrapper HTML (White Card Style)
            final_html = f"""
            <html>
            <body style="font-family: 'Helvetica Neue', Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    
                    <div style="text-align: center; border-bottom: 2px solid #efefef; padding-bottom: 20px; margin-bottom: 20px;">
                        <h1 style="color: #d32f2f; margin: 0; font-size: 28px; letter-spacing: -1px;">⚽ The Daily Kickoff</h1>
                        <p style="color: #888; font-size: 14px; margin-top: 5px; font-style: italic;">Curated Viral Trends & News</p>
                    </div>

                    <div style="color: #333; line-height: 1.6; font-size: 16px;">
                        {html_content}
                    </div>

                    <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #efefef; text-align: center; color: #999; font-size: 12px;">
                        <p>Sent by Sree's AI Agent • Built with CrewAI & Python</p>
                        <p><a href="#" style="color: #999; text-decoration: none;">Unsubscribe (Just text me)</a></p>
                    </div>
                    
                </div>
            </body>
            </html>
            """

            msg.attach(MIMEText(final_html, 'html'))
            
            # Send
            server.send_message(msg)
            print(f"   ✅ Sent to: {receiver}")

        # 3. Close Connection
        server.quit()
        print("🎉 All emails sent successfully!")

    except Exception as e:
        print(f"❌ Failed to send email blast: {str(e)}")

def main():
    # 1. Define your interests
    # You can customize this list to change what the agent hunts for
    interests = "reddevils,RealMadrid,soccercirclejerk,PremierLeague"

    # 2. Instantiate Agents & Tasks
    agents = SoccerAgents()
    tasks = SoccerTasks()

    hunter = agents.trend_hunter_agent()
    curator = agents.curator_agent()

    # Pass arguments to tasks
    task1 = tasks.fetch_trends(hunter, interests)
    task2 = tasks.compile_feed(curator)

    # 3. Assemble the Crew
    crew = Crew(
        agents=[hunter, curator],
        tasks=[task1, task2],
        process=Process.sequential,
        verbose=True
    )

    print("🚀 Starting the Soccer Crew...")
    
    # 4. Kickoff!
    # The result contains the raw HTML body from the Curator
    result = crew.kickoff()
    
    # 5. Send to everyone
    print("\n\nFINAL CONTENT GENERATED. SENDING BLAST...\n")
    send_email_blast(str(result))

if __name__ == "__main__":
    main()