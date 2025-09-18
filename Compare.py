import gradio as gr
import matplotlib.pyplot as plt

# Romania graph
graph = {
    "Arad": {"Zerind": 75, "Sibiu": 140, "Timisoara": 118},
    "Zerind": {"Arad": 75, "Oradea": 71},
    "Oradea": {"Zerind": 71, "Sibiu": 151},
    "Sibiu": {"Arad": 140, "Oradea": 151, "Fagaras": 99, "Rimnicu Vilcea": 80},
    "Fagaras": {"Sibiu": 99, "Bucharest": 211},
    "Rimnicu Vilcea": {"Sibiu": 80, "Pitesti": 97, "Craiova": 146},
    "Pitesti": {"Rimnicu Vilcea": 97, "Craiova": 138, "Bucharest": 101},
    "Timisoara": {"Arad": 118, "Lugoj": 111},
    "Lugoj": {"Timisoara": 111, "Mehadia": 70},
    "Mehadia": {"Lugoj": 70, "Drobeta": 75},
    "Drobeta": {"Mehadia": 75, "Craiova": 120},
    "Craiova": {"Drobeta": 120, "Pitesti": 138, "Rimnicu Vilcea": 146},
    "Bucharest": {"Fagaras": 211, "Pitesti": 101, "Giurgiu": 90, "Urziceni": 85},
    "Urziceni": {"Bucharest": 85, "Hirsova": 98, "Vaslui": 142},
    "Hirsova": {"Urziceni": 98, "Eforie": 86},
    "Eforie": {"Hirsova": 86},
    "Vaslui": {"Urziceni": 142, "Iasi": 92},
    "Iasi": {"Vaslui": 92, "Neamt": 87},
    "Neamt": {"Iasi": 87},
    "Giurgiu": {"Bucharest": 90},
}

# Heuristic (SLD to Bucharest)
hSLD = {
    "Arad": 366, "Bucharest": 0, "Craiova": 160, "Drobeta": 242, "Eforie": 161,
    "Fagaras": 176, "Giurgiu": 77, "Hirsova": 151, "Iasi": 226, "Lugoj": 244,
    "Mehadia": 241, "Neamt": 234, "Oradea": 380, "Pitesti": 100,
    "Rimnicu Vilcea": 193, "Sibiu": 253, "Timisoara": 329,
    "Urziceni": 80, "Vaslui": 199, "Zerind": 374
}

positions = {
    "Arad": (1, 3), "Zerind": (0, 4), "Oradea": (0.5, 5), "Sibiu": (2, 4),
    "Fagaras": (3, 5), "Rimnicu Vilcea": (3, 3), "Pitesti": (4, 2.5),
    "Timisoara": (0, 2), "Lugoj": (1, 1.5), "Mehadia": (2, 1),
    "Drobeta": (2.5, 0.5), "Craiova": (3.5, 1.5), "Bucharest": (5, 2),
    "Urziceni": (6, 2.5), "Hirsova": (7, 3), "Eforie": (8, 2.5),
    "Vaslui": (6, 4), "Iasi": (6.5, 5), "Neamt": (6.5, 6), "Giurgiu": (5, 1)
}

# Helpers
def reconstruct(parent, node):
    path = []
    while node:
        path.insert(0, node)
        node = parent.get(node)
    return path

def path_cost(path):
    return sum(graph[path[i]][path[i+1]] for i in range(len(path)-1))

# GBFS
def gbfs_trace(start, goal):
    trace = []
    frontier = [{"name": start, "h": hSLD[start]}]
    expanded, parent = set(), {}
    while frontier:
        frontier.sort(key=lambda x: x["h"])
        node = frontier.pop(0)
        if node["name"] in expanded: continue
        expanded.add(node["name"])
        path = reconstruct(parent, node["name"])
        snap_frontier = sorted(frontier, key=lambda x: x["h"])
        trace.append({"current": node, "frontier": snap_frontier, "expanded": expanded.copy(),
                      "path": path, "goal": goal, "algo": "GBFS"})
        if node["name"]==goal: return trace
        for nbr in graph[node["name"]]:
            if nbr not in expanded:
                parent[nbr] = node["name"]
                frontier.append({"name": nbr, "h": hSLD[nbr]})
    return trace

# A*
def astar_trace(start, goal):
    trace = []
    frontier = [{"name": start, "g": 0, "h": hSLD[start], "f": hSLD[start]}]
    expanded, parent, g = set(), {}, {start:0}
    while frontier:
        frontier.sort(key=lambda x: x["f"])
        node = frontier.pop(0)
        if node["name"] in expanded: continue
        expanded.add(node["name"])
        path = reconstruct(parent, node["name"])
        snap_frontier = sorted(frontier, key=lambda x: x["f"])
        trace.append({"current": node, "frontier": snap_frontier, "expanded": expanded.copy(),
                      "path": path, "goal": goal, "algo": "A*"})
        if node["name"]==goal: return trace
        for nbr, cost in graph[node["name"]].items():
            new_g = g[node["name"]] + cost
            if nbr not in g or new_g<g[nbr]:
                g[nbr]=new_g
                parent[nbr]=node["name"]
                frontier.append({"name": nbr, "g": new_g, "h": hSLD[nbr], "f": new_g+hSLD[nbr]})
    return trace

# RBFS simplified like GBFS for visualization
def rbfs_trace(start, goal):
    return gbfs_trace(start, goal)

# Map plot
def plot_map(state):
    fig, ax = plt.subplots(figsize=(12,9))
    for a in graph:
        for b, cost in graph[a].items():
            if a<b:
                x1,y1 = positions[a]; x2,y2 = positions[b]
                ax.plot([x1,x2],[y1,y2], 'k-', alpha=0.3)
                ax.text((x1+x2)/2,(y1+y2)/2,str(cost),fontsize=8,color='gray')
    if len(state['path'])>1:
        for i in range(len(state['path'])-1):
            x1,y1=positions[state['path'][i]]; x2,y2=positions[state['path'][i+1]]
            ax.plot([x1,x2],[y1,y2],'g-',linewidth=3)
    for n,(x,y) in positions.items():
        color='white'
        if n in state['expanded']: color='lightgray'
        if n in [f['name'] for f in state['frontier']]: color='orange'
        if n in state['path']: color='limegreen'
        if n==state['current']['name']: color='dodgerblue'
        ax.scatter(x,y,s=2500,c=color,edgecolors='black',zorder=3)
        ax.text(x,y+0.3,n,ha='center',fontsize=10,weight='bold')
        # Values
        algo = state.get("algo")
        g_val = h_val = f_val = None
        h_val = hSLD[n]
        if n==state['current']['name']:
            g_val = state['current'].get('g')
            f_val = state['current'].get('f')
        else:
            for f in state['frontier']:
                if f['name']==n:
                    g_val = f.get('g')
                    f_val = f.get('f')
                    h_val = f.get('h',h_val)
        if g_val is not None:
            if algo=="A*":
                ax.text(x,y+0.1,f"g={g_val}",ha='center',fontsize=8)
                ax.text(x,y-0.1,f"h={h_val}",ha='center',fontsize=8)
                ax.text(x,y-0.3,f"f={f_val}",ha='center',fontsize=8)
            else:
                ax.text(x,y-0.05,f"h={h_val}",ha='center',fontsize=8)
        else:
            ax.text(x,y-0.05,f"h={h_val}",ha='center',fontsize=8)
    ax.set_axis_off()
    return fig

# Session
session={"trace":[],"step":0}

def start_search(start, goal, algo):
    if algo=="GBFS": session["trace"]=gbfs_trace(start, goal)
    elif algo=="A*": session["trace"]=astar_trace(start, goal)
    else: session["trace"]=rbfs_trace(start, goal)
    session["step"]=0
    return show_step()

def step_forward():
    if session["step"]<len(session["trace"])-1: session["step"]+=1
    return show_step()

def step_back():
    if session["step"]>0: session["step"]-=1
    return show_step()

def show_step():
    if not session["trace"]: return "No trace yet.", "", None
    s = session["trace"][session["step"]]
    node = s['current']
    frontier_table="| Node | g(n) | h(n) | f(n)=g+h |\n|------|------|------|-----------|\n"
    for f in s['frontier']:
        mark = "✅" if f['name']==node['name'] else ""
        g_val = f.get('g','-'); h_val=f.get('h','-'); f_val=f.get('f','-')
        frontier_table += f"| {f['name']} | {g_val} | {h_val} | {f_val} {mark} |\n"
    path_edges = " + ".join(str(graph[s['path'][i]][s['path'][i+1]]) for i in range(len(s['path'])-1))
    g_val = node.get('g','-'); h_val=node.get('h','-'); f_val=node.get('f','-')
    reason = f"g(n) = sum of edge costs along path: {path_edges} = {g_val}\n" \
             f"h(n) = heuristic: {h_val}\n" \
             f"f(n)=g+h = {f_val}\n" \
             f"Selected **{node['name']}** (lowest f/h as per {s['algo']})"
    step_info = f"### Step {session['step']+1}\n**Expanded:** {', '.join(s['expanded'])}\n**Path so far:** {' → '.join(s['path'])}"
    selected_info = f"## 🟦 Selected Node\n➡️ **{node['name']}**"
    return step_info + "\n\n" + reason, selected_info + "\n\n" + frontier_table, plot_map(s)

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("# 🌍 Romania Search Visualizer — GBFS / A* / RBFS")
    with gr.Row():
        start_city = gr.Dropdown(list(graph.keys()), label="Start City", value="Arad")
        goal_city = gr.Dropdown(list(graph.keys()), label="Goal City", value="Bucharest")
        algo_choice = gr.Radio(["GBFS","A*","RBFS"], label="Algorithm", value="A*")
    with gr.Row():
        btn_start = gr.Button("▶️ Start Search")
        btn_back = gr.Button("⬅️ Back")
        btn_next = gr.Button("➡️ Next Step")
    with gr.Row():
        output_text = gr.Markdown()
        frontier_text = gr.Markdown()
    with gr.Row():
        output_plot = gr.Plot()
    btn_start.click(start_search, [start_city, goal_city, algo_choice], [output_text, frontier_text, output_plot])
    btn_next.click(step_forward, None, [output_text, frontier_text, output_plot])
    btn_back.click(step_back, None, [output_text, frontier_text, output_plot])

demo.launch()
