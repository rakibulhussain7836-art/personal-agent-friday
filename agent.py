"""
agent.py
Friday's AI brain - powered by Gemini.
"""

import os
import json
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools import (
    calculate,
    read_file,
    write_file,
    web_search,
    run_command,
    open_website,
)

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MEMORY_FILE = "memory.json"

SYSTEM_PROMPT = """
You are Friday, a helpful personal AI assistant running on the user's computer.

You can talk naturally with the user and use your available tools.

IMPORTANT TOOL RULES:

1. If the user asks you to calculate something, use calculate.
2. If the user asks you to search for current information, use web_search.
3. If the user asks you to open a website, use open_website.
4. If the user asks you to read a text file, use read_file.
5. If the user asks you to create or write a file, use write_file.
6. run_command can execute computer terminal commands.
   NEVER execute a command that requires confirmation unless the user
   explicitly confirms it.
7. After using a tool, explain the result naturally and briefly.
8. If the user is simply talking to you, respond conversationally.
   Do not use a tool unnecessarily.

You are called Friday.
Be concise, friendly and helpful.
"""

GEMINI_TOOLS = [
    calculate,
    read_file,
    write_file,
    web_search,
    run_command,
    open_website,
]


def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"facts": []}


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)


class Agent:
    def __init__(self):
        self.memory = load_memory()

        memory_context = ""
        if self.memory.get("facts"):
            facts = "\n".join(f"- {fact}" for fact in self.memory["facts"])
            memory_context = "\n\nThings you remember about the user:\n" + facts

        self.config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT + memory_context,
            tools=GEMINI_TOOLS
        )

        self.history = []

    def chat(self, user_message: str) -> str:
        try:
            self.history.append({
                "role": "user",
                "parts": [{"text": user_message}]
            })

            # Keep only the last 20 messages so context doesn't keep growing
            # and slowing every response down over time
            if len(self.history) > 20:
                self.history = self.history[-20:]

            start = time.time()

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=self.history,
                config=self.config
            )

            elapsed = time.time() - start
            print(f"[Gemini response took {elapsed:.2f} seconds]")

            reply = response.text

            self.history.append({
                "role": "model",
                "parts": [{"text": reply}]
            })

            return reply

        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                return "I've hit my daily usage limit. Try again later, or check aistudio.google.com for reset time."
            return f"Error: {e}"

    def remember(self, fact: str):
        if not fact:
            return
        self.memory.setdefault("facts", [])
        self.memory["facts"].append(fact)
        save_memory(self.memory)


if __name__ == "__main__":
    agent = Agent()
    print("Friday is ready. Type 'exit' to quit.")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            break

        if user_input.lower().startswith("remember:"):
            fact = user_input.split(":", 1)[1].strip()
            agent.remember(fact)
            print("Friday: I'll remember that.")
            continue

        reply = agent.chat(user_input)
        print(f"Friday: {reply}\n")