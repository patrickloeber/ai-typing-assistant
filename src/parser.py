from dataclasses import dataclass, field
from functools import partial
import re
from typing import Callable, Dict, List, Tuple


@dataclass
class PromptResult:
    index: int
    label: str
    comment: str | None = field(default=None)


def extract_result(
    result_pattern: re.Pattern[str],
    label_lookup: Callable[[str], Tuple[str, int]],
    response_entry: str,
) -> PromptResult | None:
    matches = result_pattern.findall(response_entry)
    # match = result_pattern.search(response_entry)
    if matches:

        try:
            index_match = re.search(r"^(\d+)(?=\.)", response_entry, re.IGNORECASE)
            if index_match:
                index = int(index_match.group(0))
                found_weighted_labels = [label_lookup(m) for m in matches]

                # found_weighted_labels = [(m, weighted_labels[m]) for m in matches if m in weighted_labels.keys()]
                asserted_label = max(found_weighted_labels, key=lambda x: x[1])
                label = asserted_label[0]
        except Exception as ex:
            print(ex)

        return PromptResult(index=index, label=label)
    else:
        return None


def extract_results(
    response: str, weighted_labels: Dict[str, int], label_lookup
) -> List[PromptResult | None]:

    result_pattern = update_weighted_labels_with_catchall(weighted_labels)

    extract_result_partial = partial(extract_result, result_pattern, label_lookup)

    response_entries = response.split("\n")

    return [extract_result_partial(x) for x in response_entries]


def update_weighted_labels_with_catchall(weighted_labels):
    assigned_labels = list(weighted_labels.keys())
    assigned_labels.append(r"\b[A-Z_]{3,}\b")
    result_pattern: re.Pattern[str] = re.compile(r"(" + "|".join(assigned_labels) + ")")

    return result_pattern
