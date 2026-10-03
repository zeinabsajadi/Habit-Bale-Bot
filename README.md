🤖 Habit Tracker Bot for Bale

A habit-tracking bot built for Bale Messenger, designed to help users build consistent habits through daily reminders, progress tracking, streaks, statistics, and personalized feedback.

The project combines a conversational bot interface with a persistent database and scheduled background tasks to create a lightweight habit-tracking system.

✨ Features

📝 Habit Management

- Add and manage personal habits
- Set a daily reminder time for each habit
- Change or deactivate existing habits
- Track daily completion status

⏰ Automated Reminders

- Scheduled daily habit reminders
- Timezone-aware scheduling using "Asia/Tehran"
- Automatic handling of unanswered daily habits
- Background scheduling with APScheduler

📊 Progress & Statistics

- Current success streaks
- Missed-day streaks
- Habit completion statistics
- Progress tracking over time
- User-level behavioral statistics

💬 Conversational User Flow

The bot uses state-based conversation flows to guide users through multi-step interactions such as adding habits, changing settings, and reporting missed habits.

User states are handled explicitly so that incoming messages can be routed according to the current interaction flow.

🧠 Personalized Feedback

When a user misses a habit, the bot can ask for the reason in free text and analyze the response using predefined rules.

The system stores the resulting failure category and uses user statistics such as:

- Current streak
- Missed-day streak
- Recent comeback behavior
- Habit completion status
- Relationship score

to support personalized responses.

🎬 Context-Aware GIF Responses

The project includes a GIF response system that selects responses based on the user's current habit-tracking context.

This creates a more engaging and personalized interaction instead of relying only on static text messages.

🏗️ Architecture

The project is organized into several focused modules:

Habit-Bale-Bot/
│
├── bot.py
├── handlers.py
├── database.py
├── scheduler.py
├── user_stats.py
├── failure_reason_analyzer.py
├── gif_sender.py
├── gifs.py
├── messages.py
├── config.py
├── upload_gifs.py
├── utils.py
│
├── gifs/
├── requirements.txt
└── habit_tracker.db

Main Components

"bot.py"
Initializes the Bale bot, registers event handlers, initializes the database, and starts the scheduler.

"handlers.py"
Contains the main conversational flows and command/message handling logic.

"database.py"
Defines the SQLAlchemy models and database session management for users, habits, and daily logs.

"scheduler.py"
Runs scheduled jobs for habit reminders and daily status processing.

"user_stats.py"
Calculates user-level statistics used by the personalized response system.

"failure_reason_analyzer.py"
Processes free-text failure reasons and maps them to predefined categories.

"gif_sender.py" / "gifs.py"
Manage context-aware GIF responses.

🛠️ Tech Stack

- Python
- Bale Bot API / python-bale-bot
- SQLAlchemy
- SQLite
- APScheduler
- python-dotenv
- pytz
- asyncio

The dependency list is defined in "requirements.txt".

🔄 Interaction Flow

A typical daily flow looks like this:

User
  │
  ▼
Bale Messenger
  │
  ▼
Habit Bot
  │
  ├── Check active habits
  │
  ├── Send scheduled reminder
  │
  ▼
User response
  │
  ├── Completed
  │      └── Update daily log
  │
  └── Not completed
         │
         ├── Ask for reason
         ├── Analyze response
         ├── Store failure category
         └── Generate contextual feedback

🚀 Getting Started

1. Clone the repository

git clone https://github.com/zeinabsajadi/Habit-Bale-Bot.git
cd Habit-Bale-Bot

2. Create a virtual environment

python -m venv .venv
source .venv/bin/activate

On Windows:

.venv\Scripts\activate

3. Install dependencies

pip install -r requirements.txt

4. Configure environment variables

Create a ".env" file:

BALE_BOT_TOKEN=your_bot_token

The application loads the bot token through "python-dotenv".

5. Run the bot

python bot.py

The application initializes the database and starts the Bale bot and scheduler.

🗃️ Data Model

The application uses SQLAlchemy with SQLite for persistence.

The core entities include:

- User — stores user information and behavioral metadata
- Habit — represents a user's tracked habit
- DailyLog — stores daily completion records

Users can have multiple habits, while each habit is associated with daily tracking records.

🎯 Project Goals

This project was built to explore the engineering challenges behind a conversational habit-tracking system, including:

- Event-driven bot development
- Stateful conversational flows
- Database modeling and persistence
- Scheduled background jobs
- Behavioral data aggregation
- Rule-based text analysis
- Context-aware user feedback

📌 Future Improvements

Possible directions for future development include:

- PostgreSQL support for production deployments
- Redis-based state management
- More robust natural-language analysis of failure reasons
- Improved analytics and visualization
- Web-based administration
- Automated testing
- Dockerized deployment
- More sophisticated personalization models

📄 License

This project is currently intended as a personal learning and development project.
