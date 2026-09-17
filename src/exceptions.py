class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""


class ParserDataException(Exception):
    """Вызывается, когда парсер получает некорректные данные."""


class ParserStatusException(Exception):
    """Вызывается, когда парсер не может определить статус PEP."""
