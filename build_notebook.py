from pathlib import Path
import base64
import html
import json
import platform
import nbformat as nbf
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from notebook_extra import add_extra

ROOT = Path(__file__).resolve().parent
cells = []
def md(text):
    cells.append(nbf.v4.new_markdown_cell(text))
def code(text):
    cells.append(nbf.v4.new_code_cell(text.strip()))

md('''# DISCOVERING AI AGENT — Notebook thực hành
**Mã bài:** agent01_CT_04_hainn · **Ngày:** 23/10/2026

Triển khai tự viết dựa trên mục **Goal-based agents**, **Reasoning with available tools**
và **Activity logs** trong [IBM, What are AI agents?](https://www.ibm.com/think/topics/ai-agents).
Bài 1 là agent ký hiệu dùng BFS, **không phải bản tái lập ReAct**. Bài 2 dùng
retrieval và chính sách Python; bài 3 huấn luyện Q-learning thật. Cả ba không gọi LLM.
Đồ thị, biến cố và ca kiểm tra là dữ liệu mô phỏng phục vụ học tập.
Chạy các cell từ trên xuống. Bài 1–2 dùng thư viện chuẩn Python; bài 3 thêm
Matplotlib để xuất biểu đồ. Notebook mở rộng gồm ba bài thực hành.''')
code('''from collections import deque
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
print("Goal: A -> F; all edges have unit cost.")''')
md('''## 1. Bộ lập kế hoạch
BFS trả về đường ngắn nhất trên **mô hình hiện biết**. `blocked` là bộ nhớ về các cạnh
không đi được. Nếu không có đường, trả về `None`; tập `seen` ngăn duyệt lặp.''')
code('''def plan_route(graph, start, goal, blocked):
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
print("Known closure:", plan_route(GRAPH, "B", "F", {edge("B", "D")}))''')
md('''## 2. Công cụ tương tác môi trường
Sau lần di chuyển đầu tiên, môi trường đóng cạnh B–D. Agent chỉ phát hiện khi thử
đi qua cạnh đó; kế hoạch ban đầu không được biết trước biến cố. `move` là công cụ
duy nhất làm thay đổi vị trí và trả về quan sát có cấu trúc.''')
code('''class World:
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
print("Move B -> D:", w.move("D"))''')
md('''## 3. Vòng điều khiển agent
Định nghĩa bộ nhớ, mục tiêu và giới hạn số lần gọi công cụ. Một kế hoạch chỉ bị bỏ
khi phản hồi thực tế cho thấy nó không còn thực thi được.''')
code('''def run_agent(world, goal="F", budget=12):
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

print("Agent ready: planner + tool + memory + stopping rule.")''')
md('''## 4. Chạy thực nghiệm
So sánh môi trường tĩnh và môi trường có biến cố. Một lần gọi công cụ thất bại
vẫn tiêu tốn ngân sách, nhưng không tăng số bước di chuyển thành công.''')
code('''baseline = run_agent(World())
dynamic = run_agent(World(dynamic=True))
for line in dynamic["log"]:
    print(line)
for name, result in [("STATIC", baseline), ("DYNAMIC", dynamic)]:
    print(name, result["status"], "path=", "->".join(result["path"]),
          "moves=", len(result["path"]) - 1,
          "calls=", result["calls"], "plans=", result["plans"])
assert dynamic["status"] == "success"
assert dynamic["path"] == ["A", "B", "C", "E", "F"]
assert edge("B", "D") in dynamic["blocked"]''')
md('''## 5. Kiểm tra các tình huống có ý nghĩa
Các assert kiểm tra thành công, tái lập kế hoạch, hết ngân sách, không thể đến đích
và trạng thái đã ở đích. Đây là 5 ca xác định, không phải ước lượng xác suất thành công.''')
code('''cases = {
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
print("5/5 cases passed; dynamic run replanned exactly once.")''')
md('''## Nhận xét
Tĩnh: A–B–D–F (3 bước, 3 lần gọi). Động: A–B–C–E–F (4 bước, 5 lần gọi,
2 lần lập kế hoạch). Phản hồi B–D bị chặn làm thay đổi bộ nhớ và kế hoạch.
Agent thích nghi bằng cập nhật trạng thái, **không cập nhật trọng số hoặc học chính sách**.
Giới hạn: đồ thị nhỏ, chi phí bằng nhau, lỗi xác định, cạnh chặn không mở lại.
Muốn tối ưu chi phí khác nhau cần Dijkstra/A*; muốn dùng ngôn ngữ tự nhiên có thể thêm LLM
nhưng phải kiểm tra tham số công cụ và giữ tiêu chí dừng độc lập.''')

add_extra(md, code)
nb = nbf.v4.new_notebook(cells=cells, metadata={
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": platform.python_version()},
})
# Execute real notebook cell sources in one IPython namespace. No fabricated output.
shell = InteractiveShell.instance()
counter = 0
for cell in nb.cells:
    if cell.cell_type != "code":
        continue
    counter += 1
    cell.execution_count = counter
    with capture_output() as captured:
        result = shell.run_cell(cell.source, store_history=False)
    if result.error_before_exec or result.error_in_exec:
        raise RuntimeError(str(result.error_before_exec or result.error_in_exec))
    cell.outputs = []
    if captured.stdout:
        cell.outputs.append(nbf.v4.new_output("stream", name="stdout", text=captured.stdout))
    if captured.stderr:
        cell.outputs.append(nbf.v4.new_output("stream", name="stderr", text=captured.stderr))
    print(f"Executed cell {counter}: {len(captured.stdout)} output chars")
nbf.validate(nb)
nbf.write(nb, ROOT / "agent01_CT_04_hainn.ipynb")
(ROOT / "agent01_CT_04_hainn_code.py").write_text(
    '# Full executable code exported from the notebook.\n'
    + '\n\n'.join(f'# Cell {c.execution_count}\n{c.source}'
                   for c in nb.cells if c.cell_type == 'code') + '\n')

css = '''body{margin:0;background:#eef2f6;color:#17212f;font:18px Arial,sans-serif}
main{width:1100px;margin:20px auto;background:white;border:1px solid #d5dce4;padding:26px;box-sizing:border-box}
h1{font-size:24px;margin:0 0 18px} .subtitle{font:15px Arial;color:#526277;margin-bottom:20px}
.row{display:flex;margin:12px 0}.prompt{width:84px;flex-shrink:0;color:#245b9e;font:16px monospace;padding-top:12px}
.input{border:1px solid #d5dce4;background:#f7f9fc;padding:10px 14px;flex:1;overflow:hidden}
pre{margin:0;font:17px/1.45 "Courier New",monospace;white-space:pre-wrap;overflow-wrap:anywhere}
.output{flex:1;padding:8px 14px;border-left:3px solid #d5e6d8}.out{color:#63736a}
''' + HtmlFormatter().get_style_defs('.highlight')
sections = []
for cell in nb.cells:
    if cell.cell_type != "code":
        continue
    n = cell.execution_count
    inp = highlight(cell.source, PythonLexer(), HtmlFormatter())
    out = html.escape("".join(o.get("text", "") for o in cell.outputs))
    fragment = f'<div class="row"><div class="prompt">In [{n}]:</div><div class="input">{inp}</div></div><div class="row"><div class="prompt out">Output</div><div class="output"><pre>{out}</pre></div></div>'
    body = f'<h1>DISCOVERING AI AGENT · Cell {n}/{counter}</h1><div class="subtitle">agent01_CT_04_hainn.ipynb · Python {platform.python_version()} · Executed output</div>' + fragment
    page = f'<!DOCTYPE html><html lang="vi"><meta charset="utf-8"><style>{css}</style><main>{body}</main></html>'
    (ROOT / "screenshots" / f"cell_{n}.html").write_text(page)
    sections.append(fragment)
full = f'<!DOCTYPE html><html lang="vi"><meta charset="utf-8"><title>Executed notebook</title><style>{css}</style><main><h1>agent01_CT_04_hainn.ipynb — executed code and output</h1>{"".join(sections)}</main></html>'
(ROOT / "agent01_CT_04_hainn_notebook.html").write_text(full)
(ROOT / "build" / "results.json").write_text(json.dumps({k: {"status":r["status"], "path":r["path"], "calls":r["calls"], "plans":r["plans"]} for k,r in [("static",shell.user_ns["baseline"]),("dynamic",shell.user_ns["dynamic"])]}, indent=2))
