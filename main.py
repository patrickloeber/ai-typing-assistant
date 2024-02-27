from pynput import keyboard
from pynput.keyboard import Key, Controller
import pyperclip
import time
import httpx
from string import Template


controller = Controller()

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
OLLAMA_CONFIG = {
    "model": "mistral:7b-instruct-v0.2-q4_K_S",
    "keep_alive": "5m",
    "stream": False,
}

PROMPT_TEMPLATE = Template(
    """Fix all typos and casing and punctuation in this text, but preserve all new line characters:

$text

Return only the corrected text, don't include a preamble.
"""
)


def fix_text(text):
    prompt = PROMPT_TEMPLATE.substitute(text=text)
    response = httpx.post(
        OLLAMA_ENDPOINT,
        json={"prompt": prompt, **OLLAMA_CONFIG},
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    if response.status_code != 200:
        return None
    return response.json()["response"].strip()


def fix_current_line():
    # Cmd + Shift + Left
    controller.press(Key.cmd)
    controller.press(Key.shift)
    controller.press(Key.left)

    controller.release(Key.cmd)
    controller.release(Key.shift)
    controller.release(Key.left)

    fix_selection()


def fix_selection():
    # 1. copy to clipboard
    with controller.pressed(Key.cmd):
        controller.tap("c")
    # 2. get the text from clipboard
    time.sleep(0.1)
    text = pyperclip.paste()

    # 3. fix the text
    fixed_text = fix_text(text)

    # 4. copy back to clipboard
    pyperclip.copy(fixed_text)
    time.sleep(0.1)
    # 5. insert text
    with controller.pressed(Key.cmd):
        controller.tap("v")


def on_f9():
    fix_current_line()


def on_f10():
    fix_selection()


with keyboard.GlobalHotKeys({"<101>": on_f9, "<109>": on_f10}) as h:
    h.join()
