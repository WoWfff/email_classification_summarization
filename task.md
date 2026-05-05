Його базова суть така: потрібно побудувати Python-сервіс, який споживає повідомлення з Kafka, обробляє їх через AI-агент, зберігає результат у PostgreSQL і публікує результати в окремі Kafka topics. Також важливо врахувати можливість multi-instance deployment.

Одразу хочу уточнити кілька важливих моментів, щоб правильно зорієнтувати тебе в очікуваннях:
Це завдання не спрямоване на закриття якоїсь конкретної продуктової потреби. Його мета - оцінити твоє розуміння побудови потокової обробки даних, оскільки в нашому продукті подібні підходи використовуються практично в усіх сервісах.
Ми очікуємо саме MVP / POC, а не production-ready рішення. Тобто не потрібно витрачати багато часу на повноцінне підняття й тонке налаштування інфраструктури. Водночас буде плюсом, якщо ти коротко опишеш, що саме потрібно було б додати або змінити, щоб довести рішення до production-рівня.

Для підняття Kafka і PostgreSQL бажано використати TestContainers - там “out of the box” вже є майже все необхідне через готові modules. Сам фокус завдання - не в інфраструктурі, а в логіці сервісу та архітектурному мисленні.
Якщо виникнуть проблеми з підняттям або налаштуванням Kafka, не варто на цьому зациклюватися. У такому випадку достатньо написати код consumer’а так, щоб ти могла пояснити, як саме він мав би працювати в реальному сценарії. Повідомлення в Kafka можна пушити або з command line, або через той самий TestContainer.

Для PostgreSQL не потрібно робити повноцінні міграції. Достатньо простого SQL-скрипта для створення таблиць.

Щодо blob storage: достатньо прикрити це інтерфейсом, а під капотом можна зберігати дані локально, поруч із застосунком.
Також окремо зазначу: у нас за інфраструктуру відповідає DevOps-команда. Розробники можуть пропонувати зміни, вимоги або покращення, але імплементація інфраструктурних рішень зазвичай лежить на DevOps. Тому в межах цього завдання для нас важливіше побачити правильні архітектурні підходи, ніж повноцінно зібрану інфраструктуру.
Загалом ми очікуємо MVP із коректною архітектурною логікою, розумінням того, що потрібно буде покращити для production, і врахуванням multi-instance сценарію.
Якщо по ходу виконання виникнуть додаткові питання - пиши

Build a Python service that:
    1. Consumes messages from a Kafka topic. Message contains only email header recipients/subject and path to body blob. Body stored somewhere externally.
    2. Processes message with an AI agent (LangGraph) – email classification, and summarization.
    3. Stores processing result in DB (PostgreSQL).
    4. Produces messages to another Kafka topics with the info about AI processing results. One topic for summarization, another for classification results.
    5. Should be able to work in multi-instance deployment.
Final solution should contain:
    • set of python files
    •  required configuration
    • Docker file for deployment