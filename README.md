🚨 SafeGo AI- Because safety shouldn’t be optional.

🧠 What is SafeGo AI?
SafeGo AI is basically my attempt at solving a very real problem — personal safety, especially in unpredictable situations.It’s an AI-powered web app that helps detect risky or unsafe scenarios and respond intelligently. The idea is simple:
If something feels off, the system should already be working for you.
This project combines AI + web development + real-world usability into one clean platform.

⚙️ What it does
🔍 Detects suspicious situations using AI models
📸 Works with image/video input (real-time or uploaded)
🚨 Gives alerts or warnings when something seems unsafe
🌐 Runs as a web application (Flask-based backend)
⚡ Designed to be fast, simple, and actually usable
🏗️ Tech Stack

-Frontend:                   
HTML5                                    
CSS3                                      
JavaScript
Jinja Templates (Flask)

-Backend:
Python
Flask

-AI/ML:
TensorFlow Lite (optimized for performance)
Pre-trained/custom models for detection

SafeGo-AI/
│
├── static/              # CSS, JS, assets
├── templates/           # HTML pages (Flask)
│   └── base.html        # Main layout
│
├── model/               # AI model files
├── main.py              # Flask app entry point
├── requirements.txt     # Dependencies
└── README.md

🚀 How to Run This Locally
1. Clone the repo
git clone https://github.com/your-username/safego-ai.git
cd safego-ai
2. Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
3. Install dependencies
pip install -r requirements.txt
4. Run the app
python main.py
5. Open in browser
http://127.0.0.1:5000/

🧪 Future Improvements
📱 Mobile-friendly UI
🔔 Real-time alert system (notifications / SMS)
🧠 Better and more accurate AI models
🌍 Live camera integration
🔐 User authentication + history tracking
