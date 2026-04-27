from datetime import datetime

from src.descriptors import (
    DescriptionField,
    IdField,
    PriorityField,
    PayloadField,
    RdCreatTime,
    ValidatField,
    TaskValidatError,
)


class StatusField(ValidatField):
    """
    Статус задачи. Разрешены только значения известных строк.
    """

    def _validate(self, value: object) -> None:
        allowed = {"new", "progress", "done", "failed"}
        if value not in allowed:
            raise TaskValidatError("Недопустимый статус задачи")


class Task:
    """
    Модель задачи.

    Основана на Task из лабораторной 1: хранит id и payload + дополнительные поля для описания, статуса, приоритета и времени создания.
    """

    id = IdField()
    description = DescriptionField()
    priority = PriorityField()
    status = StatusField()
    created_at = RdCreatTime()
    payload = PayloadField(required=False)

    def __init__(self, id: int | str, description: str, priority = 5, status = "new", created_at = None,payload = None ) -> None:
        """
        Создаёт новую задачу.

        :param id: идентификатор задачи
        :param description: текст описания задачи
        :param priority: приоритет от 1 до 10
        :param status: статус задачи
        :param created_at: время создания
        :param payload: произвольные пользовательские данные
        :return: None
        """

        self._created_at = created_at or datetime.now()
        self.id = id
        self.description = description
        self.priority = priority
        self.status = status
        self.payload = payload or {}

    @property
    def is_ready(self) -> bool:
        """
        Вычисляемое свойство.
        :return: True, если задача готова к выполнению
        """

        return self.status == "new" and self.priority > 0 #type: ignore

    @property
    def short_description(self) -> str:
        """
        Короткое текстовое представление задачи.
        :return: строка с коротким описанием
        """

        return f"[{self.id}] {self.description} (priority={self.priority}, status={self.status})"

    def start(self) -> None:
        """
        Переводит задачу в статус progress.
        :return: None
        """

        if self.status not in ("new", "failed"):
            raise TaskValidatError(
                "Перевести в progress можно только новую или неудавшуюся задачу",
            )
        self.status = "progress"

    def finish(self, success: bool = True) -> None:
        """
        Завершает задачу с успешным или неуспешным результатом.
        :param success: True для DONE, False для FAILED
        :return: None
        """

        if self.status not in ("new", "progress"):
            raise TaskValidatError("Завершить можно только активную задачу")
        self.status = "done" if success else "failed"

    def to_dict(self) -> dict[str, object]:
        """
        Представление задачи.
        :return: словарь с полями задачи
        """

        return {
            "id": self.id,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at.isoformat(), #type: ignore
            "payload": self.payload,
        }

    def __repr__(self) -> str:
        return f"Task({self.short_description})"
