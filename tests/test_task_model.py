import unittest
from datetime import datetime

from src.task import Task
from src.descriptors import TaskValidatError


class TaskModelTests(unittest.TestCase):
    """
    Набор тестов для проверки модели Task.
    :return: None
    """

    def test_task_min_data(self) -> None:
        """
        Проверяет создание задачи и значения по умолчанию.
        :return: None
        """

        task = Task(id=1, description="test")
        self.assertEqual(task.id, 1)
        self.assertEqual(task.description, "test")
        self.assertEqual(task.priority, 5)
        self.assertEqual(task.status, "new")
        self.assertTrue(isinstance(task.created_at, datetime))

    def test_invalid_priority_error(self) -> None:
        """
        Проверяет, что приоритет вне диапазона вызывает исключение.
        :return: None
        """

        with self.assertRaises(TaskValidatError):
            Task(id=1, description="test", priority=100)

    def test_status_flow(self) -> None:
        """
        Проверяет нормальный переход статусов
        :return: None
        """

        task = Task(id="x", description="flow", priority=3)
        self.assertTrue(task.is_ready)

        task.start()
        self.assertEqual(task.status, "progress")

        task.finish(success=False)
        self.assertEqual(task.status, "failed")

    def test_creat_read(self) -> None:
        """
        Проверяет поведение non-data дескриптора created_at.
        :return: None
        """

        task = Task(id=1, description="test")
        original = task.created_at
        overwritten = datetime.now()

        task.created_at = overwritten
        self.assertEqual(task.created_at, overwritten)
        self.assertNotEqual(task.created_at, original)

    def test_invalid_id_type(self) -> None:
        """
        Проверяет, что id неподходящего типа вызывает исключение.
        :return: None
        """

        with self.assertRaises(TaskValidatError):
            Task(id=3.14, description="haram id") #type: ignore

    def test_empty_descript(self) -> None:
        """
        Проверяет, что пустое описание вызывает исключение.
        :return: None
        """

        with self.assertRaises(TaskValidatError):
            Task(id=1, description=" ")

    def test_priority(self) -> None:
        """
        Проверяет, что priority < 1 вызывает исключение.
        :return: None
        """

        with self.assertRaises(TaskValidatError):
            Task(id=1, description="prio", priority=0)


    def test_depends_status(self) -> None:
        """
        Проверяет, что is_ready зависит от статуса задачи.
        :return: None
        """

        task = Task(id=1, description="test", priority=5)
        self.assertTrue(task.is_ready)

        task.start()
        self.assertFalse(task.is_ready)

    def test_start_wrong_status(self) -> None:
        """
        Проверяет, что start() из DONE запрещён.
        :return: None
        """

        task = Task(id=1, description="test")
        task.finish(success=True)
        with self.assertRaises(TaskValidatError):
            task.start()

    def test_finish_wrong_status(self) -> None:
        """
        Проверяет, что finish() нельзя вызвать повторно из DONE.
        :return: None
        """

        task = Task(id=1, description="test")
        task.finish(success=True)
        with self.assertRaises(TaskValidatError):
            task.finish()


if __name__ == "__main__":
    unittest.main()
