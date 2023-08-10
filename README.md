[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&pause=1000&color=13F7CF&width=435&lines=%D0%A2%D0%B5%D0%BB%D0%B5%D0%B3%D1%80%D0%B0%D0%BC+%D0%B1%D0%BE%D1%82-%D0%B0%D1%81%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BD%D1%82)](https://git.io/typing-svg)

## Описание

Бот-ассистент.Обращается к API сервиса Практикум.Домашка для получения статуса проверки домашних работ.

Принцип работы бота:
- с переодичностью раз в 10 минут опрашивает API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы.
- при обновлении статуса анализирует ответ API и отправляет соответствующее уведомление в Telegram

#### Технологии
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
- Python 3.9


#### Запуск проекта в dev-режиме

- Склонируйте репозиторий:  
``` git clone <название репозитория> ``` 
- Скопировать .env.example и назвать его .env:  
``` cp .env.example .env ```
- Заполнить переменные окружения в .env:  
``` PRACTICUM_TOKEN = токен_к_API_Практикум.Домашка ```  
``` TELEGRAM_TOKEN = токен_Вашего_Telegtam_бота ```  
``` TELEGRAM_CHAT_ID = Ваш_Telegram_ID ```
- Установите и активируйте виртуальное окружение:  
``` python -m venv venv ```  
``` source venv/Scripts/activate ``` 
- Установите зависимости из файла requirements.txt:   
``` pip install -r requirements.txt ```
