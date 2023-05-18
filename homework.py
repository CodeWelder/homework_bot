import time
import logging
from os import getenv
from http import HTTPStatus
from typing import Optional, Dict, List, Any

import requests

from telegram import Bot

from dotenv import load_dotenv

from exceptions import (
    TokensAreNone,
    APIReturnsIncorrectHTTPStatus,
    APIRequestException,
    APIReturnsIncorrectHomeworkData,
)

# Загрузка переменных окружения
load_dotenv()
PRACTICUM_TOKEN: Optional[str] = getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN: Optional[str] = getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID: Optional[str] = getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD: int = 600  # 10 минут
TIME_WINDOW: int = 60 * 60 * 24 * 30  # 30 дней
ENDPOINT: str = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS: Dict[str, str] = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS: Dict[str, str] = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.DEBUG
)


def check_tokens() -> None:
    """Проверяет доступность переменных окружения.
    Если отсутствует хотя бы одна переменная окружения,
    останавливает бота с ошибкой.
    """
    TOKENS_DICT: Dict[str, Optional[str]] = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID,
    }

    tokens_are_none: List[str] = list(
        {key: value for key, value in TOKENS_DICT.items() if value is None}
    )
    ERROR_MESSAGE_TEMPLATE: str = (
        'Недоступны следующие переменные окружения: {}. '
        'Работа бота остановлена.'
    )
    if len(tokens_are_none) > 0:
        logging.critical(ERROR_MESSAGE_TEMPLATE.format(tokens_are_none))
        raise TokensAreNone(
            'Отсутствуют критичные для работы приложения токены.'
        )


def send_message(bot, message: str) -> None:
    """Отправляет сообщение в Telegram чат.
    Чат определяется переменной окружения TELEGRAM_CHAT_ID.
    Принимает на вход два параметра:
    экземпляр класса Bot и строку с текстом сообщения.
    """
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )
        logging.debug(f'Успешно отправлено сообщение: "{message}".')
    except Exception as error:
        logging.error(
            f'Не удалось отправить сообщение: "{message}". Ошибка: {error}.'
        )


def get_api_answer(timestamp: int):
    """Делает запрос к единственному эндпоинту API-сервиса.
    В функцию передается время в формате UNIX time.
    В случае успешного запроса возвращает ответ API,
    приведенный к типам данных Python,
    иначе - поднимает APIReturnsIncorrectHTTPStatus.
    """
    payload: Dict[str, int] = {'from_date': timestamp}

    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=payload
        )
    except requests.exceptions.RequestException as e:
        raise APIRequestException(
            f'Запрос к эндпойнту {ENDPOINT} возвращает исключение: {e}'
        )

    status_code = response.status_code
    if status_code == HTTPStatus.OK:
        response_dict = response.json()
        return response_dict
    else:
        raise APIReturnsIncorrectHTTPStatus(
            f'Эндпоинт {ENDPOINT} недоступен. '
            f'Код ответа API: {status_code}'
        )


def check_response(response_dict: Dict[str, Any]) -> bool:
    """Проверяет ответ API на соответствие документации.
    В качестве параметра функция получает ответ API,
    приведенный к типам данных Python.
    """
    result = (
        isinstance(response_dict, dict)
        and isinstance(response_dict.get('homeworks'), list)
    )
    if not result:
        raise TypeError('Ответ API не соответствует документации.')

    if not response_dict.get('homeworks'):
        logging.debug('В ответе API отсутствуют новые статусы.')
        result = False

    return result


def parse_status(homework) -> str:
    """Функция возвращает вердикт по домашней работе.
    Функция получает один элемент из списка домашних работ,
    извлекает наименование и статус этой работы,
    и возвращает строку с вердиктом из словаря HOMEWORK_VERDICTS.
    """
    homework_name: str = homework.get('homework_name')
    status: str = homework.get('status')
    verdict: Optional[str] = HOMEWORK_VERDICTS.get(status)

    if (
        status is None
        or status not in HOMEWORK_VERDICTS
        or homework_name is None
    ):
        raise APIReturnsIncorrectHomeworkData(
            f'Получены некоректный статус ({status}) '
            f'или наименование домашней работы ({homework_name}).'
        )

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main() -> None:
    """Основная логика работы бота: Сделать запрос к API, проверить ответ.
    Если есть обновления — получить статус работы из обновления
    и отправить сообщение в Telegram.
    Подождать некоторое время и вернуться в пункт 1.
    """
    check_tokens()
    bot: Bot = Bot(token=str(TELEGRAM_TOKEN))

    while True:
        try:
            time_from: int = int(time.time() - RETRY_PERIOD)
            response = get_api_answer(time_from)

            if check_response(response):
                homework = response.get('homeworks')[0]
                status: str = parse_status(homework)
                send_message(bot, status)

        except Exception as error:
            logging_message: str = f'Сбой в работе программы: {error}'
            logging.error(logging_message)
            send_message(bot, logging_message)

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
