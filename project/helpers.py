import csv
import datetime
import pytz
import requests
import subprocess
import uuid
import openai
import os
import time
import json

from urllib import parse, request
from flask import redirect, render_template, session
from functools import wraps

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")


client = openai.Client(api_key=OPENAI_API_KEY)


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/welcome")
        return f(*args, **kwargs)

    return decorated_function


# def chatbot(prompt, name):
#     # Create assistant
#     assistant = client.beta.assistants.create(
#         name="SerenAId Companion",
#         instructions="You are a companion for an artificial intelligence powered mental wellness site called SerenAId. You are here listen to people talk about any issues they may have and help them talk through questions they may have. Be very kind and reaffirming and try to give useful advice whenever possible. Give disclaimers when needed though. Try to mention the service's name SerenAId when appropriate and make sure to redirect users to SerenAId's other services such as the Virtual Relaxation Space and Daily Check Ins. Address the user as "
#         + name,
#         tools=[{"type": "code_interpreter"}],
#         model="gpt-3.5-turbo-1106",
#     )

#     # Create thread
#     thread = client.beta.threads.create()

#     # Add message to threat
#     message = client.beta.threads.messages.create(
#         thread_id=thread.id, role="user", content=prompt
#     )

#     run = client.beta.threads.runs.create(
#         thread_id=thread.id,
#         assistant_id=assistant.id,
#     )

#     while True:
#         time.sleep(2)
#         # Check run status
#         run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

#         if run.status == "completed":
#             messages = client.beta.threads.messages.list(thread_id=thread.id)

#             for message in messages.data:
#                 role = message.role
#                 content = message.content[0].text.value
#                 # print(f"THIS IS GOING TO BE MY PRINTING -- {role.capitalize()}: {content}")
#                 return f"{role.capitalize()}: {content}"


def visualize_emotion(emotion):
    response = client.images.generate(
        model="dall-e-2",
        prompt="Generate a visually pleasing dreamscape to represent these emotions: "
        + emotion,
        size="1024x1024",
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url
    print(image_url)

    return image_url


# def visualize_media(media):
#     response = client.images.generate(
#         model="dall-e-2",
#         prompt="Create an image to visualize and perfectly embody the aesthetic of this piece of media (the following will either be a book or tv show or movie etc). Include relevant colors etc but do not use any faces or text. It should just be a vibe, like maybe some sort of landscape or just dreamscape: " + media,
#         size="1024x1024",
#         quality="standard",
#         n=1,
#     )

#     image_url = response.data[0].url
#     print(image_url)

#     return image_url


def motivate(prompt):
    # Create assistant
    assistant = client.beta.assistants.create(
        name="Quote Generator",
        instructions="Say something reaffirming based on what the user says. DO NOT offer more help or say anything like 'I can help further'. This should be a one time comment provided to the user.",
        tools=[{"type": "code_interpreter"}],
        model="gpt-3.5-turbo-1106",
    )

    # Create thread
    thread = client.beta.threads.create()

    # Add message to threat
    message = client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=prompt
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    while True:
        # Check run status
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread.id)

            for message in messages.data:
                content = message.content[0].text.value
                print("{content}")
                return content


def entertain(media):
    # Create assistant
    assistant = client.beta.assistants.create(
        name="SerenAId Companion",
        instructions="Talk a little bit about this show",
        tools=[{"type": "code_interpreter"}],
        model="gpt-3.5-turbo-1106",
    )

    # Create thread
    thread = client.beta.threads.create()

    # Add message to threat
    message = client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=prompt
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    while True:
        # Check run status
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread.id)

            for message in messages.data:
                content = message.content[0].text.value
                print("{content}")
                return content


def analyze(logs):
    # Create assistant
    assistant = client.beta.assistants.create(
        name="Emotion Analysis",
        instructions="Analyze this person's history of how they have been feeling. Give some sort of deep analysis into how they have been progressing and if they left any notes, why they may be feeling that way. You should be presenting it in a nice way and you are going to be talking to the user themself! DO NOT offer more help or say anything like 'I can help further'. This should be a one time comment provided to the user and should not let them think that they can have a further conversation with you.",
        tools=[{"type": "code_interpreter"}],
        model="gpt-3.5-turbo-1106",
    )

    # Create thread
    thread = client.beta.threads.create()

    # Add message to threat
    message = client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=logs
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    while True:
        # Check run status
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread.id)

            for message in messages.data:
                content = message.content[0].text.value
                return content


def generate_colors(prompt):
    # This code is for v1 of the openai package: pypi.org/project/openai
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": 'Answer in a consistent style. Return three HEX values comma separated to mimic the vibe of this show/book/media:' + prompt +'. If you do not know about the piece of media, return three random HEX colors. Avoid black. Your only purpose is to output three HEX values that are separated by commas. The ideal outcome would like something like:\n"#HEX, #HEX, #HEX"',
                },
                {"role": "user", "content": prompt},
                {"role": "user", "content": "Normal People"},
                {"role": "assistant", "content": "#C3829F, #6DA0D7, #A4D2B5"},
                {"role": "user", "content": "Euphoria"},
                {"role": "assistant", "content": "#5D146E, #AA31AD,  #010660"},
                {"role": "user", "content": "Succession"},
                {"role": "assistant", "content": "#008080, #FF6F61, #4B0082"},
            ],
            temperature=0.2,
            max_tokens=235,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
    )

    colors =response.choices[0].message.content

    print(colors)

    color_list = colors.split(',')

    return color_list

def giphy(media):
    url = "http://api.giphy.com/v1/gifs/search"

    params = parse.urlencode({
        "q": media,
        "rating": "pg-13",
        "api_key": GIPHY_API_KEY,
        "limit": "10"
    })

    with request.urlopen("".join((url, "?", params))) as response:
        data = json.loads(response.read())

    # Loop through each set of GIFs
    for gif_data in data['data']:
        # Access the downsized GIF URL for each set
        gif_url = gif_data['images']['downsized']['url']
        print(f"Downsized GIF URL: {gif_url}")


    # Return a list of URLs
    gif_urls = [gif_data['images']['downsized']['url'] for gif_data in data['data']]
    return gif_urls
