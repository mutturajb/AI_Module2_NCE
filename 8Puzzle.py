import heapq
import gradio as gr
import matplotlib.pyplot as plt

# Goal state for the 8-puzzle
goal_state = (0, 1, 2, 3, 4, 5, 6, 7, 8)

# Manhattan distance heuristic with detailed explanation
def manhattan_details(state):
    details = []
    dist = 0
    for i, val in enumerate(state):
        if val == 0:  # skip blank
            continue
        row_cur, col_cur = divmod(i, 3)
        row_goal, col_goal = divmod(goal_state.index(val), 3)

        row_diff = abs(row_cur - row_goal)
        col_diff = abs(col_cur - col_goal)
        d = row_diff + col_diff

        explanation = (
            f"Tile {val}:\n"
            f"   Current position = ({row_cur},{col_cur})\n"
            f"   Goal position    = ({row_goal},{col_goal})\n"
            f"   Row difference   = |{row_cur} - {row_goal}| = {row_diff}\n"
            f"   Col difference   = |{col_cur} - {col_goal}| = {col_diff}\n"
            f"   Manhattan distance = {row_diff} + {col_diff} = {d}\n"
        )
        details.append(explanation)
        dist += d
    return dist, details

def manhattan(state):
    dist, _ = manhattan_details(state)
    return dist

# Generate neighbors with move info
def get_neighbors_with_move(state):
    neighbors = []
    i = state.index(0)
    x, y = divmod(i, 3)
    moves = [(-1,0),(1,0),(0,-1),(0,1)]  # Up, Down, Left, Right
    for dx, dy in moves:
        nx, ny = x+dx, y+dy
        if 0 <= nx < 3 and 0 <= ny < 3:
            j = nx*3 + ny
            new_state = list(state)
            new_state[i], new_state[j] = new_state[j], new_state[i]
            moved_tile = state[j]
            neighbors.append((tuple(new_state), moved_tile, j, i))
            # (new state, which tile moved, from index, to index)
    return neighbors

# A* algorithm
def astar(start):
    pq = []
    g = {start: 0}
    f = {start: manhattan(start)}
    came_from = {}
    heapq.heappush(pq, (f[start], start))

    while pq:
        _, current = heapq.heappop(pq)
        if current == goal_state:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path
        for neighbor, moved_tile, _, _ in get_neighbors_with_move(current):
            tentative_g = g[current] + 1
            if neighbor not in g or tentative_g < g[neighbor]:
                came_from[neighbor] = current
                g[neighbor] = tentative_g
                f[neighbor] = tentative_g + manhattan(neighbor)
                heapq.heappush(pq, (f[neighbor], neighbor))
    return None

# Plot puzzle
def plot_puzzle(state, highlight=None):
    fig, ax = plt.subplots(figsize=(5,5))
    ax.set_xlim(0,3); ax.set_ylim(0,3)
    ax.set_xticks([]); ax.set_yticks([])
    for i in range(3):
        for j in range(3):
            val = state[i*3+j]
            color = 'lightgreen' if val==highlight else ('white' if val!=0 else 'lightgray')
            ax.add_patch(plt.Rectangle((j,2-i),1,1,facecolor=color,edgecolor='black'))
            if val != 0:
                ax.text(j+0.5,2-i+0.5,str(val),ha='center',va='center',fontsize=20,weight='bold')
    return fig

# Session state
session = {"solution": [], "moves": [], "step": 0}

def parse_input(text):
    nums = list(map(int, text.replace(","," ").split()))
    return tuple(nums)

# Explain why chosen neighbor
def neighbor_choices_explanation(prev_state, chosen_state, prev_g):
    neighbors = get_neighbors_with_move(prev_state)
    lines = []
    best_f = None
    for neigh, moved_tile, from_pos, to_pos in neighbors:
        g_n = prev_g + 1
        h_n, _ = manhattan_details(neigh)
        f_n = g_n + h_n
        from_r, from_c = divmod(from_pos, 3)
        to_r, to_c = divmod(to_pos, 3)
        label = (
            f"Move tile {moved_tile}:\n"
            f"   From position (row={from_r}, col={from_c})\n"
            f"   To   position (row={to_r}, col={to_c})"
        )
        chosen_marker = "   <-- chosen" if neigh == chosen_state else ""
        lines.append((label, neigh, g_n, h_n, f_n, chosen_marker))
        if best_f is None or f_n < best_f:
            best_f = f_n

    # Build explanation
    expl = ["Neighbors considered:\n"]
    for label, neigh, g_n, h_n, f_n, chosen_marker in lines:
        expl.append(
            f"{label}\n"
            f"   g = {g_n}\n"
            f"   h = {h_n}\n"
            f"   f = {f_n}{chosen_marker}\n"
        )

    # Explain choice
    chosen_line = next(l for l in lines if l[1] == chosen_state)
    chosen_f = chosen_line[4]
    num_best = sum(1 for _,_,_,_,f,_ in lines if f == best_f)
    expl.append("Why chosen?")
    if num_best == 1:
        expl.append(f"   This move was chosen because its f = {chosen_f} is the lowest among all neighbors.")
    else:
        expl.append(
            f"   Multiple moves had the same lowest f = {chosen_f}.\n"
            f"   A* uses a tie-breaking rule: neighbors are explored\n"
            f"   in the order they are generated (Up, Down, Left, Right).\n"
            f"   The first one with the best f is chosen.\n"
            f"   That is why this tile was picked."
        )

    return "\n".join(expl)

# Solve puzzle
def solve_puzzle(start_text):
    start = parse_input(start_text)
    path = astar(start)
    if not path:
        return "❌ No solution found", None
    session["solution"] = path
    session["step"] = 0
    session["moves"] = []
    for k in range(1,len(path)):
        prev, curr = path[k-1], path[k]
        zero_prev, zero_curr = prev.index(0), curr.index(0)
        moved_tile = prev[zero_curr]
        session["moves"].append(moved_tile)
    return show_step()

# Show step
def show_step(step_idx=None):
    if not session["solution"]:
        return "⚠️ Solve first", None
    if step_idx is not None:
        session["step"] = step_idx
    step = session["step"]
    state = session["solution"][step]
    g_val = step
    h_val, h_details = manhattan_details(state)
    f_val = g_val + h_val
    move_desc = "Starting state"
    highlight_tile = None
    explanation = ""

    if step > 0:
        moved_tile = session["moves"][step-1]
        move_desc = f"Tile **{moved_tile}** moved"
        highlight_tile = moved_tile
        prev_state = session["solution"][step-1]
        explanation = neighbor_choices_explanation(prev_state, state, g_val-1)

    info = f"""
### Step {step}/{len(session['solution'])-1}
{move_desc}

**g = {g_val}, h = {h_val}, f = {f_val}**

A* uses f(n) = g(n) + h(n).  
Here:
- g(n) = steps taken so far = {g_val}  
- h(n) = Manhattan distance = {h_val}  
- f(n) = {g_val} + {h_val} = {f_val}  

**Manhattan calculation:**

""" + "\n".join(h_details) + "\n\n" + explanation

    return info, plot_puzzle(state, highlight_tile)

# Step controls
def step_forward():
    if session["step"] < len(session["solution"])-1:
        session["step"] += 1
    return show_step()

def step_back():
    if session["step"] > 0:
        session["step"] -= 1
    return show_step()

# Full solution
def show_full_solution():
    if not session["solution"]:
        return "⚠️ Solve first", None
    md = ""
    for idx, state in enumerate(session["solution"]):
        g_val = idx
        h_val, h_details = manhattan_details(state)
        f_val = g_val + h_val
        if idx==0:
            move_desc = "Starting state"
        else:
            move_desc = f"Tile {session['moves'][idx-1]} moved"
        md += f"### Step {idx}\n{move_desc}\n**g={g_val}, h={h_val}, f={f_val}**\n"
        md += "\n".join(h_details) + "\n"
        grid = "\n".join(["| "+" | ".join(str(state[r*3+c]) for c in range(3))+" |" for r in range(3)])
        md += grid + "\n\n"
    md += f"✅ **Total steps: {len(session['solution'])-1}**"
    return md, None

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## 8-Puzzle Solver with A* (Manhattan Distance)\nEnter a start state as 9 numbers (0 = blank). Example: `7 2 4 5 0 6 8 3 1`")

    start_input = gr.Textbox(label="Start State")
    solve_btn = gr.Button("Solve Puzzle")

    with gr.Row():
        btn_back = gr.Button("⬅️ Back")
        btn_next = gr.Button("➡️ Next Step")
        btn_full = gr.Button("Show Full Solution")

    output_text = gr.Markdown()
    output_plot = gr.Plot()

    solve_btn.click(solve_puzzle, start_input, [output_text, output_plot])
    btn_next.click(step_forward, None, [output_text, output_plot])
    btn_back.click(step_back, None, [output_text, output_plot])
    btn_full.click(show_full_solution, None, [output_text, output_plot])

demo.launch()
