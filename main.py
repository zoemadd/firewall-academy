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
            'Keep Your Personal Information Secret: Never share your full name, address, school, or phone number with people online.',
            'Talk to a Grown-Up: If someone says or does something online that makes you feel confused or scared, tell a grown-up you trust.',
            'Be Careful with Strangers: Not everyone online is who they say they are. Only talk to people you know in real life.',
            'Think Before You Click: Always ask a grown-up before clicking on links, downloading things, or sharing pictures.',
            'Use Safe Websites: Stick to websites, games, and videos that a parent or teacher says are safe for kids.'
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
        'introduction': 'Learn how to create strong passwords to keep your stuff safe online.',
        'why_it_matters': 'Strong passwords stop other people from looking at your things. They help to keep your accounts safe.',
        'key_concepts': [
            'Use a Mix: Make passwords with big and small letters, numbers, and symbols.',
            'Don’t Use Easy Ones: Don’t use simple words like "1234", "password", or your name.',
            'Keep It Secret: Only tell your password to a grown-up you trust.',
            'Change It Often: Change your passwords every so often to stay safe.',
            'Use Different Ones: Don’t use the same password for everything.'
        ],
        'interactive_type': 'fill_in_the_blank',
        'interactive_content': [
            {'text': 'A strong password should contain a mix of ___, numbers, and symbols.', 'answer': 'letters'},
            {'text': 'You should never share your password with ___ except a trusted adult.', 'answer': 'anyone'},
            {'text': 'It is a good habit to ___ your password regularly.', 'answer': 'change'}
        ],
        'word_bank': ['letters', 'anyone', 'change', 'symbols', 'forgot', 'secure', 'password', 'unique']

    },


    {
        'id': 3,
        'name': 'Recognising Malicious Apps and Downloads',
        'introduction': 'Find out how to spot bad apps or downloads that could hurt your device or take your information.',
        'why_it_matters': 'Some apps have viruses or tricks that can slow down your device or steal your details. Learning to spot them keeps you safe.',
        'key_concepts': [
            'Use Trusted Stores: Only get apps from safe places like the App Store or Google Play.',
            'Check What It Wants: If an app wants things it doesn’t need, be careful.',
            'Watch Out for Fakes: Some apps pretend to be real but are not. Check the name and reviews first.',
            'Too Good to Be True: Be careful of apps that promise free stuff like money or prizes.',
            'Ask a Grown-Up: If you’re not sure about an app, ask an adult before you download it.'
        ],
        'interactive_type': 'drag_and_drop',
        'interactive_content': {
            'draggable_items': [
                {'text': 'Official App Store', 'correct_zone': 'safe'},
                {'text': 'Suspicious Free Prize App', 'correct_zone': 'unsafe'},
                {'text': 'App Asking for Too Many Permissions', 'correct_zone': 'unsafe'},
                {'text': 'App with Good Reviews and Known Developer', 'correct_zone': 'safe'}
            ],
            'drop_zones': {
                'safe': 'Safe Apps & Downloads',
                'unsafe': 'Unsafe Apps & Downloads'
            }
        }
    },

    {
        'id': 4,
        'name': 'Safe Use of Voice Assistants',
        'introduction': 'Learn how to safely interact with voice assistants like Alexa, Siri, or Google Assistant while protecting your privacy.',
        'why_it_matters': 'Voice assistants can be helpful, but they may accidentally record or share personal information. Learning how to use them safely helps protect your privacy and security.',
        'key_concepts': [
            'Use With Adult Supervision: Always ask a grown-up before using a voice assistant, especially if you’re making purchases or searching for information.',
            'Do Not Share Private Information: Never tell a voice assistant your full name, address, school, or passwords.',
            'Check What It Records: Some voice assistants save what you say. Ask an adult to help check the settings and delete recordings if needed.',
            'Turn It Off When Not In Use: When you’re not using the voice assistant, turn it off or mute the microphone to protect your privacy.',
            'Be Careful With Smart Devices: Some voice assistants can control lights, locks, or other devices in your home. Only use these features with permission from a trusted adult.'
        ],
        'interactive_type': 'fill_in_the_blank',
        'interactive_content': [
            {'text': 'You should always ask a ___ before using a voice assistant.', 'answer': 'grown-up'},
            {'text': 'Never share your ___ with a voice assistant.', 'answer': 'personal information'},
            {'text': 'To protect your privacy, you should ___ the voice assistant when not in use.', 'answer': 'turn off'}
        ],
        'word_bank': ['grown-up', 'personal information', 'turn off', 'microphone', 'wake word', 'commands', 'recording', 'settings']

    },


    {
        'id': 5,
        'name': 'Cyberbullying Awareness',
        'introduction': 'Learn how to spot, stop, and deal with bullying that happens online.',
        'why_it_matters': 'Online bullying can make people feel sad or scared. Knowing what to do helps keep the internet kind.',
        'key_concepts': [
            'Tell a Grown-Up: If someone is being mean online, talk to a trusted adult.',
            'Block and Report: Stop bullies by blocking them and telling the app or website.',
            'Be Kind: Treat people online the way you want to be treated.',
            'Think Before You Post: Don’t say things online that could upset someone.',
            'Keep Info Private: Don’t share personal details. Bullies might use them to be mean.'
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
            },
            {
                'question': 'How can you help someone who is being cyberbullied?',
                'options': ['Join in the bullying', 'Encourage them to stay silent', 'Support them and help report it'],
                'answer': 'Support them and help report it'
            },
            {
                'question': 'What is the best way to respond to a mean message online?',
                'options': ['Reply with an angry message', 'Block and report the sender',
                            'Send it to all your friends'],
                'answer': 'Block and report the sender'
            }
        ]
    },

    {
        'id': 6,
        'name': 'Online Privacy and Personal Information',
        'introduction': 'Learn how to keep your private information safe while using the internet.',
        'why_it_matters': 'Sharing private stuff online can lead to problems like scams or strangers bothering you. Knowing how to stay private keeps you safe.',
        'key_concepts': [
            'Keep It Private: Don’t share your full name, address, school, phone number, or passwords.',
            'Check Settings: Ask an adult to help you set privacy settings on games, apps, and websites.',
            'Think Before You Share: Photos and videos can stay online forever. Ask a grown-up before you post anything.',
            'Don’t Trust Strangers: Never talk to or meet someone from the internet unless a grown-up says it’s okay.',
            'Use Strong Passwords: Make passwords that are hard to guess and keep them to yourself.'
        ],
        'interactive_type': 'drag_and_drop',
        'interactive_content': {
            'draggable_items': [
                {'text': 'Posting Full Name and Address', 'correct_zone': 'unsafe'},
                {'text': 'Using a Strong Password', 'correct_zone': 'safe'},
                {'text': 'Checking Privacy Settings', 'correct_zone': 'safe'},
                {'text': 'Talking to Strangers Online', 'correct_zone': 'unsafe'}
            ],
            'drop_zones': {
                'safe': 'Safe Online Practices',
                'unsafe': 'Unsafe Online Practices'
            }
        }
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
