import asyncio
from decouple import config
from openai import AsyncOpenAI
import requests
from weatherapi import WEATHER_API_KEY
from agents import Agent, OpenAIChatCompletionsModel, Runner, function_tool, set_tracing_disabled

my_key =config("GEMINI_API_KEY")

client = AsyncOpenAI(api_key=my_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")

MODEL = OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client)

@function_tool
async def get_weather(city: str) -> str:
    """Fetch the current temperature for a given city."""
    try:
        url = f"https://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&aqi=yes"
        response = requests.get(url)
        data = response.json()
        temp_c = data["current"]["temp_c"]
        condition = data["current"]["condition"]["text"]
        return f"The weather in {city} is {temp_c}°C with {condition}."
    except Exception as e:
        # Mock fallback
        return f"Sorry, could not fetch weather for {city}. (Error: {e})"

set_tracing_disabled(True)
weather_agent = Agent(
    name="Weather Assistant",
    instructions="You need to answer through api. If user ask different questions then you tell them you only give the answer according to the weather.",
    model=MODEL,
    tools=[get_weather]
)

async def main():
    user_input = input("City name mention karo jahah ka weather chahyeah..: ")
    result = await Runner.run(weather_agent, input=user_input)
    print(result.final_output)

asyncio.run(main())