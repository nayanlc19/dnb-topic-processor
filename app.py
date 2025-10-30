"""
Flask App for Topic Standardization with Real-Time Progress
Displays tqdm-style progress bar in browser
"""

from flask import Flask, render_template, Response, jsonify
from flask_cors import CORS
import json
import time
import threading
from datetime import datetime
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client
from groq import Groq

app = Flask(__name__)
CORS(app)

# Configuration - Load from environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

if not all([SUPABASE_URL, SUPABASE_SERVICE_KEY, GROQ_API_KEY]):
    raise ValueError("Missing required environment variables. Please set SUPABASE_URL, SUPABASE_SERVICE_KEY, and GROQ_API_KEY")

# Initialize clients
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

# Load taxonomy
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TAXONOMY_PATH = os.path.join(SCRIPT_DIR, 'MASTER_TAXONOMY.json')
with open(TAXONOMY_PATH, 'r', encoding='utf-8') as f:
    MASTER_TAXONOMY = json.load(f)

# Global state
processing_state = {
    'is_running': False,
    'current_subject': None,
    'current_question': 0,
    'total_questions': 0,
    'processed_total': 0,
    'subjects_completed': 0,
    'current_topic': '',
    'confidence': 0,
    'start_time': None,
    'logs': []
}

def log_message(message):
    """Add message to logs"""
    processing_state['logs'].append({
        'time': datetime.now().strftime('%H:%M:%S'),
        'message': message
    })
    if len(processing_state['logs']) > 50:
        processing_state['logs'] = processing_state['logs'][-50:]

def get_all_topics_for_subject(subject_key):
    """Get topics from master taxonomy"""
    topics = {
        "cross_cutting": {},
        "subject_specific": []
    }

    for category in MASTER_TAXONOMY["cross_cutting_topics"]["categories"]:
        topics["cross_cutting"][category["main_topic"]] = category["subtopics"]

    if subject_key in MASTER_TAXONOMY["subject_specific_topics"]["subjects"]:
        subject_data = MASTER_TAXONOMY["subject_specific_topics"]["subjects"][subject_key]
        topics["subject_specific"] = subject_data["topics"]
        topics["reference_book"] = subject_data["reference_book"]

    return topics

def map_topic_with_ai(question_text, original_topic, subject):
    """Map topic using AI"""
    topics = get_all_topics_for_subject(subject)

    if not topics["subject_specific"]:
        return {
            "topic_v2": original_topic,
            "subtopic_v2": None,
            "reference_book_v2": "Not Standardized",
            "confidence": 0.0
        }

    cross_cutting_list = []
    for main_topic, subtopics in topics["cross_cutting"].items():
        cross_cutting_list.append(f"**{main_topic}**")
        for st in subtopics:
            cross_cutting_list.append(f"  - {st}")

    subject_list = [f"  - {topic}" for topic in topics["subject_specific"]]

    prompt = f"""You are a medical education expert. Map this DNB question to the MOST APPROPRIATE topic from the predefined taxonomy below.

Question Text: {question_text[:600]}
Original Topic Label: {original_topic}

AVAILABLE TOPICS (choose EXACTLY one):

A) CROSS-CUTTING TOPICS (preferred if question is about these areas):
{chr(10).join(cross_cutting_list)}

B) SUBJECT-SPECIFIC TOPICS ({subject.upper()}):
{chr(10).join(subject_list)}

RULES:
1. If question is about research, statistics, ethics, quality - ALWAYS choose from Cross-Cutting Topics
2. Otherwise, choose from Subject-Specific Topics
3. Pick the MOST SPECIFIC topic that matches
4. Return ONLY valid JSON - no explanation

OUTPUT FORMAT (exact JSON only):
{{
  "is_cross_cutting": true/false,
  "main_topic": "exact topic name from list above",
  "subtopic": "more specific aspect if applicable or null",
  "confidence": 0.95,
  "reasoning": "one sentence why this topic"
}}"""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=250,
        )

        result_text = response.choices[0].message.content.strip()

        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()

        result = json.loads(result_text)

        main_topic = result.get("main_topic", "")
        is_valid = False

        if result.get("is_cross_cutting"):
            for ct_category in MASTER_TAXONOMY["cross_cutting_topics"]["categories"]:
                if main_topic in [ct_category["main_topic"]] + ct_category["subtopics"]:
                    is_valid = True
                    break
        else:
            if main_topic in topics["subject_specific"]:
                is_valid = True

        if not is_valid:
            main_topic = original_topic
            result["confidence"] = 0.5

        return {
            "topic_v2": main_topic,
            "subtopic_v2": result.get("subtopic"),
            "reference_book_v2": topics.get("reference_book", "Master Taxonomy"),
            "confidence": result.get("confidence", 0.7)
        }

    except Exception as e:
        return {
            "topic_v2": original_topic,
            "subtopic_v2": None,
            "reference_book_v2": topics.get("reference_book", "Unknown"),
            "confidence": 0.5
        }

def process_subjects():
    """Main processing loop"""
    subjects = [
        ("anaesth_questions", "anaesth", "Anesthesia"),
        ("anat_questions", "anat", "Anatomy"),
        ("biochem_questions", "biochem", "Biochemistry"),
        ("cardianae_questions", "cardianae", "Cardiac Anesthesia"),
        ("cardio_questions", "cardio", "Cardiology"),
        ("cvts_questions", "cvts", "CVTS"),
        ("derma_questions", "derma", "Dermatology"),
        ("em_questions", "em", "Emergency Medicine"),
        ("endo_questions", "endo", "Endocrinology"),
        ("ent_questions", "ent", "ENT"),
        ("fmt_questions", "fmt", "Forensic Medicine"),
        ("gastro_questions", "gastro", "Gastroenterology"),
        ("genetics_questions", "genetics", "Genetics"),
        ("hemat_questions", "hemat", "Hematology"),
        ("hosp_questions", "hosp", "Hospital Admin"),
        ("med_questions", "med", "Medicine"),
        ("micro_questions", "micro", "Microbiology"),
        ("nephro_questions", "nephro", "Nephrology"),
        ("neuro_questions", "neuro", "Neurology"),
        ("neuroane_questions", "neuroane", "Neuro Anesthesia"),
        ("nm_questions", "nm", "Nuclear Medicine"),
        ("ns_questions", "ns", "Neurosurgery"),
        ("obgy_questions", "obgy", "OB/GYN"),
        ("onco_questions", "onco", "Oncology"),
        ("oph_questions", "oph", "Ophthalmology"),
        ("ortho_questions", "ortho", "Orthopedics"),
        ("patho_questions", "patho", "Pathology"),
        ("ped_questions", "ped", "Pediatrics"),
        ("pharma_questions", "pharma", "Pharmacology"),
        ("physio_questions", "physio", "Physiology"),
        ("pmr_questions", "pmr", "PMR"),
        ("ps_questions", "ps", "Plastic Surgery"),
        ("psm_questions", "psm", "PSM"),
        ("psych_questions", "psych", "Psychiatry"),
        ("radio_questions", "radio", "Radiology"),
        ("rheumat_questions", "rheumat", "Rheumatology"),
        ("surg_questions", "surg", "Surgery"),
        ("tbc_questions", "tbc", "TB & Chest"),
        ("uro_questions", "uro", "Urology"),
        ("vs_questions", "vs", "Vascular Surgery"),
    ]

    processing_state['start_time'] = datetime.now().isoformat()
    log_message("🚀 Started topic standardization process")

    for table_name, subject_key, display_name in subjects:
        if not processing_state['is_running']:
            break

        processing_state['current_subject'] = display_name
        log_message(f"📚 Processing {display_name}...")

        # Fetch unprocessed questions
        response = supabase.table(table_name).select("id, question_text, topic").is_("topic_v2", "null").limit(10000).execute()
        questions = response.data

        processing_state['total_questions'] = len(questions)
        processing_state['current_question'] = 0

        if not questions:
            log_message(f"✓ {display_name}: No questions to process")
            processing_state['subjects_completed'] += 1
            continue

        for i, question in enumerate(questions, 1):
            if not processing_state['is_running']:
                break

            processing_state['current_question'] = i

            # Map topic
            mapping = map_topic_with_ai(
                question.get("question_text", ""),
                question.get("topic", ""),
                subject_key
            )

            processing_state['current_topic'] = mapping['topic_v2']
            processing_state['confidence'] = mapping['confidence']

            # Update database
            try:
                supabase.table(table_name).update({
                    "topic_v2": mapping["topic_v2"],
                    "subtopic_v2": mapping["subtopic_v2"],
                    "reference_book_v2": mapping["reference_book_v2"],
                    "ai_confidence_score": mapping["confidence"]
                }).eq("id", question["id"]).execute()

                processing_state['processed_total'] += 1
            except Exception as e:
                log_message(f"❌ Error updating Q#{question['id']}: {e}")

            # Rate limiting
            if i % 25 == 0:
                time.sleep(60)
            else:
                time.sleep(2)

        processing_state['subjects_completed'] += 1
        log_message(f"✅ {display_name} complete: {len(questions)} questions processed")

    processing_state['is_running'] = False
    log_message("🎉 All subjects processed!")

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/start', methods=['POST'])
def start_processing():
    """Start the processing"""
    if not processing_state['is_running']:
        processing_state['is_running'] = True
        processing_state['processed_total'] = 0
        processing_state['subjects_completed'] = 0
        processing_state['logs'] = []

        thread = threading.Thread(target=process_subjects)
        thread.daemon = True
        thread.start()

        return jsonify({'status': 'started'})
    return jsonify({'status': 'already_running'})

@app.route('/stop', methods=['POST'])
def stop_processing():
    """Stop the processing"""
    processing_state['is_running'] = False
    log_message("⏸️ Processing stopped by user")
    return jsonify({'status': 'stopped'})

@app.route('/status')
def get_status():
    """Get current status"""
    return jsonify(processing_state)

@app.route('/stream')
def stream():
    """Server-Sent Events for real-time updates"""
    def generate():
        while True:
            data = json.dumps(processing_state)
            yield f"data: {data}\n\n"
            time.sleep(1)

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
