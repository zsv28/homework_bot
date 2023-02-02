import logging
import os
import sys
import time
from http import HTTPStatus
from logging import Formatter, StreamHandler

import requests
import telegram
from dotenv import load_dotenv

from exceptions import EndpointError, EndpointStatusError

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = StreamHandler(stream=sys.stdout)
logger.addHandler(handler)
formatter = Formatter(
    '%(asctime)s, %(levelname)s, %(name)s, '
    '%(funcName)s, %(levelno)s, %(message)s'
)
handler.setFormatter(formatter)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверяет доступность токенов."""
    variables_data = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }
    no_value = [
        var_name for var_name, value in variables_data.items() if not value
    ]
    if no_value:
        logger.critical(
            f'Не задан токен для: {no_value}.'
        )
        return False
    logger.info('Все токены доступны.')
    return True


def send_message(bot, message):
    """Отправляет сообщения с информацией в Telegram."""
    try:
        logger.info('Идет отправка сообщения')
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except telegram.error.TelegramError as error:
        logger.error(f'Ошибка при отправке сообщения: {error}', exc_info=True)
    else:
        logging.debug(f'Сообщение: {message} - успешно отправлено')


def get_api_answer(current_timestamp):
    """Делает запрос к API сервису Яндекс Практикум."""
    logger.info('Выполняется запрос к API сервису Яндекс Практикум')
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        api_response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except requests.exceptions.RequestException as error:
        raise EndpointError(
            f'Проблема при обращении к {ENDPOINT}.Ошибка {error}'
        )
    if api_response.status_code != HTTPStatus.OK:
        raise EndpointStatusError(
            f'ENDPOINT {ENDPOINT} c параметрами {params} недоступен'
        )
    logger.info('Ответ API сервиса Яндекс Практикум успешно получен')
    return api_response.json()


def check_response(response):
    """Проверяет ответ API на корректность."""
    logger.info('Проверка корректного ответа API')
    if not isinstance(response, dict):
        raise TypeError(
            f'Тип данных ответа API не является словарём: {response}'
        )
    if 'homeworks' not in response:
        raise KeyError(
            'Ключ homeworks отсутствует в ответе API.'
            f'Ключи ответа: {response.keys()}'
        )
    homeworks = response['homeworks']
    if 'current_date' not in response:
        raise KeyError(
            'Ключ current_date отсутствует в ответе API.'
            f'Ключи ответа: {response.keys()}'
        )
    if not isinstance(homeworks, list):
        raise TypeError(
            'Тип данных значения по ключу homeworks'
            f'не является списком: {homeworks}'
        )
    logger.info('Ответ API корректен')


def parse_status(homework):
    """Извлекает статус проверки домашнего задания."""
    logger.info('Извлекается статус проверки домашнего задания')
    for key in ('homework_name', 'status'):
        if key not in homework:
            raise KeyError(
                'Отсутствует необходимый ключ для определения статуса '
                f'проверки домашнего задания: {key}'
            )
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status not in HOMEWORK_VERDICTS:
        raise ValueError(
            'Незадокументированный статус проверки '
            f'домашней работы: {homework_status}'
        )
    logger.info('Статус проверки домашнего задания получен')
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        message = 'Бот остановлен! Проверь корректность токенов.'
        sys.exit(message)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    info_message = ''
    while True:
        try:
            response = get_api_answer(current_timestamp)
            check_response(response)
            homeworks = response['homeworks']
            if not homeworks:
                logger.info('Список домашнего задания пуст')
                continue
            status_homework = parse_status(homeworks[0])
            if status_homework != info_message:
                info_message = status_homework
                send_message(bot, info_message)
            else:
                logger.debug(
                    'Статус проверки домашнего задания не обновлялся'
                )
            current_timestamp = response.get(
                'current_date', int(time.time())
            )
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if message != info_message:
                info_message = message
                logger.error(message)
                send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
