from datetime import datetime


class TaskValidatError(Exception):
    """Исключение для ошибок валидации полей задачи."""


class BaseDescriptor:
    """Базовый дескриптор, который запоминает имя атрибута."""

    def __set_name__(self, owner: type, name: str) -> None:
        """
        Запоминает имя атрибута и внутреннее имя хранения.
        :param owner: класс-владелец
        :param name: публичное имя атрибута
        :return: None
        """

        self._public_name = name
        self._private_name = "_" + name


class ValidatField(BaseDescriptor):
    """Data-дескриптор с простой валидацией значений."""

    def __init__(self, *, required: bool = True) -> None:
        """
        Создаёт дескриптор поля.
        :param required: булево значение
        :return: None
        """

        self._required = required

    def __get__(self, instance: object, owner: type | None = None) -> object:
        """
        Возвращает значение поля из экземпляра.
        :param instance: экземпляр, из которого читаем значение
        :param owner: класс-владелец
        :return: значение поля или дескриптор
        """

        if instance is None:
            return self
        return getattr(instance, self._private_name)

    def __set__(self, instance: object, value: object) -> None:
        """
        Устанавливает значение поля в экземпляр с валидацией.
        :param instance: экземпляр, в который записываем значение
        :param value: новое значение поля
        :return: None
        """

        if self._required and value is None:
            raise TaskValidatError(f"Поле {self._public_name} не может быть None")
        self._validate(value)
        setattr(instance, self._private_name, value)

    def _validate(self, value: object) -> None:
        """
        Базовый метод валидации.
        :param value: проверяемое значение
        :return: None
        """
        pass


class IdField(ValidatField):
    """Идентификатор задачи."""

    def _validate(self, value: object) -> None:
        if not isinstance(value, (int, str)):
            raise TaskValidatError("id задачи должен быть int или str")


class DescriptionField(ValidatField):
    """Описание задачи."""

    def _validate(self, value: object) -> None:
        if not isinstance(value, str):
            raise TaskValidatError("description задачи должен быть строкой")
        if not value.strip():
            raise TaskValidatError("description задачи не может быть пустым")


class PriorityField(ValidatField):
    """Приоритет задачи. Целое от 1 до 10."""

    def _validate(self, value: object) -> None:
        if not isinstance(value, int):
            raise TaskValidatError("priority должен быть целым числом")
        if value < 1 or value > 10:
            raise TaskValidatError("priority должен быть в диапазоне от 1 до 10")


class PayloadField(ValidatField):
    """Поле payload. Ожидается словарь."""

    def _validate(self, value: object) -> None:
        if not isinstance(value, dict):
            raise TaskValidatError("payload должен быть словарём")


class RdCreatTime(BaseDescriptor):
    """Non-data дескриптор. Значение хранится в атрибуте _created_at."""

    def __get__(self, instance: object, owner: type | None = None) -> datetime | BaseDescriptor:
        """
        Возвращает время создания задачи.
        :param instance: экземпляр, из которого читаем значение
        :param owner: класс-владелец
        :return: datetime времени создания или дескриптор
        """

        if instance is None:
            return self
        return getattr(instance, self._private_name)
