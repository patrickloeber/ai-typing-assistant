from dataclasses import asdict
from functools import partial
import random
import time
from typing import Any, Dict, List, Tuple
from typing import List
from llm import query_prompt
import pandas as pd
from ollama_config import OLLAMA_CONFIG
from parser import PromptResult, extract_results

NEWLINE = "\n"

WEIGHTED_LABELS = {
    "CURRENT-SMOKER": {"weight": 2, "reason": "the person is a smoker"},
    "NEVER-SMOKED": {"weight": 1, "reason": "the person has never smoked"},
    "PAST-SMOKER": {"weight": 4, "reason": "the person quit smoking in the past"},
    "TOBACCO-USER": {"synonym_of": "NEVER-SMOKED"},
    "NEVER-SMOKER": {"synonym_of": "NEVER-SMOKED"},
}


def build_label_prompt(label, reason):
    return f"Return the label {label}, if {reason}"


def get_weight(weighted_labels: Dict[str, Any], k: str) -> Tuple[str, int]:
    if k in weighted_labels:
        v = weighted_labels[k]
        if "weight" in v:
            return str(k), int(v["weight"])
        elif "synonym_of" in v:
            new_key = v["synonym_of"]
            return str(new_key), int(weighted_labels[new_key]["weight"])
        else:
            return str(k), int(-1)
    else:
        return str(k), int(-1)


label_lookup = partial(get_weight, WEIGHTED_LABELS)

# weighted_labels = {i[0]:i[1] for i in [label_lookup(k, v) for  k,v in WEIGHTED_LABELS.items()]}


def build_prompt(text_to_check) -> str:
    # Qualify each label with an assertion of LOW, MEDIUM, or HIGH probability.
    enumerated_points: Dict[int, str] = build_enumerated_points(text_to_check)

    prefix = [
        "This is an exercise to label sentences to indicate smoking status for people.",
        # "marijuana or chewing tobacco as part of the labeling.",
        "The only permitted labels for this activity are CURRENT-SMOKER, PAST-SMOKER, and NEVER-SMOKED.  Do not use or create any new labels."
        "The following rule should be applied when assigning labels:"
        "- Do not include references to the following terms as part of the decision:"
        "   - marijuana,",
        "   - pot, or",
        "   - chewing tobacco.",
        "- Present tense use of the verb \"smoke\" indicates CURRENT-SMOKER"
        "- References to cigars or pipes indicate CURRENT-SMOKER"
        "Each of following numbered phrases represent an assertion about smoking status for different people.",
    ]

    comments = enumerated_points.values()

    suffix: List[str] = [
        "Return only one of the following labels:",
        "   - Return the label CURRENT-SMOKER, if the person is a smoker,",
        "   - Return the label PAST-SMOKER, if the person quit smoking in the past, or",
        "   - Return the label NEVER-SMOKED, if the person has never smoked.",
        NEWLINE,
        "Return only the corrected label, don't include a preamble.",
    ]
    prompt_pieces: List[str] = []
    prompt_pieces.extend(prefix)
    prompt_pieces.append(NEWLINE)
    prompt_pieces.extend(comments)
    prompt_pieces.append(NEWLINE)
    prompt_pieces.extend(suffix)

    prompt_text = "\n".join(prompt_pieces)

    return prompt_text


def build_enumerated_points(text_to_check) -> Dict[int, str]:
    return {idx: f"{(idx+1)}. {txt.strip()}" for idx, txt in enumerate(text_to_check)}


if __name__ == "__main__":

    MAX_NUMBER_COMMENTS = 10

    start_time = time.time()

    query_label = "Smoking Status"

    text_to_check = []
    with open(
        r"X:\_\Project_Deppen_Lung-Cancer\Deppen-HF-Comments-Processing\__archive\samples\.non_phi_samples\smoke\smoke_mock_data.txt"
    ) as fh:
        text_to_check = fh.readlines()

    # random.shuffle(text_to_check)
    if MAX_NUMBER_COMMENTS:
        text_to_check = text_to_check[0:MAX_NUMBER_COMMENTS]

    prompt_text = build_prompt(text_to_check)

    response: None | str = query_prompt(prompt_text)

    prompt_results: List[PromptResult] = [
        x for x in extract_results(response, WEIGHTED_LABELS, label_lookup) if x
    ]

    assert len(text_to_check) == len(prompt_results)
    for idx, p in enumerate(prompt_results):
        prompt_results[idx].comment = text_to_check[idx]

    df: pd.DataFrame = pd.DataFrame.from_records(
        [asdict(x).values() for x in prompt_results]
    )
    df.columns = ["#", "label", "Comment"]
    query_label_file_name: str = query_label.replace(" ", "_").rstrip().lower()
    with open(
        rf"X:\_\NLPSSC\ai-typing-assistant\_output\result_{query_label_file_name}.md",
        "w",
    ) as fh:
        fh.write(f"# Results for query: {query_label.title()}{NEWLINE}{NEWLINE}")
        fh.write(f"## Prompt{NEWLINE}{NEWLINE}")
        fh.write(
            f"<pre>{NEWLINE}{NEWLINE}{prompt_text.replace(f'{NEWLINE}{NEWLINE}', NEWLINE)}{NEWLINE}{NEWLINE}</pre>{NEWLINE}{NEWLINE}"
        )
        fh.write(f"## Results{NEWLINE}{NEWLINE}")
        fh.write(df.to_markdown(index=False))

        end_time = time.time()

        fh.write(f"{NEWLINE}")
        fh.write(f"## Metrics{NEWLINE}{NEWLINE}")
        fh.write(f"Total Processing Time: {round((end_time - start_time), 2)} secs")
        fh.write(f"{NEWLINE}{NEWLINE}")
        fh.write(f"## Configuration{NEWLINE}{NEWLINE}")
        fh.write(f"LLM model: {OLLAMA_CONFIG['model']}")
