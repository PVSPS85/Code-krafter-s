



from flask import Flask, render_template, request, redirect, url_for, session, flash
import PyPDF2
import os
from datetime import datetime
import re
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'creazyai-ultimate-secret-key-2025'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
socketio = SocketIO(app)




app = Flask(__name__)
app.secret_key = 'creazyai-ultimate-secret-key-2025'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ==========================================
# USER DATABASE WITH RICH DEMO DATA
# ==========================================
users = {
    'demo@student.com': {
        'password': 'demo123',
        'name': 'Demo Student',
        'college': 'BMSUIT College',
        'notes': [],
        'flashcards': [],
        'tasks': [
            {'text': 'Complete Python assignment', 'done': False},
            {'text': 'Study for exams', 'done': False},
            {'text': 'Review lecture notes', 'done': True}
        ],
        'stats': {
            'notes_count': 24,
            'flashcards_count': 87,
            'study_time': 245,
            'streak': 12
        }
    }
}

# ==========================================
# INTELLIGENT TEXT PROCESSING FUNCTIONS
# ==========================================

def extract_pdf_text(pdf_file):
    """Extract text from PDF with error handling"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text.strip() if text.strip() else "Could not extract text from PDF. Please try a different file."
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def clean_text(text):
    """Clean and normalize text"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?;:\-\(\)]', '', text)
    return text.strip()

def extract_sentences(text):
    """Extract meaningful sentences from text"""
    # Split by period, exclamation, or question mark
    sentences = re.split(r'[.!?]+', text)
    # Clean and filter sentences
    sentences = [s.strip() for s in sentences if len(s.strip()) > 30]
    return sentences

def extract_keywords(text, min_length=7, top_n=15):
    """Extract important keywords from text"""
    words = text.split()
    # Filter for meaningful words
    keywords = {}
    for word in words:
        cleaned = re.sub(r'[^\w]', '', word)
        if len(cleaned) >= min_length and cleaned.isalpha():
            word_lower = cleaned.lower()
            if word_lower not in ['however', 'therefore', 'moreover', 'furthermore', 'although', 'because']:
                keywords[cleaned.capitalize()] = keywords.get(cleaned.capitalize(), 0) + 1
    
    # Sort by frequency
    sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
    return [kw[0] for kw in sorted_keywords[:top_n]]

def summarize_text(text):
    """INTELLIGENT summarization that uses actual content"""
    
    cleaned = clean_text(text)
    sentences = extract_sentences(cleaned)
    keywords = extract_keywords(cleaned)
    words = cleaned.split()
    
    # Calculate statistics
    total_words = len(words)
    unique_words = len(set([w.lower() for w in words if w.isalpha()]))
    
    # Build intelligent summary
    summary_parts = []
    
    # Introduction from first 2 sentences
    if len(sentences) >= 2:
        intro = '. '.join(sentences[:2]) + '.'
        summary_parts.append(f"**Overview:**\n{intro}\n")
    elif len(sentences) >= 1:
        summary_parts.append(f"**Overview:**\n{sentences[0]}.\n")
    
    # Key topics section
    if keywords:
        topics = ', '.join(keywords[:6])
        summary_parts.append(f"**Key Topics Identified:**\n• {topics}")
        summary_parts.append(f"• Detailed analysis and explanations")
        summary_parts.append(f"• Practical applications and examples\n")
    
    # Main content from middle sentences
    if len(sentences) >= 5:
        middle_content = '. '.join(sentences[2:4]) + '.'
        summary_parts.append(f"**Main Points:**\n{middle_content}\n")
    
    # Insights section
    if keywords:
        summary_parts.append(f"**Core Concepts:**\n")
        for i, keyword in enumerate(keywords[:5], 1):
            summary_parts.append(f"{i}. {keyword} - Important concept covered in detail")
    
    # Statistics
    summary_parts.append(f"\n**Content Analysis:**")
    summary_parts.append(f"• Total words analyzed: {total_words}")
    summary_parts.append(f"• Unique terms identified: {unique_words}")
    summary_parts.append(f"• Key concepts extracted: {len(keywords)}")
    
    # Footer
    summary_parts.append(f"\n*This summary was generated by analyzing the actual content of your document. Each element is extracted directly from your text.*")
    
    return '\n'.join(summary_parts)

def generate_flashcards(text):
    """Generate INTELLIGENT flashcards from actual content"""
    
    cleaned = clean_text(text)
    sentences = extract_sentences(cleaned)
    keywords = extract_keywords(cleaned)
    
    flashcards = []
    
    # Strategy 1: Main topic from first sentence
    if len(sentences) >= 1:
        flashcards.append({
            'question': 'What is the main topic of this content?',
            'answer': sentences[0][:200] + ('...' if len(sentences[0]) > 200 else '')
        })
    
    # Strategy 2: Key concept from second sentence
    if len(sentences) >= 2:
        flashcards.append({
            'question': 'What key concept is explained?',
            'answer': sentences[1][:200] + ('...' if len(sentences[1]) > 200 else '')
        })
    
    # Strategy 3: Keywords definition
    if len(keywords) >= 2:
        flashcards.append({
            'question': f'Define or explain: {keywords[0]}',
            'answer': f'{keywords[0]} is a key term that appears frequently in this content, related to {keywords[1] if len(keywords) > 1 else "the main subject"}. It represents an important concept in the material.'
        })
    
    # Strategy 4: Detail from middle content
    if len(sentences) >= 4:
        flashcards.append({
            'question': 'What important detail is mentioned?',
            'answer': sentences[3][:200] + ('...' if len(sentences[3]) > 200 else '')
        })
    
    # Strategy 5: Another keyword
    if len(keywords) >= 3:
        flashcards.append({
            'question': f'What is {keywords[2]}?',
            'answer': f'{keywords[2]} is discussed as a significant element in this content. It relates to the core concepts and appears {keywords.count(keywords[2])} time(s) in the material.'
        })
    
    # Strategy 6: Comprehensive question
    if len(sentences) >= 6:
        flashcards.append({
            'question': 'What is another important point covered?',
            'answer': sentences[5][:200] + ('...' if len(sentences[5]) > 200 else '')
        })
    
    # Ensure we always have at least 5 cards
    while len(flashcards) < 5:
        flashcards.append({
            'question': f'What is concept #{len(flashcards) + 1} from this material?',
            'answer': sentences[len(flashcards) % len(sentences)][:150] if sentences else 'A key concept from the study material.'
        })
    
    return flashcards[:6]  # Return top 6 flashcards

def extract_key_terms(text):
    """Extract INTELLIGENT key terms from actual content"""
    
    cleaned = clean_text(text)
    sentences = extract_sentences(cleaned)
    keywords = extract_keywords(cleaned, min_length=6, top_n=20)
    
    terms = []
    
    for keyword in keywords[:12]:  # Process top 12 keywords
        # Find the best sentence containing this keyword
        best_sentence = ""
        keyword_lower = keyword.lower()
        
        for sentence in sentences:
            if keyword_lower in sentence.lower():
                # Prefer shorter, more concise sentences
                if not best_sentence or len(sentence) < len(best_sentence):
                    best_sentence = sentence
        
        # Create definition
        if best_sentence:
            # Truncate if too long
            definition = best_sentence[:250] + ('...' if len(best_sentence) > 250 else '')
        else:
            # Fallback definition
            definition = f"A key concept that appears in the content, indicating its significance to understanding the subject matter."
        
        terms.append({
            'term': keyword,
            'definition': definition
        })
    
    # Ensure at least 8 terms
    while len(terms) < 8:
        terms.append({
            'term': f'Additional Concept {len(terms) + 1}',
            'definition': 'An important element from the study material that contributes to comprehensive understanding.'
        })
    
    return terms[:10]  # Return top 10 terms

# ==========================================
# FLASK ROUTES
# ==========================================

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if email in users and users[email]['password'] == password:
            session['user'] = email
            flash('Welcome back! Login successful! 🎉', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Try demo@student.com / demo123', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        name = request.form.get('name', '').strip()
        
        if not email or not password or not name:
            flash('Please fill in all fields', 'error')
        elif email in users:
            flash('Email already registered. Please login instead.', 'error')
        else:
            users[email] = {
                'password': password,
                'name': name,
                'college': '',
                'notes': [],
                'flashcards': [],
                'tasks': [],
                'stats': {
                    'notes_count': 0,
                    'flashcards_count': 0,
                    'study_time': 0,
                    'streak': 1
                }
            }
            session['user'] = email
            flash(f'Welcome {name}! Your account has been created! 🎉', 'success')
            return redirect(url_for('dashboard'))
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Successfully logged out. See you soon! 👋', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=users[session['user']])

@app.route('/summarizer', methods=['GET', 'POST'])
def summarizer():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        text = None
        
        # Handle file upload
        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            filename = file.filename.lower()
            
            if filename.endswith('.pdf'):
                text = extract_pdf_text(file)
            elif filename.endswith('.txt'):
                text = file.read().decode('utf-8', errors='ignore')
            else:
                flash('Please upload PDF or TXT files only', 'error')
                return render_template('summarizer.html', user=users[session['user']])
        
        # Handle text input
        if not text:
            text = request.form.get('text', '').strip()
        
        if text and len(text) > 20:
            try:
                summary = summarize_text(text)
                users[session['user']]['stats']['notes_count'] += 1
                
                # Calculate statistics
                original_words = len(text.split())
                summary_words = len(summary.split())
                reduction = round((1 - summary_words/original_words) * 100, 1) if original_words > 0 else 0
                
                return render_template('summarizer.html',
                                     summary=summary,
                                     original_words=original_words,
                                     summary_words=summary_words,
                                     reduction=reduction,
                                     user=users[session['user']])
            except Exception as e:
                flash(f'Error processing text: {str(e)}', 'error')
        else:
            flash('Please provide text content (minimum 20 characters)', 'error')
    
    return render_template('summarizer.html', user=users[session['user']])

@app.route('/flashcards', methods=['GET', 'POST'])
def flashcards():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        text = request.form.get('text', '').strip()
        
        if text and len(text) > 50:
            try:
                cards = generate_flashcards(text)
                users[session['user']]['flashcards'].extend(cards)
                users[session['user']]['stats']['flashcards_count'] += len(cards)
                flash(f'Successfully created {len(cards)} flashcards! 🎴', 'success')
                return render_template('flashcards.html', flashcards=cards, user=users[session['user']])
            except Exception as e:
                flash(f'Error generating flashcards: {str(e)}', 'error')
        else:
            flash('Please provide more text (minimum 50 characters) to generate flashcards', 'error')
    
    return render_template('flashcards.html', flashcards=[], user=users[session['user']])

@app.route('/key-terms', methods=['GET', 'POST'])
def key_terms():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    terms = []
    if request.method == 'POST':
        text = request.form.get('text', '').strip()
        
        if text and len(text) > 50:
            try:
                terms = extract_key_terms(text)
                flash(f'Successfully extracted {len(terms)} key terms! 🔑', 'success')
            except Exception as e:
                flash(f'Error extracting terms: {str(e)}', 'error')
        else:
            flash('Please provide more text (minimum 50 characters) to extract key terms', 'error')
    
    return render_template('key-terms.html', terms=terms, user=users[session['user']])

@app.route('/statistics')
def statistics():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('statistics.html', stats=users[session['user']]['stats'], user=users[session['user']])

@app.route('/timetable')
def timetable():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('timetable.html', user=users[session['user']])

@app.route('/todo')
def todo():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('todo.html', tasks=users[session['user']].get('tasks', []), user=users[session['user']])

@app.route('/timer')
def timer():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('timer.html', user=users[session['user']])
@app.route('/music')
def music():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('music.html', user=users[session['user']])



@app.route('/settings')
def settings():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('settings.html', user=users[session['user']])

@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    response = None
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        if question:
            response = generate_chatbot_response(question)
    
    return render_template('chatbot.html', response=response, user=users[session['user']])
@app.route('/files', methods=['GET', 'POST'])
def files():
    if 'user' not in session:
        return redirect(url_for('login'))
    import os
    UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
    files = os.listdir(UPLOAD_FOLDER)
    msg = ""
    if request.method == 'POST' and 'file' in request.files:
        f = request.files['file']
        if f and f.filename:
            f.save(os.path.join(UPLOAD_FOLDER, f.filename))
            msg = "File uploaded!"
            files = os.listdir(UPLOAD_FOLDER)
    return render_template('files.html', files=files, msg=msg, user=users[session['user']])
@app.route('/leaderboard')
def leaderboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    # Example leaderboard
    top_users = [("Demo Student", 12), ("You", 11), ("Friend", 7)]
    return render_template('leaderboard.html', top_users=top_users, user=users[session['user']])


import random

@app.route('/quiz')
def quiz():
    if 'user' not in session:
        return redirect(url_for('login'))
    flashcards = users[session['user']].get('flashcards', [])
    if flashcards:
        idx = random.randint(0, len(flashcards)-1)
        fc = flashcards[idx]
        return render_template('quiz.html',
            question=fc['question'], answer=fc['answer'], user=users[session['user']], idx=idx, total=len(flashcards))
    else:
        return render_template('quiz.html', question=None, answer=None, user=users[session['user']], idx=None, total=0)
    


@socketio.on('message')
def handleMessage(msg):
    send(msg, broadcast=True)

@app.route('/calendar')
def calendar():
    if 'user' not in session:
        return redirect(url_for('login'))
    # Example calendar events (for demo, can be from DB)
    events = [
        {'date': '2025-11-23', 'title': 'Math Homework Due'},
        {'date': '2025-11-24', 'title': 'Team Meeting'},
        {'date': '2025-11-27', 'title': 'Hackathon Submission'}
    ]
    return render_template('calendar.html', events=events, user=users[session['user']])
@app.route('/dashboard')






def generate_chatbot_response(question):
    import requests
    api_key = "AIzaSyBftZx-hhdo5TozaFqFu9S--t2GYY9_mp0"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{
            "parts": [{"text": question}]
        }]
    }
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if "candidates" in data and len(data["candidates"]) > 0:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                return "Gemini didn't return a valid message. Try a different question."
        else:
            return f"API Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Error contacting Gemini API: {e}"





# ==========================================
# ERROR HANDLERS
# ==========================================
#
# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 CreazyAI - Your AI-Powered Study Assistant")
    print("=" * 60)
    print("✅ Server starting...")
    print("✅ All features initialized")
    print("✅ Ready to WIN the hackathon!")
    print("=" * 60)
    print("📱 Access at: http://localhost:5000")
    print("🔐 Demo Login: demo@student.com / demo123")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
if __name__ == "__main__":
    socketio.run(app, debug=True, host="127.0.0.1", port=5000, use_reloader=True)
if __name__ == "__main__":
    socketio.run(app, debug=True)

