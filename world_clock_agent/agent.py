from datetime import datetime
from dateutil import tz
from google.adk.agents.llm_agent import Agent
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.tools.google_search_tool import google_search
from google.genai import types


def get_current_time(timezone: str) -> dict:
    """Returns the current date and time for a given timezone.

    Args:
        timezone: The IANA timezone name (e.g., 'Asia/Kolkata', 'America/New_York', 'Europe/London', 'UTC').

    Returns:
        dict: A dictionary containing current time details or an error message.
    """
    target_tz = tz.gettz(timezone)
    if target_tz is None:
        return {
            "status": "error",
            "message": f"Timezone '{timezone}' was not recognized. Please provide a valid IANA timezone name (e.g. 'Asia/Kolkata', 'America/New_York', 'UTC')."
        }

    now = datetime.now(target_tz)
    return {
        "status": "success",
        "timezone": timezone,
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%I:%M:%S %p"),
        "time_24hr": now.strftime("%H:%M:%S"),
        "day_of_week": now.strftime("%A"),
        "timezone_abbreviation": now.strftime("%Z"),
    }


root_agent = Agent(
    model='gemini-3.8-flash',
    name='root_agent',
    description='A world clock assistant that can report the current time across different timezones and search the web.',
    instruction=(
        'Answer user questions about the current time and date across the world. '
        'Use the get_current_time tool to fetch accurate time for any specified timezone. '
        'Use Google Search when you need to look up timezones for specific cities, regions, or current events.'
    ),
    tools=[get_current_time, google_search],
    code_executor=BuiltInCodeExecutor(),
    generate_content_config=types.GenerateContentConfig(
        tool_config=types.ToolConfig(
            include_server_side_tool_invocations=True
        )
    ),
)

