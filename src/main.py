import asyncio

from src.async_executor import AsyncTaskExe
from src.handlers import EchoTaskHandler, FailingTaskHandler, SleepTaskHandler
from src.task import Task
from src.task_queue import TaskQueue


def main() -> None:
    """Точка входа в приложение."""
    async def run() -> None:
        queue = TaskQueue(
            [
                Task(id="T-1", description="гусь echo-задача", priority=8, status="new", payload={"kind": "echo", "message": "hello"}),
                Task(id="T-2", description="гусь спит-задача", priority=5, status="new", payload={"kind": "sleep", "seconds": 0.01}),
                Task(id="T-3", description="гусиная неверная задача", priority=6, status="new", payload={"kind": "fail"}),
            ]
        )

        executor = AsyncTaskExe()
        executor.add_handler(EchoTaskHandler())
        executor.add_handler(SleepTaskHandler())
        executor.add_handler(FailingTaskHandler())

        await executor.enqueue_from_task_queue(queue)
        await executor.run()

    asyncio.run(run())


if __name__ == "__main__":
    main()
