import unittest

from src.descriptors import RdCreatTime, TaskValidatError, ValidatField
from src.task import Task
from src.task_queue import TaskQueue

def build_queue() -> TaskQueue:
    tasks = [
        Task(id="1", description="гусь1", priority=3, status="new"),
        Task(id="2", description="гусь2", priority=8, status="progress"),
        Task(id="3", description="гусь3", priority=9, status="new"),
        Task(id="4", description="гусь4", priority=1, status="failed"),
    ]
    return TaskQueue(tasks)


class TestTaskQueue(unittest.TestCase):

    def test_iter(self) -> None:
        q = build_queue()
        ids = [task.id for task in q]
        self.assertEqual(ids, ["1", "2", "3", "4"])

    def test_iter_dop(self) -> None:
        queue_data = build_queue()
        first = [task.id for task in queue_data]
        second = [task.id for task in queue_data]
        self.assertEqual(first, second)

    def test_len_get(self) -> None:
        q = build_queue()
        self.assertEqual(len(q), 4)
        self.assertEqual(q[1].id, "2")

    def test_filter_status(self) -> None:
        q = build_queue()
        res = q.filter_by_status("new")
        self.assertIs(iter(res), res)
        self.assertTrue(hasattr(res, "__next__"))
        self.assertEqual([task.id for task in res], ["1", "3"])

    def test_filter_priority(self) -> None:
        q = build_queue()
        filtered_tasks_result = q.filter_by_min_priority(8)
        self.assertEqual([task.id for task in filtered_tasks_result], ["2", "3"])

    def test_ready_tasks_stream(self) -> None:
        q = build_queue()
        ids = [task.id for task in q.ready_tasks_stream()]
        self.assertEqual(ids, ["1", "3"])

    def test_add_extend(self) -> None:
        q = TaskQueue()
        q.add_task(Task(id="11", description="goose", priority=2, status="new"))
        q.extend(
            [
                Task(id="12", description="goose1", priority=4, status="new"),
                Task(id="13", description="goose2", priority=7, status="done"),
            ]
        )
        self.assertEqual(len(q), 3)
        self.assertEqual([task.id for task in q], ["11", "12", "13"])

    def test_bad_id(self) -> None:
        with self.assertRaises(TaskValidatError):
            Task(id=None, description="ok", priority=5, status="new")  # type: ignore

    def test_bad_priority(self) -> None:
        with self.assertRaises(TaskValidatError):
            Task(id="5", description="ok", priority=11, status="new")

    def test_bad_status(self) -> None:
        with self.assertRaises(TaskValidatError):
            Task(id="5", description="ok", priority=5, status="unknown")

    def test_start(self) -> None:
        task = Task(id="10", description="feed-goose", priority=5, status="new")
        task.start()
        self.assertEqual(task.status, "progress")

    def test_repr(self) -> None:
        t = Task(id="14", description="repr test", priority=4, status="new")
        self.assertIn("Task(", repr(t))

    def test_start_invalid(self) -> None:
        task = Task(id="21", description="work", priority=5, status="done")
        with self.assertRaises(TaskValidatError):
            task.start()

    def test_to_dict(self) -> None:
        task = Task(id="23", description="payload", priority=6, status="new")
        data = task.to_dict()
        self.assertEqual(data["id"], "23")
        self.assertIn("created_at", data)

    def test_finish_failed(self) -> None:
        task = Task(id="24", description="payload", priority=6, status="progress")
        task.finish(success=False)
        self.assertEqual(task.status, "failed")


    def test_desc_class(self) -> None:
        self.assertIsInstance(Task.created_at, RdCreatTime)
        self.assertTrue(hasattr(Task, "id"))
        self.assertIsNone(ValidatField(required=False)._validate("any"))   #type: ignore



if __name__ == "__main__":
    unittest.main()
