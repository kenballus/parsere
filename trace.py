import functools
import json
import subprocess
import sys

import tqdm
import networkx

from archr.targets import DockerImageTarget  # type: ignore
from archr.analyzers import QEMUTracerAnalyzer  # type: ignore
from archr.analyzers.qemu_tracer import QEMUBBLTrace  # type: ignore
from networkx import DiGraph


def color_from_label(label: str) -> str:
    h: int = abs(hash(label))
    hue: int = int(((h & 0xFF) / 256) * 360)  # In degrees

    # Scale sat and val to [0.8, 1] because I want the color to be bright
    sat: float = (((h >> 8) & 0xFF) / 256) * 0.2 + 0.8
    val: float = (((h >> 16) & 0xFF) / 256) * 0.2 + 0.8

    # From https://en.wikipedia.org/wiki/HSL_and_HSV#HSV_to_RGB
    c: float = val * sat
    hue_prime: int = hue // 60
    x: float = c * (1 - abs(hue_prime % 2 - 1))

    r: float
    g: float
    b: float
    if hue_prime < 1:
        r, g, b = c, x, 0
    elif 1 <= hue_prime < 2:
        r, g, b = x, c, 0
    elif 3 <= hue_prime < 4:
        r, g, b = 0, c, x
    elif 4 <= hue_prime < 5:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x

    r_str, g_str, b_str = (hex(int(c * 256))[2:].zfill(2) for c in (r, g, b))

    return f"#{r_str}{g_str}{b_str}"


def main(image_id: str, labelled_test_inputs: list[tuple[str, bytes]]) -> None:
    labels, test_inputs = map(list, zip(*labelled_test_inputs))

    edge_sets: list[set[tuple[int, int]]] = []

    with DockerImageTarget(image_id).build().start() as target:
        tracer: QEMUTracerAnalyzer = QEMUTracerAnalyzer(target)
        tracer.nock()
        for prefix in tqdm.tqdm(test_inputs, desc="Executing test_inputs"):
            fire_result: QEMUBBLTrace = tracer.fire(testcase=prefix).trace
            block_trace: list[int] = [fire_result[i] for i in range(len(fire_result))]
            edge_sets.append(set(zip(block_trace, block_trace[1:])))

    edges_seen: set[tuple[int, int]] = set()
    labelled_edges: set[tuple[int, int]] = set()
    g: DiGraph = DiGraph()
    for i, (edge_set, prefix, label) in enumerate(zip(edge_sets, test_inputs, labels)):
        if len(prefix) > 0:
            for edge in functools.reduce(set.__and__, edge_sets[i:]) - edges_seen:
                # - This is the first time we've seen this edge
                # - This edge appears in all subsequent edge sets
                g.add_edge(*edge, color=color_from_label(label), xlabel=label)
                labelled_edges.add(edge)
        edges_seen |= edge_set

    # Add the rest of the edges we encountered
    g.add_edges_from(edges_seen - labelled_edges)

    for node in g.nodes():
        edge_colors: set[str | None] = set(data.get("color") for _, _, data in list(g.in_edges(node, data=True)) + list(g.out_edges(node, data=True)))
        if len(edge_colors) == 1 and None not in edge_colors:
            g.nodes[node]["style"] = "filled"
            g.nodes[node]["fillcolor"] = next(iter(edge_colors))

    with DockerImageTarget(image_id).build().start() as target:
        argv: list[str] = ["/usr/bin/addr2line", "-e", target.target_path] + [hex(node) for node in g.nodes()]
        locations: list[str] = target.run_command(args=argv, stdout=subprocess.PIPE).stdout.read().strip().decode("ascii").split("\n")
        for node, location in zip(g.nodes(), locations):
            if "/" in location:
                location = location.split("/")[-1]
            g.nodes[node]["label"] = f"{hex(node)} ({location})"
            g.nodes[node]["shape"] = "box"

    networkx.drawing.nx_pydot.to_pydot(g).write_raw("out.dot")


RULE_NAMES: list[str] = ["scheme", "user", "password", "host", "port", "path", "query", "frag"]
intermediate_result: str = ""

def walk(pt: dict, result: list[bytes] | None = None, rules: list[str] | None = None, depth: int = 0):
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
                result.append(intermediate_result.encode("latin1"))
            else:
                result.append(result[-1] + intermediate_result.encode("latin1"))

            intermediate_result = ""
    else:
        # Terminal
        intermediate_result += text

    if "children" in pt:
        for child in pt["children"]:
            walk(child, result, rules, depth + 1)

    if depth == 0:
        result.append(text.encode("latin1"))
        return list(zip([""] + rules, result))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <docker_image_id>")
        print(f"    (Reads ANTLR JSON from stdin)")
        exit(1)

    with open("/dev/stdin") as f:
        j: dict = json.load(f)
    pt: dict = j["parse_tree"]

    main(sys.argv[1], walk(pt))
