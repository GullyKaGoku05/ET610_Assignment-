# Learning Analytics of Gaze Attention and Story Navigation

> **ET610 — Learning Analytics Assignment**  
> **IIT Bombay | Autumn 2026**

An evidence-based learning analytics study examining **learner gaze attention, question-level dwell behaviour, gaze dispersion, and story-section navigation** using recorded interaction and eye-gaze data.

---

## 📌 Overview

This project investigates how a learner interacted with an educational reading/comprehension activity by analysing:

- **Gaze attention and observed dwell time** across four questions (Q1–Q4)
- **Gaze dispersion** using the spatial variability of gaze coordinates
- Differences in attention across different **question formats**
- **Story-section navigation** using recorded interaction events
- Revisits and backward navigation where supported by the interaction data

The analysis combines structured gaze data, activity metadata, screenshots, and interaction logs to provide a quantitative description of the learner's behaviour.

> **Important:** This study contains gaze data from a single learner. Therefore, the findings are descriptive and should not be interpreted as population-level conclusions.

---

## 🎯 Objectives

The analysis focuses on the following questions:

1. **How much observed gaze dwell is associated with each question?**
2. **How does gaze spread vary across the questions?**
3. **How does learner attention vary across different question formats?**
4. **What evidence of forward navigation, revisits, or backward movement is present in the recorded story interaction?**

---

## 📊 Dataset

The project uses the following data sources:

| File | Description |
|---|---|
| `dataset.csv` | Timestamped gaze observations |
| `dataset.json` | Screen metadata, question labels, and gaze information |
| `robotcomprehension.xlsx` | Interaction/click log, when available |
| `screenshots/` | Screens captured during the learning activity |

### Gaze Data

The gaze dataset contains:

- **3,346 gaze observations**
- **1 learner**
- **1 learning activity**
- **36 recorded screens**
- Gaze timestamps spanning approximately **457 seconds**

The gaze observations are ordered chronologically using `gaze_timestamp`.

The analysis does **not** use the unavailable `screen_timestamp` field.

---

## 🧠 Methodology

### 1. Timestamp-Based Dwell Estimation

Raw gaze observations are **not treated as fixations**.

Instead, observed dwell is estimated from consecutive gaze timestamps:

1. Sort observations by `gaze_timestamp`.
2. For each gaze observation, calculate the time until the next observation.
3. Use the interval only when the next observation remains on the same screen.
4. Cap individual intervals at **0.50 seconds**.
5. Assign zero dwell when the screen changes.

This provides a **timestamp-based observed dwell estimate**, rather than a fixation-duration measure.

---

### 2. Gaze Spread

Gaze spread is calculated using the spatial variability of the gaze coordinates.

For each question:

\[
\text{Gaze Spread} =
\sqrt{\sigma_x^2+\sigma_y^2}
\]

where:

- \(\sigma_x\) = standard deviation of horizontal gaze position
- \(\sigma_y\) = standard deviation of vertical gaze position

A larger value indicates greater spatial dispersion of recorded gaze positions.

Bounding-box area is also retained as a supplementary measure.

---

### 3. Question Identification

Question membership is obtained from the screen metadata in `dataset.json`.

The four questions are:

| Question | Format |
|---|---|
| Q1 | Multiple selection |
| Q2 | Free text |
| Q3 | Multiple choice |
| Q4 | Free text |

Question format is used for **descriptive comparison only**. The analysis does not assume that one question format is inherently more difficult than another.

---

## 📈 Results

### Question-Level Gaze Behaviour

| Question | Format | Gaze Observations | Observed Dwell (s) | Gaze Spread |
|---|---|---:|---:|---:|
| Q1 | Multiple selection | 304 | **36.127** | 184.380 |
| Q2 | Free text | 115 | **15.924** | 167.302 |
| Q3 | Multiple choice | 149 | **19.260** | **209.819** |
| Q4 | Free text | 223 | **26.861** | **149.346** |

### Key observations

- **Q1** had the highest observed dwell at **36.127 seconds**.
- **Q2** had the lowest observed dwell at **15.924 seconds**.
- **Q3** showed the greatest gaze spread at **209.819**.
- **Q4** showed the smallest gaze spread at **149.346**.
- The two free-text questions, Q2 and Q4, show substantially different dwell behaviour, indicating that **question format alone does not explain observed attention**.

These results describe this learner's recorded behaviour and should not be interpreted as evidence that a particular question type is universally harder.

---

## 📊 Visualizations

### Figure 1 — Observed Dwell by Question

The figure compares timestamp-based observed dwell across Q1–Q4.

### Figure 2 — Gaze Spread by Question

The figure compares the spatial dispersion of recorded gaze positions across Q1–Q4.

The generated figures are available in:

```text
figures/
├── figure1_dwell.png
└── figure2_spread.png
```

---

## 🧭 Story Navigation

Story navigation is analysed separately from gaze behaviour using **recorded interaction/click events**.

The navigation analysis is intended to identify:

- Story-section transitions
- Forward movement
- Backward movement
- Revisited sections
- Repeated interaction with previously visited content

Gaze or screenshot ordering is **not substituted for actual interaction clicks**.

### Data availability note

The supplied project archive used for this analysis does not contain the original interaction workbook (`robotcomprehension.xlsx`). Consequently, navigation statistics cannot be independently recomputed from the supplied archive.

The reproducible script therefore **does not fabricate navigation events**. If the original interaction workbook is supplied, the script can process the recorded clicks and calculate the navigation measures.

The absence of interaction records in the supplied archive should **not** be interpreted as evidence that the learner did not reread, revisit, or navigate backward.

---

## ⚠️ Limitations

Several limitations should be considered when interpreting the results:

### Single-learner dataset

Only one gaze-tracked learner is available. Therefore, the findings are descriptive and cannot establish general behavioural patterns.

### Gaze samples are not fixations

The recorded gaze samples are not automatically equivalent to eye fixations. The analysis therefore reports **timestamp-based observed dwell**, not fixation duration.

### Missing screen timestamps

The `screen_timestamp` field is unavailable/missing. Screen association is therefore derived from the available gaze and screen metadata rather than relying on this field.

### Coordinate-system uncertainty

The original coordinate-system resolution is not documented in the supplied metadata. Most screenshots are **1366 × 632**, but the analysis does not impose an unsupported 1920 × 1080 coordinate assumption.

Some gaze coordinates fall outside the screenshot bounds; these observations are retained rather than silently removed.

### Interaction log availability

The original interaction workbook required to independently verify click-based story navigation was not present in the supplied archive.

---

## 🔬 Reproducibility

The complete analysis can be reproduced using the Python script:

```text
src/
└── learning_analytics_reproducible.py
```

The script:

1. Loads the gaze CSV.
2. Loads the JSON screen metadata.
3. Sorts gaze observations using `gaze_timestamp`.
4. Maps observations to Q1–Q4.
5. Calculates timestamp-based observed dwell.
6. Calculates gaze dispersion.
7. Generates the analysis figures.
8. Processes the interaction workbook when it is available.
9. Explicitly reports an error rather than inventing navigation data when the interaction workbook is missing.

### Requirements

Python 3.9+ is recommended.

Install the required packages with:

```bash
pip install pandas numpy matplotlib openpyxl
```

### Run the analysis

From the project root:

```bash
python src/learning_analytics_reproducible.py
```

The script expects the dataset files to be available in the appropriate project directories.

---

## 📁 Project Structure

```text
ET610_Assignment-/
│
├── README.md
│
├── report/
│   └── Learning_Analytics_Final_Report.pdf
│
├── data/
│   ├── dataset.csv
│   ├── dataset.json
│   └── robotcomprehension.xlsx
│
├── src/
│   └── learning_analytics_reproducible.py
│
├── figures/
│   ├── figure1_dwell.png
│   └── figure2_spread.png
│
└── screenshots/
    ├── screen_000001.png
    ├── screen_000002.png
    └── ...
```

> `robotcomprehension.xlsx` should only be included when the original interaction data is available.

---

## 📄 Report

The final academic report provides the complete methodology, quantitative results, interpretation, limitations, and reproducibility information.

**Author:** Nikhil Kshirsagar  
**Institution:** IIT Bombay  
**Email:** 23b4221@iitb.ac.in

---

## 🔗 Repository

GitHub repository:

**GullyKaGoku05/ET610_Assignment-**

---

## 📝 Academic Integrity & Data Handling

This project reports only measurements that can be supported by the supplied data.

In particular:

- No missing interaction events are fabricated.
- Raw gaze samples are not labelled as fixations.
- Gaze observations are chronologically ordered using `gaze_timestamp`.
- Missing `screen_timestamp` values are not substituted with invented timestamps.
- Unsupported coordinate-system assumptions are avoided.
- Descriptive findings are not presented as causal or population-level conclusions.

---

## 📚 References

The analysis is based primarily on the supplied course dataset, metadata, screenshots, and interaction records.

Additional methodological references should be added here if external literature or course readings are cited in the final submission.
