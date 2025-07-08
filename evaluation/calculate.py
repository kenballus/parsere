import os
import json

json_dir = os.path.join(os.path.dirname(__file__), 'json_output')

final = {"gpt": 0, "deepseek": 0, "total": 0}

labelwise = {"curl": {}, "apr": {}}
for filename in os.listdir(json_dir):
    if "curl" in filename:
        tool = "curl"
    else:
        tool = "apr"
    if filename.endswith('.json'):
        filepath = os.path.join(json_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for result in data:
                label = result.get('metadata', {}).get('label')
                gpt = result.get('gpt', {}).get('label')
                deepseek = result.get('deepseek', {})
                deepseek = deepseek.get('label', None) if deepseek else None

                if label not in labelwise[tool]:
                    labelwise[tool][label] = {"gpt": 0, "deepseek": 0, "total": 0}
                labelwise[tool][label]["total"] += 1
                if label == gpt:
                    labelwise[tool][label]['gpt'] += 1
                if label == deepseek:
                    labelwise[tool][label]['deepseek'] += 1

for key in labelwise["curl"].keys():
    print(f'{key} & {labelwise["curl"][key]["gpt"]/labelwise["curl"][key]["total"]*100:.2f} & {labelwise["curl"][key]["deepseek"]/labelwise["curl"][key]["total"]*100:.2f} & {labelwise["curl"][key]["total"]} \\\\')
for key in labelwise["apr"].keys():
    print(f'{key} & {labelwise["apr"][key]["gpt"]/labelwise["apr"][key]["total"]*100:.2f} & {labelwise["apr"][key]["deepseek"]/labelwise["apr"][key]["total"]*100:.2f} & {labelwise["apr"][key]["total"]} \\\\')