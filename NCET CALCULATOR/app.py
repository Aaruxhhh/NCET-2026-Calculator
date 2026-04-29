import os
import re
from flask import Flask, request, jsonify, render_template
import pdfplumber

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files[]' not in request.files or 'answer_key_text' not in request.form:
        return jsonify({'error': 'Missing response sheets or answer key text'}), 400

    # 1. Parse the PASTED Answer Key Text
    answer_key_text = request.form.get('answer_key_text', '')
    active_answer_key = {}
    
    try:
        # Regex looks for a 4-6 digit Question ID, any amount of space/tabs/newlines, 
        # and then the Correct Option(s) or the word 'Dropped'
        matches = re.findall(r'\b(\d{4,6})\b\s+([1-4](?:\s*,\s*[1-4])*|Dropped)', answer_key_text, re.IGNORECASE)
        for q_id, ans in matches:
            # Clean up spaces (e.g., "1, 3" becomes "1,3") and capitalize "Dropped"
            active_answer_key[q_id] = ans.replace(" ", "").title()
            
    except Exception as e:
        return jsonify({'error': f'Failed to parse Answer Key text: {str(e)}'}), 400

    if not active_answer_key:
        return jsonify({'error': 'Could not find valid Question IDs and Answers in the pasted text. Please make sure you copied the table correctly.'}), 400

    # 2. Parse the Response Sheet PDFs
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
                
                blocks = full_text.split("Question ID:")
                for block in blocks[1:]:
                    id_match = re.search(r'^\s*(\d+)', block)
                    if not id_match:
                        continue
                    q_id = id_match.group(1).strip()

                    ans_match = re.search(r'Answer Given By Candidate is:\s*(\d+)', block)
                    if ans_match:
                        ans = ans_match.group(1).strip()
                    elif "NOT ANSWERED" in block or "--" in block or "Not Attempted" in block:
                        ans = "Not Attempted"
                    else:
                        ans = "Not Attempted"

                    all_parsed_data[q_id] = ans
            except Exception as e:
                print(f"Error parsing file {file.filename}: {e}")

    # 3. Grade the responses against the dynamic key
    results = []
    score, correct, incorrect, unattempted = 0, 0, 0, 0

    for q_id, cand_ans in all_parsed_data.items():
        official_ans = active_answer_key.get(q_id, "Unknown")
        if official_ans == "Unknown":
            continue

        if official_ans.lower() == "dropped":
            score += 4
            status = "Dropped (+4)"
        elif cand_ans == "Not Attempted":
            unattempted += 1
            status = "Unattempted (0)"
        # Using .split(',') handles multiple correct options like "1,3"
        elif cand_ans in official_ans.split(','):
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
        "questions": results,
        "keys_found": len(active_answer_key) # Helpful for debugging
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
