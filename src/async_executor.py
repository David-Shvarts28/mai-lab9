import asyncio
from typing import Protocol, runtime_checkable

from src.task import Task
from src.task_queue import TaskQueue


@runtime_checkable
class TaskHandler(Protocol):

    def can_handle(self, task: Task) -> bool:
        """Подходит ли обработчик для данной задачи."""
        ...

    async def handle(self, task: Task) -> None:
        """Асинхронно выполнить обработку задачи."""
        ...


class ExecutorResource:

    async def __aenter__(self) -> object:
        """Открывает ресурс перед выполнением задач."""
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        """Закрывает ресурс после выполнения задач."""
        return False


class AsyncTaskExe:

    def __init__(self) -> None:
        self._queue = asyncio.Queue()
        self._handlers = []
        self._logs = []
        self._errors = []

    def add_handler(self, handler: object) -> None:
        """Регистрирует обработчик после проверки контракта TaskHandler.
        :param handler: объект реализующий протокол TaskHandler
        :raises TypeError: если handler не поддерживает нужный контракт
        """
        if not isinstance(handler, TaskHandler):
            raise TypeError("Обработчик должен реализовывать протокол TaskHandler")
        self._handlers.append(handler)

    async def enqueue_from_task_queue(self, queue: TaskQueue) -> None:
        """Переносит задачи из очереди TaskQueue в асинхронную очередь.
        :param queue: очередь задач
        """
        k = 0
        for task in queue:
            await self._queue.put(task)
            k += 1
        self._logs.append(f"Загружено задач: {k}")

    async def run(self) -> None:
        """Запускает последовательную асинхронную обработку задач."""
        async with ExecutorResource():
            while not self._queue.empty():
                task = await self._queue.get()
                await self._execute_task(task)
                self._queue.task_done()

    async def _execute_task(self, task: Task) -> None:
        """Ищет подходящий обработчик и запускает его.
        :param task: задача
        """
        try:
            task.start()
            handler = self._pick_handler(task)
            if handler is None:
                task.finish(success=False)
                self._errors.append(f"Для задачи {task.id} не найден обработчик")
                return
            await handler.handle(task)
            task.finish(success=True)
            self._logs.append(f"Задача {task.id} завершена успешно")
        except Exception as error:
            task.finish(success=False)
            self._errors.append(f"Ошибка выполнения задачи {task.id}: {error}")

    def _pick_handler(self, task: Task) -> TaskHandler | None:
        """Подбирает первый обработчик, который умеет взять задачу.
        :param task: задача
        :return: обработчик или None
        """
        for handler in self._handlers:
            if handler.can_handle(task):
                return handler
        return None

    def get_logs(self) -> list[str]:
        """Вернуть список логов"""
        return self._logs.copy()

    def get_errors(self) -> list[str]:
        """Вернуть список ошибок"""
        return self._errors.copy()

    @property
    def logs(self) -> list[str]:
        """Логи"""
        return self._logs.copy()

    @property
    def errors(self) -> list[str]:
        """Ошибки"""
        return self._errors.copy()