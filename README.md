# homework_bot

## Short description
Python telegram bot для проверки статуса проверки домашней работы на платформе https://practicum.yandex.ru/.
Раз в 10 минут обращается к API и, если есть обновления, отправляет информацию на телеграм пользователя.

## Installation process
1. **Clone the project:** git clone https://github.com/CodeWelder/homework_bot.git
2. **Create environment:** python -m venv venv
3. **Activate environment:** source venv/Scripts/activate
4. **Upgrade pip:** python -m pip install --upgrade pip
5. **Install requirements:** pip install -r requirements.txt
6. **Add tokens:** Rename '.env_example' to '.env' and fill in all tokens.

## How to run
python homework.py
