import os
import re
from flask import Flask, request, jsonify, render_template
import pdfplumber

app = Flask(__name__)

# Master Answer Key based on the official NCET 2026 responses
ANSWER_KEY = {
  "12699": "2", "12700": "1", "12701": "1", "12702": "3", "12703": "4", "12704": "2",
  "12705": "1", "12706": "3", "12707": "4", "12708": "3", "12709": "2", "12710": "2",
  "12711": "1", "12712": "4", "12713": "2", "12714": "3", "12715": "1", "12716": "3",
  "12717": "4", "12718": "2", "12719": "4", "12720": "4", "12721": "2", "12915": "3",
  "12916": "3", "12917": "3", "12919": "1", "12921": "1", "12922": "4", "12923": "2",
  "12925": "2", "12936": "4", "12937": "2", "12938": "4", "12939": "4", "12940": "2",
  "12941": "1", "12942": "2", "12943": "1", "12944": "3", "12945": "2", "12946": "3",
  "12947": "2", "12948": "3", "12949": "1", "12950": "4", "12313": "3", "12316": "2",
  "12320": "1", "12328": "3", "12348": "2", "12351": "1", "12356": "4", "12359": "2",
  "12363": "1", "12368": "4", "12370": "4", "12375": "2", "12378": "3", "12385": "4",
  "12393": "3", "12395": "2", "12403": "3", "12404": "2", "12405": "3", "12406": "2",
  "12407": "1", "12408": "3", "12409": "4", "12410": "2", "12411": "3", "12413": "2",
  "12415": "1", "13785": "3", "1736": "3", "1776": "1", "1778": "4", "1780": "1",
  "1781": "1", "1782": "2", "1784": "4", "1787": "3", "1789": "2", "1790": "3",
  "1968": "3", "1969": "2", "1970": "4", "1971": "4", "1972": "2", "1973": "2",
  "1974": "1", "1975": "2", "1976": "1", "1977": "1", "1978": "1", "1979": "2",
  "1980": "4", "1981": "3", "1982": "1", "1983": "4", "1984": "3", "1985": "1",
  "13426": "1", "12154": "3", "12156": "4", "12158": "3", "12160": "2", "12162": "1",
  "12164": "1", "12199": "3", "12200": "4", "12201": "1", "12202": "1", "12203": "4",
  "12204": "1", "12205": "1", "12206": "3", "12207": "3", "12208": "3", "12209": "2",
  "12210": "1", "12211": "2", "12212": "1", "12213": "4", "12214": "3", "12215": "4",
  "12216": "4", "12217": "4", "12218": "3", "12219": "2", "12435": "4", "12436": "1",
  "12440": "4", "12441": "1", "12442": "2", "12443": "1", "12444": "3", "12446": "1",
  "12447": "2", "12448": "Dropped", "12451": "3", "12452": "2", "12454": "4",
  "12455": "4", "12457": "2", "12459": "1", "12461": "3", "12463": "3", "12465": "3",
  "12466": "2", "12469": "1", "12470": "2", "12472": "3", "1386": "2", "1387": "3",
  "1388": "3", "1391": "3", "1392": "1", "1394": "2", "1395": "3", "1396": "3",
  "1402": "2", "1403": "2", "1405": "2", "1406": "3", "1407": "2", "1408": "2",
  "1409": "4", "1410": "3", "1411": "2", "1412": "4", "1413": "4", "1414": "4",
  "1415": "3", "1416": "3", "1417": "2", "1418": "1", "1419": "4", "1420": "3",
  "1421": "4", "1422": "1"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400

    files = request.files.getlist('files[]')
    all_parsed_data = {}

    for file in files:
        if file and file.filename.lower().endswith('.pdf'):
            try:
                with pdfplumber.open(file) as pdf:
                    full_text = ""
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            full_text += text + "\n"
                
                # BUG FIX: Split by Question ID to isolate each block. 
                # This ensures we don't misalign arrays if a question is skipped.
                blocks = full_text.split("Question ID:")
                for block in blocks[1:]:
                    # Extract ID
                    id_match = re.search(r'^\s*(\d+)', block)
                    if not id_match:
                        continue
                    q_id = id_match.group(1).strip()

                    # Extract Answer
                    ans_match = re.search(r'Answer Given By Candidate is:\s*(\d+)', block)
                    if ans_match:
                        ans = ans_match.group(1).strip()
                    elif "NOT ANSWERED" in block or "--" in block or "Not Attempted" in block:
                        ans = "Not Attempted"
                    else:
                        ans = "Not Attempted" # Fallback safeguard

                    all_parsed_data[q_id] = ans
            except Exception as e:
                print(f"Error parsing file {file.filename}: {e}")

    # Process and Score
    results = []
    score, correct, incorrect, unattempted = 0, 0, 0, 0

    for q_id, cand_ans in all_parsed_data.items():
        official_ans = ANSWER_KEY.get(q_id, "Unknown")
        if official_ans == "Unknown":
            continue # Skip questions we don't have the key for

        if official_ans == "Dropped":
            score += 4
            status = "Dropped (+4)"
        elif cand_ans == "Not Attempted":
            unattempted += 1
            status = "Unattempted (0)"
        elif cand_ans == official_ans:
            score += 4
            correct += 1
            status = "Correct (+4)"
        else:
            score -= 1
            incorrect += 1
            status = "Incorrect (-1)"

        results.append({
            "question_id": q_id,
            "official_answer": official_ans,
            "candidate_answer": cand_ans,
            "status": status
        })

    return jsonify({
        "total_score": score,
        "correct": correct,
        "incorrect": incorrect,
        "unattempted": unattempted,
        "questions": results
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)