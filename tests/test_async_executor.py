import unittest

from src.async_executor import AsyncTaskExe, ExecutorResource
from src.handlers import EchoTaskHandler, FailingTaskHandler, SleepTaskHandler
from src.task import Task
from src.task_queue import TaskQueue


class AsyncExecutorTests(unittest.IsolatedAsyncioTestCase):

    async def test_context_manager(self) -> None:
        """Вход и выход async контекстного менеджера."""
        resource = ExecutorResource()
        async with resource as opened_resource:
            self.assertIs(opened_resource, resource)

    async def test_run_ok_and_fail(self) -> None:
        """Успешная обработка и обработка исключений."""
        queue = TaskQueue(
            [
                Task(id="A-1", description="echo", payload={"kind": "echo", "message": "ok"}),
                Task(id="A-2", description="sleep", payload={"kind": "sleep", "seconds": 0.001}),
                Task(id="A-3", description="fail", payload={"kind": "fail"}),
            ]
        )
        executor = AsyncTaskExe()
        echo_handler = EchoTaskHandler()

        executor.add_handler(echo_handler)
        executor.add_handler(SleepTaskHandler())
        executor.add_handler(FailingTaskHandler())
        await executor.enqueue_from_task_queue(queue)
        await executor.run()

        self.assertTrue(any("Задача A-1 завершена успешно" in line for line in executor.logs))
        self.assertEqual(queue[0].status, "done")
        self.assertEqual(queue[1].status, "done")
        self.assertEqual(queue[2].status, "failed")
        self.assertTrue(any("Ошибка выполнения задачи A-3" in err for err in executor.errors))

    async def test_no_handler(self) -> None:
        """Подходящий обработчик отсутствует."""
        queue = TaskQueue(
            [
                Task(id="A-4", description="неизвестный гусь", payload={"kind": "неизвестный гусь"}),
            ]
        )
        executor = AsyncTaskExe()
        await executor.enqueue_from_task_queue(queue)
        await executor.run()

        self.assertEqual(queue[0].status, "failed")
        self.assertTrue(any("Не найден обработчик" in err for err in executor.errors))

    async def test_handler_contract(self) -> None:
        """Runtime-валидации контракта обработчика."""
        executor = AsyncTaskExe()

        class BadHandler:
            def can_handle(self, task):
                return True

        with self.assertRaises(TypeError):
            executor.add_handler(BadHandler())

if __name__ == "__main__":
    unittest.main()
