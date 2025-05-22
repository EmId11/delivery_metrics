import json
import random

def guess_unit_and_range(metric_name):
    name = metric_name.lower()
    if "self-assessment score" in name or "rate" in name or "score" in name:
        return "score", "Score (0–10)", 0, 10, 1
    if "%" in name or "percent" in name or "coverage" in name:
        return "%", "%", 0, 100, 1
    if "sprint" in name and ("avg number" in name or "number of sprints" in name):
        return "sprints", "Number of Sprints", 0, 8, 1
    if "# of" in name or "number of" in name or "count" in name:
        return "count", "Count", 0, 120, 0
    if "days" in name or "duration" in name or "age" in name:
        return "days", "Days", 0, 30, 1
    if "hours" in name or "hour" in name:
        return "hours", "Hours", 0, 80, 1
    if "minutes" in name:
        return "minutes", "Minutes", 0, 180, 0
    if "touch time" in name or "total time" in name:
        return "days", "Days", 0, 30, 1
    if "index" in name:
        return "index", "Index", 0, 100, 1
    if "maintainability index" in name:
        return "index", "Maintainability Index", 0, 100, 1
    if "complexity" in name or "cyclomatic" in name:
        return "complexity", "Complexity Score", 0, 30, 1
    return "count", "Count", 0, 100, 0

def generate_realistic_timeseries(unit, minval, maxval, decimals):
    base = random.uniform(minval, maxval)
    timeseries = [base]
    for i in range(11):
        if random.random() < 0.2 and i > 2:
            change = random.uniform(-0.4, 0.4) * (maxval - minval)
        else:
            change = random.uniform(-0.1, 0.1) * (maxval - minval)
        val = max(min(timeseries[-1] + change, maxval), minval)
        timeseries.append(val)
    for i in range(2, len(timeseries)-2):
        if random.random() < 0.12:
            timeseries[i] += (random.uniform(-0.3, 0.3) * (maxval - minval))
            timeseries[i] = max(min(timeseries[i], maxval), minval)
    return [round(v, decimals) for v in timeseries]

def update_metrics(metrics):
    for metric in metrics:
        unit, y_label, minv, maxv, decs = guess_unit_and_range(metric["metric_name"])
        metric["unit"] = unit
        metric["y_axis_label"] = y_label
        metric["timeseries"] = generate_realistic_timeseries(unit, minv, maxv, decs)
        metric["value"] = round(metric["timeseries"][-1], decs)
    return metrics

def process_tree(node):
    if "metrics" in node and isinstance(node["metrics"], list):
        node["metrics"] = update_metrics(node["metrics"])
    if "children" in node and isinstance(node["children"], list):
        for child in node["children"]:
            process_tree(child)
    return node

with open("delivery_health_tree_structured.json") as f:
    data = json.load(f)

data_updated = [process_tree(node) for node in data]

with open("delivery_health_tree_structured_enhanced.json", "w") as f:
    json.dump(data_updated, f, indent=2)

print("DONE. Check delivery_health_tree_structured_enhanced.json")