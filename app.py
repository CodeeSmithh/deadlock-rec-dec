from flask import Flask, render_template, request
import json

app = Flask(__name__)

def detect_and_recover(data):
    n = data['numProcesses']
    m = data['numResources']
    alloc = data['alloc']
    req = data['req']
    avail = data['avail'][:]

    finish = [False] * n
    work = avail[:]
    steps = []

    # Step 1: Simulate normal completions
    steps.append("🔍 Checking for safe state by simulating process completions...")
    changed = True
    while changed:
        changed = False
        for i in range(n):
            if not finish[i] and all(req[i][j] <= work[j] for j in range(m)):
                for j in range(m):
                    work[j] += alloc[i][j]
                finish[i] = True
                changed = True
                steps.append(f"✅ Process P{i} completed successfully and released its resources: {alloc[i]}")

    # Step 2: Deadlock detection
    deadlocked = [i for i in range(n) if not finish[i]]
    terminated = []

    if deadlocked:
        steps.append(f"⚠️ Deadlock detected. Processes involved: {', '.join(f'P{p}' for p in deadlocked)}")
    else:
        steps.append("✅ System is in a safe state. No deadlock detected.")

    # Step 3: Recovery by terminating the most resource-heavy processes
    while deadlocked:
        proc = max(deadlocked, key=lambda i: sum(alloc[i]))
        terminated.append(proc)
        steps.append(f"🛑 Terminating Process P{proc} to reclaim resources: {alloc[proc]}")
        for j in range(m):
            work[j] += alloc[proc][j]
        finish[proc] = True
        deadlocked = [i for i in range(n) if not finish[i]]

    if terminated:
        steps.append(f"✅ Recovery complete. Terminated processes: {', '.join(f'P{p}' for p in terminated)}")

    return {
        "safe": len(terminated) == 0,
        "terminated": terminated,
        "steps": steps
    }

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/result', methods=['POST'])
def result():
    data = json.loads(request.form["matrixData"])
    result = detect_and_recover(data)
    return render_template("result.html", result=result)

if __name__ == '__main__':
    app.run(debug=True)
