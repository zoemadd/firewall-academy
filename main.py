import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

DB_PATH = 'users.db'  # Path to SQLite database

LESSONS = [
    {
        'id': 1,
        'name': 'Online Safety Basics',
        'introduction': 'Welcome! This lesson will teach you how to stay safe when using the internet. You will learn how to protect your personal information and what to do if something feels wrong online.',
        'why_it_matters': 'Staying safe online is just as important as staying safe in real life. By learning these rules, you can have fun online while keeping yourself safe from people who might want to trick you.',
        'key_concepts': [
            'Keep Your Personal Information Secret - Never share your full name, address, school, or phone number with people online.',
            'Talk to a Grown-Up - If someone says or does something online that makes you feel confused or scared, tell a grown-up you trust.',
            'Be Careful with Strangers - Not everyone online is who they say they are. Only talk to people you know in real life.',
            'Think Before You Click - Always ask a grown-up before clicking on links, downloading things, or sharing pictures.',
            'Use Safe Websites - Stick to websites, games, and videos that a parent or teacher says are safe for kids.'
        ],
        'interactive_type': 'quiz',
        'interactive_content': [
            {
                'question': 'What should you do if someone online asks where you live?',
                'options': ['Tell them', 'Keep it a secret', 'Ask them where they live'],
                'answer': 'Keep it a secret'
            },
            {
                'question': 'Who should you tell if you see something scary online?',
                'options': ['A friend', 'A trusted adult', 'No one'],
                'answer': 'A trusted adult'
            },
            {
                'question': 'Is it okay to talk to strangers online?',
                'options': ['Yes, if they are nice', 'Only if they know your friend', 'No, always ask a grown-up first'],
                'answer': 'No, always ask a grown-up first'
            },
            {
                'question': 'Why should you ask a grown-up before clicking on a link?',
                'options': ['To make sure it is safe', 'Because it’s fun', 'So you can share your information'],
                'answer': 'To make sure it is safe'
            },
            {
                'question': 'What kind of websites are safe to visit?',
                'options': ['Any website', 'Websites your parent or teacher says are safe', 'Websites with lots of pop-ups'],
                'answer': 'Websites your parent or teacher says are safe'
            }
        ]
    },
    {
        'id': 2,
        'name': 'Password Best Practices',
        'introduction': 'Learn how to create strong passwords to keep your devices safe.',
        'why_it_matters': 'Strong passwords protect your information from hackers and keep your devices secure.',
        'key_concepts': [
            'Use a mix of letters, numbers, and symbols.',
            'Avoid using easy-to-guess passwords like "1234" or your name.',
            'Change your password regularly and never share it with others.'
        ],
        'interactive_type': 'quiz',
        'interactive_content': [
            {
                'question': 'Which password is the strongest?',
                'options': ['123456', 'P@ssw0rd!', 'MyName2023'],
                'answer': 'P@ssw0rd!'
            },
            {
                'question': 'Why is "1234" a bad password?',
                'options': ['It is too short', 'It is easy to guess', 'It is hard to remember'],
                'answer': 'It is easy to guess'
            }
        ]
    },
    {
        'id': 3,
        'name': 'Recognising Malicious Apps and Downloads',
        'introduction': 'Learn how to spot and avoid dangerous apps or downloads.',
        'why_it_matters': 'Malicious apps can steal your information or damage your device if you are not careful.',
        'key_concepts': [
            'Only download apps from official app stores.',
            'Check permissions before installing new apps.',
            'If you are unsure about an app, ask an adult.'
        ],
        'interactive_type': 'simulation',
        'interactive_content': '<iframe src="https://your-vm-url.com" width="800" height="600"></iframe>'
    },
    {
        'id': 4,
        'name': 'Safe Use of Voice Assistants',
        'introduction': 'Learn how to safely interact with voice assistants like Alexa or Siri.',
        'why_it_matters': 'Voice assistants can accidentally share personal information if not used carefully.',
        'key_concepts': [
            'Only use voice assistants with adult supervision.',
            'Do not share private information with voice assistants.',
            'Turn off voice assistants when not in use.'
        ],
        'interactive_type': 'simulation',
        'interactive_content': '<iframe src="https://your-vm-url.com" width="800" height="600"></iframe>'
    },
    {
        'id': 5,
        'name': 'Cyberbullying Awareness',
        'introduction': 'Recognize and respond to cyberbullying.',
        'why_it_matters': 'Knowing how to handle cyberbullying helps keep the internet a safe place.',
        'key_concepts': [
            'Always speak to a trusted adult if you experience or witness bullying.',
            'Block and report users who are unkind or threatening.',
            'Be kind and respectful to others online.'
        ],
        'interactive_type': 'quiz',
        'interactive_content': [
            {
                'question': 'What should you do if you are bullied online?',
                'options': ['Ignore it', 'Fight back', 'Tell a trusted adult'],
                'answer': 'Tell a trusted adult'
            },
            {
                'question': 'Is it okay to share someone else’s private information?',
                'options': ['Yes, if it is funny', 'No, it is private', 'Only with friends'],
                'answer': 'No, it is private'
            }
        ]
    },
    {
        'id': 6,
        'name': 'Online Privacy and Personal Information',
        'introduction': 'Learn how to protect your private information online.',
        'why_it_matters': 'Protecting your personal data keeps you safe from identity theft and scams.',
        'key_concepts': [
            'Do not share personal information with strangers.',
            'Check privacy settings on devices and apps.',
            'Always ask an adult before sharing anything online.'
        ],
        'interactive_type': 'simulation',
        'interactive_content': '<iframe src="https://your-vm-url.com" width="800" height="600"></iframe>'
    }
]

USERS = {
    'user@example.com': 'password123'
}

# Connect to SQLite Database
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access rows as dictionaries
    return conn

# Check if user is logged in (helper function)
def is_logged_in():
    return 'user' in session

# Register a new user
def register_user(email, password):
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, password))
        conn.commit()
    except sqlite3.IntegrityError:
        return False  # User already exists
    finally:
        conn.close()
    return True

# Validate login credentials
def validate_user(email, password):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password)).fetchone()
    conn.close()
    return user

# Sign-Up Page Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if register_user(email, password):
            return redirect(url_for('login'))  # Successful sign-up, go to login page
        else:
            return render_template('signup.html', error="User already exists.", logged_in=False)

    return render_template('signup.html', logged_in=False)

# Dynamic Lesson Route (with login protection)
@app.route('/lesson/<int:lesson_id>', methods=['GET', 'POST'])
def lesson(lesson_id):
    # Ensure user is logged in
    if not is_logged_in():
        return redirect(url_for('login', next=request.path))

    # Find the lesson by ID
    lesson = next((l for l in LESSONS if l['id'] == lesson_id), None)
    if not lesson:
        return "Lesson not found", 404

    # Retrieve the user's email from the session
    user_email = session['user']

    # Fetch saved progress (if any)
    user_progress = get_user_progress(user_email)
    saved_score = next((p[1] for p in user_progress if p[0] == f'lesson_{lesson_id}'), None)

    # Handle Quiz Submission and Save Progress
    if request.method == 'POST' and lesson['interactive_type'] == 'quiz':
        user_answers = request.form

        # Calculate score
        score = sum(1 for i, q in enumerate(lesson['interactive_content']) if user_answers.get(f'question-{i}') == q['answer'])

        # Save progress in the database
        save_progress(user_email, f'lesson_{lesson_id}', score)

        # Update saved_score to display immediately
        saved_score = score

    # Render the lesson page with saved score (if any)
    return render_template('lesson.html', lesson=lesson, score=saved_score, total=len(lesson['interactive_content']), enumerate=enumerate, logged_in=True)

# Lessons Page (Requires Login)
@app.route('/lessons')
def lessons():
    if not is_logged_in():
        return redirect(url_for('login', next=request.path))
    return render_template('lessons.html', lessons=LESSONS, logged_in=True)

@app.route('/')
def home():
    return render_template('index.html', logged_in=is_logged_in())

@app.route('/parental_advice')
def parental_advice():
    return render_template('parental_advice.html', logged_in=is_logged_in())


# Login Page Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        next_page = request.args.get('next') or url_for('home')

        if validate_user(email, password):
            session['user'] = email
            return redirect(next_page)  # Redirect to intended page

        return render_template('login.html', error="Invalid credentials", logged_in=False)

    return render_template('login.html', logged_in=False)


# Logout Route
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

# Saving progress of the activities
def save_progress(user_email, quiz_id, score):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO progress (user_email, quiz_id, score) 
        VALUES (?, ?, ?)
        ON CONFLICT(user_email, quiz_id) 
        DO UPDATE SET score=excluded.score;
    ''', (user_email, quiz_id, score))

    conn.commit()
    conn.close()

def get_user_progress(user_email):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('SELECT quiz_id, score FROM progress WHERE user_email = ?', (user_email,))
    progress = cursor.fetchall()

    conn.close()
    return progress

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_progress = get_user_progress(session['user_email'])
    return render_template('dashboard.html', progress=user_progress)

if __name__ == '__main__':
    app.run(debug=True)
