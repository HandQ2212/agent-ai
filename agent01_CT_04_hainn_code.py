# Full executable code exported from the notebook.
# Cell 1
from collections import deque
import platform

GRAPH = {
    "A": ["B", "C"], "B": ["A", "D", "C"],
    "C": ["A", "B", "E"], "D": ["B", "F"],
    "E": ["C", "F"], "F": ["D", "E"],
}

def edge(a, b):
    return frozenset((a, b))

print("Python:", platform.python_version())
print("Nodes:", len(GRAPH))
print("Goal: A -> F; all edges have unit cost.")

# Cell 2
def plan_route(graph, start, goal, blocked):
    queue = deque([[start]])
    seen = {start}
    while queue:
        path = queue.popleft()
        node = path[-1]
        if node == goal:
            return path
        for nxt in graph.get(node, []):
            if nxt not in seen and edge(node, nxt) not in blocked:
                seen.add(nxt)
                queue.append(path + [nxt])
    return None

print("Initial plan:", plan_route(GRAPH, "A", "F", set()))
print("Known closure:", plan_route(GRAPH, "B", "F", {edge("B", "D")}))

# Cell 3
class World:
    def __init__(self, start="A", dynamic=False, closed=()):
        self.pos = start
        self.dynamic = dynamic
        self.closed = set(closed)
        self.moves = 0

    def move(self, nxt):
        if self.dynamic and self.moves >= 1:
            self.closed.add(edge("B", "D"))
        if nxt not in GRAPH.get(self.pos, []):
            return {"ok": False, "error": "invalid", "pos": self.pos}
        if edge(self.pos, nxt) in self.closed:
            return {"ok": False, "error": "blocked", "pos": self.pos}
        self.pos = nxt
        self.moves += 1
        return {"ok": True, "pos": self.pos}

w = World(dynamic=True)
print("Move A -> B:", w.move("B"))
print("Move B -> D:", w.move("D"))

# Cell 4
def run_agent(world, goal="F", budget=12):
    blocked, route, log = set(), [], []
    visited = [world.pos]
    calls, plans, status = 0, 0, "budget_exhausted"
    while world.pos != goal and calls < budget:
        if not route:
            path = plan_route(GRAPH, world.pos, goal, blocked)
            plans += 1
            log.append("PLAN " + str(path))
            if path is None:
                status = "unreachable"
                break
            route = path[1:]
        src, nxt = world.pos, route.pop(0)
        observation = world.move(nxt)
        calls += 1
        log.append(f"ACT {src}->{nxt}: {observation}")
        if observation["ok"]:
            visited.append(world.pos)
        else:
            blocked.add(edge(src, nxt))
            route = []
    if world.pos == goal:
        status = "success"
    return dict(status=status, path=visited, calls=calls,
                plans=plans, blocked=blocked, log=log)

print("Agent ready: planner + tool + memory + stopping rule.")

# Cell 5
baseline = run_agent(World())
dynamic = run_agent(World(dynamic=True))
for line in dynamic["log"]:
    print(line)
for name, result in [("STATIC", baseline), ("DYNAMIC", dynamic)]:
    print(name, result["status"], "path=", "->".join(result["path"]),
          "moves=", len(result["path"]) - 1,
          "calls=", result["calls"], "plans=", result["plans"])
assert dynamic["status"] == "success"
assert dynamic["path"] == ["A", "B", "C", "E", "F"]
assert edge("B", "D") in dynamic["blocked"]

# Cell 6
cases = {
    "static": (baseline, "success", 3),
    "dynamic": (dynamic, "success", 5),
    "budget": (run_agent(World(dynamic=True), budget=1),
               "budget_exhausted", 1),
    "unreachable": (run_agent(World(closed=[edge("A", "B"),
                       edge("A", "C")])), "unreachable", 2),
    "already_goal": (run_agent(World(start="F")), "success", 0),
}
for name, (result, expected, calls) in cases.items():
    assert result["status"] == expected, (name, result)
    assert result["calls"] == calls, (name, result)
    assert result["calls"] <= 12
    print(f"PASS {name:13} status={expected:17} calls={calls}")
assert dynamic["plans"] == 2
print("5/5 cases passed; dynamic run replanned exactly once.")

# Cell 7
import math
import re
import unicodedata
from collections import Counter

DOCS = {
    "D1": {"title": "Library hours", "version": "demo-v1",
           "text": "The library opens from 08:00 to 20:00 on weekdays."},
    "D2": {"title": "Borrowing books", "version": "demo-v1",
           "text": "Students can borrow at most 3 books for 14 days."},
    "D3": {"title": "Lab access", "version": "demo-v1",
           "text": "Lab access requires a student card and a reservation."},
    "D4": {"title": "Course registration", "version": "demo-v1",
           "text": "Course registration closes on day 15 of each term."},
}

def tokens(text):
    clean = unicodedata.normalize("NFKD", text).casefold()
    return re.findall(r"[a-z0-9]+", clean)

print("Synthetic documents:", len(DOCS))
print("Corpus version: demo-v1; not actual university regulations.")

# Cell 8
def cosine(left, right):
    dot = sum(v * right.get(k, 0) for k, v in left.items())
    norm_l = math.sqrt(sum(v*v for v in left.values()))
    norm_r = math.sqrt(sum(v*v for v in right.values()))
    return dot / (norm_l * norm_r) if norm_l and norm_r else 0.0

INDEX = {key: Counter(tokens(d["title"] + " " + d["text"]))
         for key, d in DOCS.items()}

def search_docs(query, top_k=2):
    vector = Counter(tokens(query))
    scored = [(cosine(vector, vec), key) for key, vec in INDEX.items()]
    ranked = sorted(scored, key=lambda x: (-x[0], x[1]))
    return [{"id": key, "score": round(score, 4)}
            for score, key in ranked[:top_k] if score > 0]

print("Search:", search_docs("library hours"))
print("Unknown:", search_docs("quantum banana"))

# Cell 9
def call_tool(name, args):
    if not isinstance(args, dict):
        raise ValueError("arguments must be a dictionary")
    if name == "search":
        if set(args) - {"query", "top_k"} or "query" not in args:
            raise ValueError("invalid search schema")
        query, k = args["query"], args.get("top_k", 2)
        if not isinstance(query, str) or not 1 <= len(query) <= 200:
            raise ValueError("query must contain 1..200 characters")
        if type(k) is not int or not 1 <= k <= 4:
            raise ValueError("top_k must be an integer in 1..4")
        return search_docs(query, k)
    if name == "read":
        if set(args) != {"id"} or not isinstance(args["id"], str):
            raise ValueError("invalid read schema")
        if args["id"] not in DOCS:
            raise ValueError("document not found")
        return dict(DOCS[args["id"]], id=args["id"])
    raise ValueError("tool not allowed")

print(call_tool("read", {"id": "D2"}))
try:
    call_tool("shell", {"command": "anything"})
except ValueError as error:
    print("Rejected:", error)

# Cell 10
def research_agent(question, budget=3, cache=None):
    cache = {} if cache is None else cache
    key = ("demo-v1", question) if isinstance(question, str) else None
    if key in cache:
        return dict(cache[key], calls=0, trace=["CACHE HIT"])
    trace, calls = [], 0
    def invoke(name, args):
        nonlocal calls
        if calls >= budget:
            raise RuntimeError("budget_exhausted")
        calls += 1
        result = call_tool(name, args)
        trace.append(f"{name} {args} -> {result}")
        return result
    try:
        hits = invoke("search", {"query": question, "top_k": 2})
        if not hits:
            status, answer = "no_evidence", "No supporting document."
        else:
            doc = invoke("read", {"id": hits[0]["id"]})
            status = "answered"
            answer = f"{doc['text']} [{doc['id']}; {doc['version']}]"
    except (ValueError, RuntimeError) as error:
        status, answer = str(error), "No verified answer."
    result = dict(status=status, answer=answer, calls=calls, trace=trace)
    if status == "answered":
        cache[key] = dict(result)
    return result

retrieval_result = research_agent("library hours")
print("Answer:", retrieval_result["answer"])
print("Calls:", retrieval_result["calls"])
print("Tools:", [line.split()[0] for line in retrieval_result["trace"]])

# Cell 11
cache = {}
first = research_agent("borrow books", cache=cache)
cached = research_agent("borrow books", cache=cache)
assert "[D2; demo-v1]" in first["answer"]
assert first["calls"] == 2 and cached["calls"] == 0
assert research_agent("quantum banana")["status"] == "no_evidence"
assert research_agent("lab access", budget=1)["status"] == "budget_exhausted"
assert research_agent("")["status"] != "answered"
assert search_docs("course registration")[0]["id"] == "D4"
print("PASS evidence ID, cache, no evidence, budget, empty input, ranking")
for name, args in [("search", {"query": "x", "top_k": True}),
                   ("read", {"id": "D99"})]:
    try:
        call_tool(name, args)
        raise AssertionError("invalid tool input was accepted")
    except ValueError:
        print("PASS rejected", name, args)
print("8/8 retrieval and tool contract checks passed.")

# Cell 12
import random
from collections import defaultdict
from pathlib import Path

SIZE = 5
START, TARGET = (0, 0), (4, 4)
WALLS = {(1, 1), (1, 2), (2, 2), (3, 0), (3, 2)}
DELTAS = [(-1, 0), (0, 1), (1, 0), (0, -1)]

def grid_step(state, action):
    if state == TARGET:
        return state, 0.0, True
    dr, dc = DELTAS[action]
    nxt = (state[0] + dr, state[1] + dc)
    valid = (0 <= nxt[0] < SIZE and 0 <= nxt[1] < SIZE
             and nxt not in WALLS)
    if not valid:
        return state, -3.0, False
    return nxt, (10.0 if nxt == TARGET else -1.0), nxt == TARGET

print("Grid:", SIZE, "x", SIZE, "; walls:", sorted(WALLS))
print("Invalid move:", grid_step(START, 0))
print("Terminal:", grid_step(TARGET, 1))

# Cell 13
def choose_q(Q, state, rng, epsilon):
    if rng.random() < epsilon:
        return rng.randrange(4)
    best = max(Q[state])
    return rng.choice([a for a in range(4) if Q[state][a] == best])

def q_update(Q, state, action, reward, nxt, done, alpha, gamma):
    bootstrap = 0.0 if done else gamma * max(Q[nxt])
    target = reward + bootstrap
    Q[state][action] += alpha * (target - Q[state][action])

probe = defaultdict(lambda: [0.0] * 4)
probe[TARGET] = [100.0] * 4
q_update(probe, (4, 3), 1, 10.0, TARGET, True, 0.2, 0.95)
assert abs(probe[(4, 3)][1] - 2.0) < 1e-12
print("Terminal update:", probe[(4, 3)][1], "(expected 2.0)")

# Cell 14
def train_q(seed, episodes=2500, max_steps=100):
    rng = random.Random(seed)
    Q = defaultdict(lambda: [0.0] * 4)
    history = []
    for episode in range(episodes):
        state, total, reached = START, 0.0, False
        epsilon = max(0.05, 0.9 * (0.995 ** episode))
        for step in range(max_steps):
            action = choose_q(Q, state, rng, epsilon)
            nxt, reward, done = grid_step(state, action)
            q_update(Q, state, action, reward, nxt, done, 0.2, 0.95)
            total += reward
            state = nxt
            if done:
                reached = True
                break
        history.append(dict(reward=total, steps=step+1, success=reached))
    return Q, history

TRAINED = {seed: train_q(seed) for seed in (7, 42, 2026)}
for seed, (_, history) in TRAINED.items():
    tail = history[-100:]
    print(seed, "episodes=", len(history), "last100 success=",
          sum(h["success"] for h in tail), "mean reward=",
          round(sum(h["reward"] for h in tail) / len(tail), 2))

# Cell 15
def evaluate_q(Q=None, episodes=100):
    outcomes = []
    for episode in range(episodes):
        rng = random.Random(10000 + episode)
        state, path, total = START, [START], 0.0
        for step in range(100):
            action = rng.randrange(4) if Q is None else choose_q(Q, state, rng, 0)
            state, reward, done = grid_step(state, action)
            path.append(state)
            total += reward
            if done:
                break
        outcomes.append(dict(success=state == TARGET, steps=len(path)-1,
                             reward=total, path=path))
    return outcomes

EVALS = {"random": evaluate_q()}
EVALS.update({str(seed): evaluate_q(Q) for seed, (Q, _) in TRAINED.items()})
for label, outcomes in EVALS.items():
    print(label, "success=", sum(x["success"] for x in outcomes), "/100",
          "mean steps=", round(sum(x["steps"] for x in outcomes)/100, 2))
print("Learned path:", EVALS["2026"][0]["path"])

# Cell 16
grid_graph = {}
for r in range(SIZE):
    for c in range(SIZE):
        if (r, c) in WALLS:
            continue
        neighbours = [grid_step((r, c), a)[0] for a in range(4)]
        grid_graph[(r, c)] = [n for n in neighbours if n != (r, c)]
oracle = plan_route(grid_graph, START, TARGET, set())
optimal_steps = len(oracle) - 1
assert optimal_steps == 8
for seed, (Q, history) in TRAINED.items():
    assert len(history) == 2500
    assert all(x["success"] and x["steps"] == optimal_steps
               for x in EVALS[str(seed)])
    before = {s: tuple(v) for s, v in Q.items()}
    evaluate_q(Q, episodes=5)
    assert before == {s: tuple(v) for s, v in Q.items()}
    assert all(s not in WALLS for s in EVALS[str(seed)][0]["path"])
print("PASS 3 seeds: success, optimal length, legal path, frozen Q.")
print("Oracle shortest steps:", optimal_steps)
print("Terminal bootstrap check: PASS")

# Cell 17
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

Path("assets").mkdir(exist_ok=True)
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
for seed, (_, hist) in TRAINED.items():
    rewards = [x["reward"] for x in hist]
    smoothed = [sum(rewards[i-99:i+1])/100 for i in range(99, len(hist))]
    axes[0].plot(range(100, len(hist)+1), smoothed, label=str(seed))
axes[0].set(xlabel="Training episode", ylabel="Mean return (100 episodes)",
            title="Q-learning: actual training returns")
axes[0].legend(title="Seed")
board = [[int((r, c) in WALLS) for c in range(SIZE)] for r in range(SIZE)]
axes[1].imshow(board, cmap="Greys", vmin=0, vmax=1)
path = EVALS["2026"][0]["path"]
axes[1].plot([p[1] for p in path], [p[0] for p in path], "o-", color="#24798c")
axes[1].set(title="Frozen policy: seed 2026", xticks=range(5), yticks=range(5))
axes[1].text(0, 0, "S", color="red", fontsize=13)
axes[1].text(4, 4, "G", color="red", fontsize=13)
fig.tight_layout()
fig.savefig("assets/q_learning_results.png", dpi=180)
plt.close(fig)
print("Saved assets/q_learning_results.png")
print("Training: 3 seeds x 2500 episodes; evaluation: 100 episodes/policy.")
