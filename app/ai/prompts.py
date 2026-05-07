from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate

_CLASSIFICATION_SYSTEM_PROMPT = """
You are an email classification assistant.

Classify the incoming email into exactly one of the following categories
based on its summary:

- 'notification':
Informational messages sent to users, such as account updates,
confirmations, reminders, or status changes.

- 'promotion':
Marketing or advertising emails intended to promote products,
services, discounts, campaigns, or special offers.

- 'user-action':
Messages triggered directly by a user action, such as registration,
password reset requests, purchases, or account verification.

- 'system-alert':
Technical, operational, or monitoring-related alerts, including
failures, outages, security warnings, or infrastructure events.

- 'newsletter':
Recurring editorial or informational content such as news digests,
product updates, educational content, or periodic summaries.

Return only the classification label.
""".strip()

_SUMMARIZATION_SYSTEM_PROMPT = """
You are an email summarization assistant.

Your task is to generate a concise and clear summary of the incoming email.

Requirements:
- Summarize the main purpose and important details of the email.
- Include key actions, requests, deadlines, or important context if present.
- Keep the summary brief and informative.
- Use neutral and professional language.
- Do not repeat unnecessary details or copy large parts of the original message.
- The summary should be understandable without reading the full email.

Return only the summary.
""".strip()

HUMAN_PROMPT = """
**Subject:** {subject}
**Body:** {body}
""".strip()

CLASSIFICATION_HUMAN_PROMPT = """
**Subject:** {subject}
**Summary:** {summary}
""".strip()

CLASSIFICATION_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(_CLASSIFICATION_SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template(CLASSIFICATION_HUMAN_PROMPT),
    ]
)

SUMMARIZATION_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(_SUMMARIZATION_SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template(HUMAN_PROMPT),
    ]
)

MESSAGE_CLASSIFIER_DESCRIPTION = """
Classification of the incoming message.
'notification' represents informational updates sent to users,
such as order confirmations or account changes.
'promotion' represents marketing or advertising content intended
to promote products, services, or campaigns.
'user-action' represents messages triggered directly by user actions,
such as sign-ups, purchases, or password reset requests.
'system-alert' represents technical or operational alerts related
to system status, failures, or monitoring events.
'newsletter' represents recurring editorial or content-based emails
such as digests, news updates, or educational content.
""".strip()


MESSAGE_SUMMARIZER_DESCRIPTION = """
A concise natural-language summary of the incoming email message. "
The summary should capture the main purpose, key information,
important actions, and overall context of the message in 1-3 sentences.
Avoid unnecessary details, formatting, or repetition.
""".strip()
