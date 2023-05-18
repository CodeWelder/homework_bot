"""Модуль с кастомными исключениями проекта."""


class TokensAreNone(Exception):
    """Отсутствуют критичные для работы приложения токены."""
    pass


class APIReturnsIncorrectHTTPStatus(Exception):
    """Запрос к API возвращает статус отличный от 200."""
    pass


class APIRequestException(Exception):
    """Запрос к API возвращает RequestException."""
    pass


class APIReturnsIncorrectHomeworkData(Exception):
    """Ответ API содержит пустой или некорректный статус
    или наименование домашней работы."""
    pass
