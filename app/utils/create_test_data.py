# create_test_data.py
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DATA = {
    "monday_schedule.txt": """Good morning,

Here is the schedule for Monday:

09:00 – Team stand-up meeting
10:00 – Project planning session
12:00 – Lunch break
13:00 – Work on feature implementation
15:30 – Client call
17:00 – Wrap-up and notes

Please let me know if anything needs to be adjusted.

Best regards
""",
    "google.txt": """Security Alert,

We detected a new sign-in to your Google account from an unrecognized device.

Details:

* Location: Unknown
* Device: New browser session
* Time: Recently

If this was you, no further action is required.

If you do not recognize this activity, we strongly recommend that you:

* Change your password immediately
* Review your recent account activity
* Enable two-factor authentication

You can review your account security settings at any time.

Stay safe,
Google Security Team
""",
    "linkedin.txt": """Hello,

We are currently looking for a Backend Python Developer to join our team.

Position: Backend Engineer (Python)
Location: Remote / Hybrid
Employment type: Full-time

Responsibilities:

* Develop and maintain backend services
* Design and optimize APIs
* Work with databases and messaging systems
* Collaborate with cross-functional teams

Requirements:

* Strong experience with Python
* Familiarity with FastAPI or similar frameworks
* Experience with SQL databases
* Understanding of asynchronous programming

Nice to have:

* Experience with Kafka or similar systems
* Knowledge of Docker and CI/CD

We offer:

* Competitive salary
* Flexible working hours
* Opportunity to work on scalable systems
* Friendly and professional team

If you are interested, please reply to this message or send your CV.

Best regards
""",
    "daily_offer.txt": """Good day,

Here is today’s special offer:

* 20% discount on selected products
* Free delivery for orders over $50
* Limited-time bundle deals available

The offer is valid until the end of the day.

Don’t miss the chance to save.

Best regards
""",
}


def create_test_data() -> None:
    base = Path("data/blobs")
    base.mkdir(parents=True, exist_ok=True)
    for filename, content in DATA.items():
        (base / filename).write_text(content, encoding="utf-8")
    logger.info("Test blob files created.")
