from transformers import pipeline
import textstat
import json
import re
import os
import torch

# Set seed for consistent results
torch.manual_seed(42)

# === Remove old JSON if exists ===
if os.path.exists("simulated_kid_results.json"):
    os.remove("simulated_kid_results.json")

# === Load model ===
generator = pipeline("text2text-generation", model="google/flan-t5-small")

# === UK Age Mapping Function ===
def uk_reading_age(grade_score):
    mapping = {
        0: "Reception or Year 1",
        1: "Year 2",
        2: "Year 3",
        3: "Year 4",
        4: "Year 5",
        5: "Year 6",
    }
    if grade_score <= 0.9:
        return "suitable for ages 5–6 (Reception or Year 1)", True
    elif grade_score <= 1.9:
        return "suitable for ages 6–7 (Year 2)", True
    elif grade_score <= 2.9:
        return "suitable for ages 7–8 (Year 3)", True
    elif grade_score <= 3.9:
        return "suitable for ages 8–9 (Year 4)", True
    elif grade_score <= 4.9:
        return "suitable for ages 9–10 (Year 5)", True
    elif grade_score <= 5.9:
        return "suitable for ages 10–11 (Year 6)", True
    else:
        return "above the target age range (11+)", False

# === Clean up generated output ===
def clean_response(text):
    text = re.sub(r"(?i)you are 8 years old[\.,]?\s*", "", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip().capitalize()

# === Core Functions ===
def simulate_kid_response(lesson_text):
    prompt = (
        f"Pretend you're 8 years old and just learned this at school:\n{lesson_text}\n\n"
        f"What would you tell your friend about it? Use two short, simple sentences."
    )

    result = generator(prompt, max_length=150, truncation=True)[0]['generated_text']
    response = clean_response(result)

    # Light filter: regenerate if too short or echo
    if len(response.split()) < 5 or "you learned this" in response.lower():
        result = generator(prompt, max_length=150, truncation=True)[0]['generated_text']
        response = clean_response(result)

    score = textstat.flesch_kincaid_grade(response)
    age_range, is_suitable = uk_reading_age(score)
    return response, score, age_range, is_suitable


def simulate_activity_feedback(lesson_text, activity_type):
    activity_prompt_map = {
        "quiz": "You answered some quiz questions about it.",
        "fill_in_the_blank": "You filled in missing words to complete important sentences.",
        "drag_and_drop": "You sorted things into safe and unsafe categories."
    }

    activity_description = activity_prompt_map.get(activity_type, "You did an activity about the topic.")

    prompt = (
        f"Pretend you're 8 years old and you just did this activity:\n{activity_description}\n"
        f"It was part of a lesson about online safety:\n{lesson_text}\n\n"
        f"How did you feel about the activity? Was it helpful or fun? Say it in two short sentences like you're telling your friend."
    )

    result = generator(prompt, max_length=150, truncation=True)[0]['generated_text']
    response = clean_response(result)

    # Light filter: regenerate if too short or too generic
    if len(response.split()) < 6 or response.lower() in ["helpful", "fun", "good"]:
        result = generator(prompt, max_length=150, truncation=True)[0]['generated_text']
        response = clean_response(result)

    score = textstat.flesch_kincaid_grade(response)
    age_range, is_suitable = uk_reading_age(score)
    return response, score, age_range, is_suitable

# === Load Lessons ===
lessons = [
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

# === Run and collect results ===
results_dict = {}

for lesson in lessons:
    lesson_name = lesson["name"]
    lesson_text = lesson["introduction"] + " " + lesson["why_it_matters"]
    activity_type = lesson["interactive_type"]

    kid_summary, kid_score, kid_range, kid_ok = simulate_kid_response(lesson_text)
    activity_feedback, act_score, act_range, act_ok = simulate_activity_feedback(lesson_text, activity_type)

    print(f"\n\U0001F4DA Lesson: {lesson_name}")
    print(f"\U0001F4D8 Summary readability: {kid_range}")
    print(f"\n\U0001F3AF Activity type: {activity_type}")
    print(f"\U0001F5E3️  Feedback: {activity_feedback}")
    print(f"\U0001F4D8 Feedback readability: {act_range}")

    if not kid_ok or not act_ok:
        print("⚠️ Some content may be above the intended age range.")
    else:
        print("✅ Both summary and feedback are suitable")

    results_dict[lesson_name] = {
        "summary_readability_score": kid_score,
        "summary_age_range": kid_range,
        "activity_type": activity_type,
        "activity_feedback": activity_feedback,
        "activity_readability_score": act_score,
        "activity_age_range": act_range,
        "is_summary_suitable": kid_ok,
        "is_activity_suitable": act_ok
    }

# === Save results ===
with open("simulated_kid_results.json", "w") as f:
    json.dump(results_dict, f, indent=2)

print("\n✅ All lessons tested and saved to 'simulated_kid_results.json'")