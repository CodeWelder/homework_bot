# homework_bot

## Short description
Python telegram bot для проверки статуса проверки домашней работы на платформе https://practicum.yandex.ru/.
Раз в 10 минут обращается к API и, если есть обновления, отправляет информацию на телеграм пользователя.

## Installation process
git clone https://github.com/CodeWelder/homework_bot.git
py -3.8 -m venv venv
source venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

## How to run
python homework.py