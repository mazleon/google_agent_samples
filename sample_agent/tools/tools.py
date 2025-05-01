""" This file contains the tools list and their functionalities which can be used with LLM"""

import random
import datetime
# Some greeting styles
greeting_styles = [
    "Hello there",
    "Hi there",
    "Hello",
    "Hi",
    "Hello, how are you?",
    "Hi, how are you?",
    "Hello, I am a helpful assistant.",
    "Hi, I am a helpful assistant.",
    "Hello, I am a helpful assistant, how can I help you?",
    "Hi, I am a helpful assistant, how can I help you?",
]

# Some farewell styles
farewell_styles = [
    "Goodbye",
    "Bye",
    "See you later",
    "See you soon",
    "See you",
    "Bye, have a great day!",
    "Goodbye, have a great day!",
    "Bye, take care!",
    "Goodbye, take care!",
    "Bye, have a good day!",
    "Goodbye, have a good day!",
    "Bye, have a good night!",
    "Goodbye, have a good night!",
    "Bye, have a good week!",
    "Goodbye, have a good week!",
    "Bye, have a good month!",
    "Goodbye, have a good month!",
    "Bye, have a good year!",
    "Goodbye, have a good year!",
]

def get_greeting()->str:
    """
    Returns a random greeting from the greeting_styles list.
    """
    return random.choice(greeting_styles)

def get_farewell()->str:
    """
    Returns a random farewell from the farewell_styles list.
    """
    return random.choice(farewell_styles)


def get_current_time()->str:
    """
    Returns the current time.
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")