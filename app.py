import json
import urllib.request
from pathlib import Path
import logging

BASE_DIR = Path(__file__).resolve().parent
NOTES_DIR = BASE_DIR / "notes"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_JSON = OUTPUT_DIR / "graph.json"
OUTPUT_HTML = OUTPUT_DIR / "index.html"
OLLAMA_URL = "http://localhost:11434/api/generate"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def query_local_qwen(note_title, note_content):
    prompt = f"""System: You are an expert code and JSON generation assistant. Your task is to analyze markdown note content and extract knowledge graph elements.
Input Note Title: {note_title}
Input Note Content: {note_content}

Output Requirement: Respond ONLY with a valid JSON snippet containing extracted tags and conceptual links. Do not include markdown code fences, conversational filler, or explanations.

JSON Schema Structure:
{{"concepts": ["concept_1", "concept_2", "concept_3"], "links_to": ["related_topic_1"]}}
"""
    payload = {
        "model": "qwen2.5:7b",
        "prompt": prompt,
        "stream": False
    }
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result.get("response", "")
    except Exception as e:
        logging.error(f"Error communicating with local Ollama: {e}")
        return ""

def generate_d3_html():
    """Generates an interactive D3.js force-directed graph viewer."""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>LinkNode Knowledge Graph</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body { background: #0f172a; color: #f8fafc; font-family: sans-serif; margin: 0; overflow: hidden; }
        svg { width: 100vw; height: 100vh; }
        .node { stroke: #fff; stroke-width: 1.5px; cursor: pointer; }
        .link { stroke: #475569; stroke-opacity: 0.6; stroke-width: 1.5px; }
        .node-label { fill: #e2e8f0; font-size: 11px; pointer-events: none; }
    </style>
</head>
<body>
    <svg></svg>
    <script>
        d3.json("graph.json").then(data => {
            const width = window.innerWidth, height = window.innerHeight;
            const svg = d3.select("svg").attr("viewBox", [0, 0, width, height]);

            const simulation = d3.forceSimulation(data.nodes)
                .force("link", d3.forceLink(data.links).id(d => d.id).distance(80))
                .force("charge", d3.forceManyBody().strength(-200))
                .force("center", d3.forceCenter(width / 2, height / 2));

            const link = svg.append("g").selectAll("line").data(data.links).join("line").attr("class", "link");
            
            const node = svg.append("g").selectAll("circle").data(data.nodes).join("circle")
                .attr("class", "node")
                .attr("r", d => d.group === 1 ? 7 : 4)
                .attr("fill", d => d.group === 1 ? "#38bdf8" : "#f43f5e")
                .call(d3.drag()
                    .on("start", (event, d) => { if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
                    .on("drag", (event, d) => { d.fx = event.x; d.fy = event.y; })
                    .on("end", (event, d) => { if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }));

            const label = svg.append("g").selectAll("text").data(data.nodes).join("text")
                .attr("class", "node-label")
                .text(d => d.id)
                .attr("dx", 8).attr("dy", 3);

            simulation.on("tick", () => {
                link.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
                node.attr("cx", d => d.x).attr("cy", d => d.y);
                label.attr("x", d => d.x).attr("y", d => d.y);
            });
        });
    </script>
</body>
</html>
"""
    OUTPUT_HTML.write_text(html_content, encoding="utf-8")

def build_graph():
    NOTES_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    nodes = []
    edges = []
    canon = {}  # normalized key -> first label seen, so "Python"/"python"/"PYTHON" become one node

    def label_for(name, group):
        key = " ".join(str(name).lower().replace("_", " ").replace("-", " ").split())
        if key not in canon:
            canon[key] = str(name).strip()
            nodes.append({"id": canon[key], "group": group})
        return canon[key]

    # RECURSIVE SCAN: grabs .md files in root AND all subfolders like 27NOV2026
    md_files = list(NOTES_DIR.rglob("*.md"))
    if not md_files:
        logging.info(f"No markdown files found in {NOTES_DIR} or its subfolders!")
        return

    for file_path in md_files:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        title = label_for(file_path.stem, 1)

        response_text = query_local_qwen(title, content)
        if response_text:
            try:
                clean_text = response_text.replace("```json", "").replace("```", "").strip()
                response_data = json.loads(clean_text)
                for concept in response_data.get("concepts", []):
                    edges.append({"source": title, "target": label_for(concept, 2)})
                # Every link target gets a node too; force-graph refuses to draw
                # if any link points at an id that isn't in "nodes".
                for link in response_data.get("links_to", []):
                    edges.append({"source": title, "target": label_for(link, 3)})
            except json.JSONDecodeError:
                logging.error(f"Failed to parse Qwen response: {response_text}")
        else:
            logging.warning(f"No response from Qwen for note: {title}")

    # Deduplicate nodes and links to prevent graph fragmentation
    unique_nodes = nodes  # already unique via label_for()
    
    seen_edges = set()
    unique_edges = []
    for e in edges:
        source_id = e["source"]["id"] if isinstance(e["source"], dict) else e["source"]
        target_id = e["target"]["id"] if isinstance(e["target"], dict) else e["target"]
        edge_key = (source_id, target_id)
        if edge_key not in seen_edges and source_id != target_id:
            seen_edges.add(edge_key)
            unique_edges.append({"source": source_id, "target": target_id})

    # Safety net: never ship a link to a missing node (it blanks the whole page).
    valid_node_ids = {n["id"] for n in unique_nodes}
    clean_edges = [e for e in unique_edges
                   if e["source"] in valid_node_ids and e["target"] in valid_node_ids]
    dropped = len(unique_edges) - len(clean_edges)
    if dropped:
        logging.warning(f"Dropped {dropped} link(s) pointing at missing nodes")

    graph_data = {"nodes": list(unique_nodes), "links": clean_edges}
    OUTPUT_JSON.write_text(json.dumps(graph_data, indent=2), encoding="utf-8")
    generate_d3_html()
    logging.info(f"SUCCESS: graph.json and index.html written to {OUTPUT_DIR}")

if __name__ == "__main__":
    build_graph()