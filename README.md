# AI powered typing assistant with Ollama

## Get Started

### 1. Set up Ollama

Ollama Installation: https://github.com/ollama/ollama

Run `ollama run mistral:7b-instruct-v0.2-q4_K_S`

Mistal 7B Instruct works well for this task, but feel free to try other models, too :)

### 2. Install dependencies
```
pip install pynput pyperclip httpx
```

- pynput: https://pynput.readthedocs.io/en/latest/
- pyperclip: https://github.com/asweigart/pyperclip
- httpx: https://github.com/encode/httpx/

### 3. Run it

Start the assistant:

```
python main.py
```

Hotkeys:

- F9: Fixes the current line (without having to select the text)
- F10: Fixes the current selection


## Customize

Hotkeys, prompt, and Ollama config can be easily customized in the code.

For example, here are some prompt templates you can try:

```python
from string import Template

PROMPT_TEMPLATE_FIX_TEXT = Template(
    """Fix all typos and casing and punctuation in this text, but preserve all new line characters:

$text

Return only the corrected text."""
)

PROMPT_TEMPLATE_GENERATE_TEXT = Template(
    """Generate a snarky paragraph with 3 sentences about the following topic:

$text

Return only the corrected text."""
)

PROMPT_TEMPLATE_SUMMARIZE_TEXT = Template(
    """Summarize the following text in 3 sentences:

$text

Return only the corrected text."""
)
```