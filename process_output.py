import json
import sys


RULE_NAMES: list[str] = ["scheme", "user", "password", "host", "port", "path", "query", "frag"]
intermediate_result: str = ""

def walk(pt: dict, result: list[str] | None = None, rules: list[str] | None = None, depth: int = 0):
    global intermediate_result
    if result is None:
        result = []
    if rules is None:
        rules = []

    text: str = pt['text'].rstrip("<EOF>")

    if "ruleName" in pt:
        rule_name: str = pt['ruleName']
        if rule_name in RULE_NAMES:
            rules.append(rule_name)
            if len(result) == 0:
                result.append(intermediate_result)
            else:
                result.append(result[-1] + intermediate_result)

            intermediate_result = ""
    else:
        # Terminal
        intermediate_result += text

    if "children" in pt:
        for child in pt["children"]:
            walk(child, result, rules, depth + 1)

    if depth == 0:
        result.append(text)
        return list(zip([""] + rules, result))

with open("/dev/stdin") as f:
    j: dict = json.load(f)

pt: dict = j["parse_tree"]
print(walk(pt))
