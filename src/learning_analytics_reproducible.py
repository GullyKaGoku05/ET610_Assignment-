"""
Reproducible Learning Analytics analysis
Focus:
1) Question-level timestamp-based observed dwell and gaze spread
2) Story-section navigation verification from the interaction log

Expected files in the same directory:
    dataset.csv
    dataset.json
    robotcomprehension.xlsx   # required for navigation analysis
    screenshots/

The supplied archive used for this report did not contain robotcomprehension.xlsx.
The script therefore raises a clear error rather than fabricating navigation events.

Gaze chronology:
- sorted by gaze_timestamp
- screen_timestamp is never used
- raw gaze samples are not treated as fixations
- observed dwell assigns the interval to the next gaze sample, capped at 0.50 s
- intervals crossing screen boundaries are set to zero
"""

from pathlib import Path
import json
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent
GAZE_CSV = BASE / "dataset.csv"
JSON_PATH = BASE / "dataset.json"
INTERACTIONS_XLSX = BASE / "robotcomprehension.xlsx"
SCREENSHOT_DIR = BASE / "screenshots"
OUTPUT_DIR = BASE / "analysis_output"
OUTPUT_DIR.mkdir(exist_ok=True)

MAX_GAP_SECONDS = 0.50

# ---------- Load ----------
gaze = pd.read_csv(GAZE_CSV)
with open(JSON_PATH, encoding="utf-8") as f:
    js = json.load(f)

required = ["user_id","activity_id","task_id","screen_id",
            "gaze_timestamp","gaze_x","gaze_y","image_file"]
missing = [c for c in required if c not in gaze.columns]
if missing:
    raise ValueError(f"Missing gaze columns: {missing}")

gaze["gaze_timestamp"] = pd.to_datetime(
    gaze["gaze_timestamp"], errors="coerce", utc=True
)
if gaze["gaze_timestamp"].isna().any():
    raise ValueError("Invalid or missing gaze_timestamp values.")

gaze = gaze.sort_values("gaze_timestamp").reset_index(drop=True)

# ---------- JSON metadata ----------
records = []
for screen in js.get("screens", []):
    for item in screen.get("gazeData", []):
        records.append({
            "screen_id": screen.get("screenId"),
            "image_file": screen.get("imageFile"),
            "gaze_timestamp": pd.to_datetime(
                item.get("timestamp"), errors="coerce", utc=True
            ),
            "panelTitle": item.get("panelTitle"),
            "elementId_json": item.get("elementId"),
        })
meta = pd.DataFrame(records)

gaze = gaze.merge(
    meta,
    on=["screen_id","image_file","gaze_timestamp"],
    how="left"
)

# ---------- Timestamp-based observed dwell ----------
gaze["next_time"] = gaze["gaze_timestamp"].shift(-1)
gaze["gap_s"] = (
    gaze["next_time"] - gaze["gaze_timestamp"]
).dt.total_seconds().clip(lower=0, upper=MAX_GAP_SECONDS)
gaze.loc[gaze["next_time"].isna(), "gap_s"] = 0

gaze["next_screen_id"] = gaze["screen_id"].shift(-1)
gaze.loc[gaze["screen_id"] != gaze["next_screen_id"], "gap_s"] = 0

# ---------- Question-level analysis ----------
FORMAT = {
    1: "Multiple selection",
    2: "Free text",
    3: "Multiple choice",
    4: "Free text",
}

gaze["question_no"] = gaze["panelTitle"].str.extract(r"Q([1-4])\s*-")[0]
qg = gaze[gaze["question_no"].notna()].copy()
qg["question_no"] = qg["question_no"].astype(int)

results = (
    qg.groupby("question_no")
    .agg(
        observations=("gaze_timestamp","size"),
        dwell_s=("gap_s","sum"),
        x_sd=("gaze_x","std"),
        y_sd=("gaze_y","std"),
        x_min=("gaze_x","min"),
        x_max=("gaze_x","max"),
        y_min=("gaze_y","min"),
        y_max=("gaze_y","max"),
    )
    .reset_index()
)

results["format"] = results["question_no"].map(FORMAT)
results["spread_sd"] = np.sqrt(
    results["x_sd"]**2 + results["y_sd"]**2
)
results["bbox_area"] = (
    (results["x_max"] - results["x_min"]) *
    (results["y_max"] - results["y_min"])
)
results = results.sort_values("question_no")

results.to_csv(OUTPUT_DIR/"question_attention_results.csv", index=False)

# ---------- Figures ----------
plt.figure(figsize=(6.6,3.0))
plt.bar(
    results["question_no"].astype(str),
    results["dwell_s"]
)
plt.xlabel("Question")
plt.ylabel("Estimated dwell (s)")
plt.title("Timestamp-based observed dwell by question")
plt.tight_layout()
plt.savefig(OUTPUT_DIR/"figure1_dwell.png", dpi=300, bbox_inches="tight")
plt.close()

plt.figure(figsize=(6.6,3.0))
plt.bar(
    results["question_no"].astype(str),
    results["spread_sd"]
)
plt.xlabel("Question")
plt.ylabel("Gaze spread (coordinate SD)")
plt.title("Spatial spread of gaze samples by question")
plt.tight_layout()
plt.savefig(OUTPUT_DIR/"figure2_spread.png", dpi=300, bbox_inches="tight")
plt.close()

# ---------- Navigation verification ----------
if not INTERACTIONS_XLSX.exists():
    raise FileNotFoundError(
        "robotcomprehension.xlsx is required to verify actual story-section "
        "clicks. It was not present in the supplied archive, so no navigation "
        "events are fabricated."
    )

events = pd.read_excel(INTERACTIONS_XLSX)
required_events = ["element","elementId","elementType","duration",
                   "verb","user","timeStamp"]
missing_events = [c for c in required_events if c not in events.columns]
if missing_events:
    raise ValueError(f"Missing interaction columns: {missing_events}")

events["timeStamp"] = pd.to_datetime(
    events["timeStamp"], errors="coerce", utc=True
)
gaze_user = str(gaze["user_id"].dropna().iloc[0])
student_events = events[events["user"].astype(str) == gaze_user].copy()
student_events = student_events.sort_values("timeStamp")

def story_section(element):
    if pd.isna(element):
        return np.nan
    m = re.match(r"\s*([1-7])\s*", str(element))
    return int(m.group(1)) if m else np.nan

student_events["story_section"] = student_events["element"].map(story_section)

clicks = student_events[
    (student_events["verb"].astype(str).str.lower() == "clicked") &
    (student_events["elementType"].astype(str).str.lower() == "instruction") &
    student_events["story_section"].notna()
].copy()

clicks["story_section"] = clicks["story_section"].astype(int)
clicks["previous_section"] = clicks["story_section"].shift(1)
clicks["backward_jump"] = (
    clicks["story_section"] < clicks["previous_section"]
).fillna(False)
clicks["revisit"] = clicks["story_section"].duplicated(keep="first")

clicks.to_csv(OUTPUT_DIR/"story_navigation_clicks.csv", index=False)
clicks[clicks["backward_jump"]].to_csv(
    OUTPUT_DIR/"backward_jumps.csv", index=False
)

print(results.to_string(index=False))
print("\nNavigation clicks:")
print(clicks[
    ["timeStamp","element","story_section","backward_jump","revisit"]
].to_string(index=False))
