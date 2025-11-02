import glob, json, os
from rich import print
from rich.table import Table

def load_latest_trace():
    files = sorted(glob.glob("runs/trace-*.jsonl"))
    if not files:
        raise SystemExit("No trace files found in runs/")
    return files[-1]

def summarize(path=None):
    path = path or load_latest_trace()
    events = [json.loads(x) for x in open(path, "r", encoding="utf-8")]
    instr = next((e.get("instruction") for e in events if e.get("event")=="reset"), "<unknown>")
    agent = next((e.get("agent") for e in events if e.get("event")=="reset"), "<unknown>")
    delivered = next((e.get("delivered") for e in events if e.get("event")=="done"), {})
    steps = [e for e in events if e.get("event")=="act"]

    print(f"[bold]Trace:[/bold] {os.path.basename(path)}")
    print(f"[bold]Instruction:[/bold] {instr}")
    print(f"[bold]Agent:[/bold] {agent}")
    print(f"[bold]Delivered:[/bold] {delivered}")

    t = Table(title="Actions")
    t.add_column("t", justify="right"); t.add_column("type"); t.add_column("payload")
    for e in steps[:200]:
        a = e.get("action", {})
        t.add_row(str(e.get("t","")), a.get("type","?"), str({k:v for k,v in a.items() if k!="type"}))
    print(t)

def main(path: str = None):
    summarize(path)

if __name__ == "__main__":
    main()
