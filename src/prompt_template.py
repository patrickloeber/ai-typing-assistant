import os
from string import Template  # noqa


def get_prompt_template(text):
#     return Template("""
                    
# Return only the corrected text, don't include a preamble. Fix all typos and casing and punctuation in this text, but preserve all new line characters:

# $text
                    
# """)
    prompt_pieces = [
        "Fix all typos and punctuation in the following text, preserving newline characters.",
        text,
        "Return only the corrected text, and do not include a preamble."
    ]
    return "\n".join(prompt_pieces)
