import logging
import re
from collections import Counter
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (BASE_DIR, DOWNLOADS_DIR_NAME, EXPECTED_STATUS,
                       MAIN_DOC_URL, PEP_URL)
from exceptions import ParserDataException, ParserStatusException
from outputs import control_output
from utils import find_tag, get_response, get_soup


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    soup = get_soup(session, whats_new_url)

    main_div = find_tag(
        soup,
        'section',
        attrs={'id': 'what-s-new-in-python'}
    )
    div_with_ul = find_tag(
        main_div,
        'div',
        attrs={'class': 'toctree-wrapper'}
    )
    sections_by_python = div_with_ul.find_all(
        'li',
        attrs={'class': 'toctree-l1'}
    )

    results = [
        ('Ссылка на статью', 'Заголовок', 'Редактор, автор')
    ]
    errors = []

    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        version_link = urljoin(
            whats_new_url,
            version_a_tag['href']
        )

        try:
            soup = get_soup(session, version_link)
        except Exception as error:
            errors.append(
                f'Ошибка при обработке страницы '
                f'{version_link}: {error}'
            )
            continue

        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')

        dl_text = dl.text.replace('\n', ' ')

        results.append(
            (version_link, h1.text, dl_text)
        )

    for error in errors:
        logging.error(error)

    return results


def latest_versions(session):
    soup = get_soup(session, MAIN_DOC_URL)

    sidebar = find_tag(
        soup,
        'div',
        attrs={'class': 'sphinxsidebarwrapper'}
    )
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise ParserDataException(
            'Не найден список с версиями Python'
        )

    results = [
        ('Ссылка на документацию', 'Версия', 'Статус')
    ]

    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)

        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''

        results.append(
            (link, version, status)
        )

    return results


def download(session):
    downloads_url = urljoin(
        MAIN_DOC_URL,
        'download.html'
    )

    soup = get_soup(session, downloads_url)

    main_tag = find_tag(
        soup,
        'div',
        attrs={'role': 'main'}
    )
    table_tag = find_tag(
        main_tag,
        'table',
        attrs={'class': 'docutils'}
    )
    archive_tag = find_tag(
        table_tag,
        'a',
        attrs={
            'href': re.compile(r'.+docs-html\.zip$')
        }
    )

    archive_link = archive_tag['href']
    archive_url = urljoin(
        downloads_url,
        archive_link
    )

    filename = archive_url.split('/')[-1]

    downloads_dir = BASE_DIR / DOWNLOADS_DIR_NAME
    downloads_dir.mkdir(exist_ok=True)

    archive_path = downloads_dir / filename

    response = get_response(session, archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)

    logging.info(
        f'Архив был загружен и сохранён: {archive_path}'
    )


def get_pep_status(session, pep_url):
    soup = get_soup(session, pep_url)

    for dt_tag in soup.find_all('dt'):
        tag_text = dt_tag.get_text(strip=True).rstrip(':')

        if tag_text == 'Status':
            status_value = dt_tag.find_next_sibling('dd')

            if status_value is not None:
                return next(status_value.stripped_strings)

    raise ParserStatusException(
        f'Не найден статус PEP: {pep_url}'
    )


def get_pep_data(row, pep_index_url):
    columns = row.find_all('td')

    if len(columns) < 2:
        raise ParserDataException(
            'В строке таблицы PEP недостаточно колонок'
        )

    first_column_tag = columns[0]
    number_tag = columns[1]

    link_tag = number_tag.find('a')

    if link_tag is None:
        raise ParserDataException(
            'В строке таблицы PEP не найдена ссылка'
        )

    pep_number = link_tag.text.strip()

    if pep_number == '0':
        raise ParserDataException(
            'PEP 0 не должен учитываться'
        )

    preview_status = first_column_tag.text.strip()[1:]

    pep_url = urljoin(
        pep_index_url,
        link_tag['href']
    )

    return pep_url, preview_status


def pep(session):
    pep_index_url = urljoin(PEP_URL, 'numerical/')
    soup = get_soup(session, pep_index_url)

    table = find_tag(soup, 'table')
    rows = [
        row for row in table.find_all('tr')
        if row.find('td') is not None
    ]

    status_counter = Counter()
    errors = []
    status_mismatches = []

    for row in tqdm(rows):
        try:
            pep_url, preview_status = get_pep_data(
                row,
                pep_index_url
            )
        except ParserDataException as error:
            errors.append(str(error))
            continue

        try:
            status = get_pep_status(
                session,
                pep_url
            )
        except Exception as error:
            errors.append(str(error))
            continue

        expected_statuses = EXPECTED_STATUS.get(
            preview_status,
            ()
        )

        if status not in expected_statuses:
            status_mismatches.append(
                'Несовпадающие статусы:\n'
                f'{pep_url}\n'
                f'Статус в карточке: {status}\n'
                f'Ожидаемые статусы: {list(expected_statuses)}'
            )

        status_counter[status] += 1

    for message in status_mismatches:
        logging.info(message)

    if errors:
        logging.error(
            '\n'.join(errors)
        )

    results = [
        ('Статус', 'Количество'),
        *status_counter.items(),
        ('Total', sum(status_counter.values())),
    ]

    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    try:
        configure_logging()

        logging.info('Парсер запущен!')

        arg_parser = configure_argument_parser(
            MODE_TO_FUNCTION.keys()
        )
        args = arg_parser.parse_args()

        logging.info(
            f'Аргументы командной строки: {args}'
        )

        session = requests_cache.CachedSession()

        if args.clear_cache:
            session.cache.clear()

        parser_mode = args.mode

        results = MODE_TO_FUNCTION[parser_mode](
            session
        )

        if results is not None:
            control_output(results, args)

    except Exception:
        logging.exception(
            'В работе парсера возникла ошибка'
        )

    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
