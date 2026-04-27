import asyncio

from src.task import Task


class EchoTaskHandler:
    """Класс обрабатывает echo-задачи."""

    def can_handle(self, task: Task) -> bool:
        """Проверяет, подходит ли задача обработчику.
        :param task: задача
        :return: True / False
        """
        kind = task.payload.get("kind")
        return kind == "echo"

    async def handle(self, task: Task) -> None:
        """Метод асинхронно выполняет echo-задачу.
        :param task: задача
        """
        return None


class SleepTaskHandler:
    """Класс обрабатывает sleep-задачи."""

    def can_handle(self, task: Task) -> bool:
        """Проверяет соответствие типа задачи.
        :param task: задача
        :return: True / False
        """
        kind = task.payload.get("kind")
        return kind == "sleep"

    async def handle(self, task: Task) -> None:
        """Асинхронно ждет установленное время.
        :param task: задача
        """
        seconds = float(task.payload.get("seconds", 0.01))
        await asyncio.sleep(seconds)


class FailingTaskHandler:
    """Класс обрабатывает fail-задачи."""

    def can_handle(self, task: Task) -> bool:
        """Проверяет соответствие типа задачи.
        :param task: задача
        :return: True / False
        """
        kind = task.payload.get("kind")
        return kind == "fail"

    async def handle(self, task: Task) -> None:
        """Завершает обработку ошибкой.
        :param task: задача
        :raises RuntimeError: тестовая ошибка обработчика
        """
        raise RuntimeError(f"Ошибка в обработчике задачи {task.id}")
