# BS4 Parser PEP

Парсер документации Python и PEP, реализованный с использованием BeautifulSoup.

## Возможности

Проект поддерживает несколько режимов работы:

- `whats-new` — парсинг списка обновлений Python;
- `latest-versions` — получение списка версий Python и их статусов;
- `download` — загрузка архива документации Python;
- `pep` — парсинг всех PEP, подсчёт количества документов по статусам и проверка соответствия статусов в общем списке и на страницах PEP.

Режим `pep` сохраняет статистику по статусам в CSV-файл.

## Технологии

- Python
- BeautifulSoup
- requests
- requests-cache
- tqdm
- PrettyTable

## Установка

Клонируйте репозиторий:

```bash
git clone git@github.com:Zh-zh-k/bs4_parser_pep.git
cd bs4_parser_pep
```

Создайте виртуальное окружение:

```bash
python -m venv venv
```

Активируйте его.

Для Linux/macOS:

```bash
source venv/bin/activate
```

Для Windows:

```bash
venv\Scripts\activate
```

Обновите pip:

```bash
python -m pip install --upgrade pip
```

Установите зависимости:

```bash
python -m pip install -r requirements.txt
```

## Запуск

Запуск парсера выполняется из корневой директории проекта:

```bash
python src/main.py <режим>
```

Доступные режимы:

```bash
python src/main.py whats-new
python src/main.py latest-versions
python src/main.py download
python src/main.py pep
```

## Дополнительные параметры

Очистить кэш:

```bash
python src/main.py pep --clear-cache
```

Вывести результат в виде таблицы:

```bash
python src/main.py pep --output pretty
```

Сохранить результат в CSV-файл:

```bash
python src/main.py pep --output file
```

CSV-файлы сохраняются в директорию:

```text
src/results/
```

## Режим PEP

В режиме `pep` программа:

- получает список всех PEP;
- исключает PEP 0;
- переходит на страницу каждого PEP;
- получает актуальный статус документа;
- сравнивает его со статусом в общем списке;
- записывает несовпадения в лог;
- подсчитывает количество PEP для каждого статуса;
- выводит общее количество документов.

Результат содержит две колонки:

```text
Статус,Количество
```

Последняя строка содержит общее количество PEP:

```text
Total,<количество>
```

## Логи

Логи работы парсера сохраняются в директорию:

```text
src/logs/
```
