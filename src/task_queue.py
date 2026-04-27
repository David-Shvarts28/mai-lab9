from src.task import Task


class TaskQueueIterator:

    def __init__(self, tasks) -> None:
        """
        Создает итератор по коллекции задач.
        :param tasks: итерируемая коллекция объектов Task
        :return: None
        """
        self._tasks = tasks
        self._index = 0

    def __iter__(self):
        """
        Возвращает сам итератор.
        """
        return self

    def __next__(self) -> Task:
        """
        Возвращает следующую задачу очереди.
        """
        if self._index >= len(self._tasks):
            raise StopIteration
        cur = self._tasks[self._index]
        self._index += 1
        return cur


class TaskQueue:
    """Коллекция задач."""

    def __init__(self, tasks = None) -> None:
        """
        Создает новую очередь задач.
        :param tasks: начальная коллекция объектов Task (опционально)
        :return: None
        """
        if tasks is not None:
            self._tasks = list(tasks)
        else:
            self._tasks = []

    def add_task(self, task: Task) -> None:
        """
        Добавляет одну задачу в очередь.
        :param task: экземпляр Task
        :return: None
        """
        self._tasks.append(task)

    def extend(self, tasks) -> None:
        """
        Добавляет несколько задач в очередь.
        :param tasks: коллекция объектов Task
        :return: None
        """
        self._tasks.extend(tasks)

    def __iter__(self):
        """
        Возвращает новый итератор для повторного обхода.
        """
        return TaskQueueIterator(self._tasks)

    def __len__(self) -> int:
        """
        Возвращает размер очереди.
        """
        return len(self._tasks)

    def __getitem__(self, index: int)  -> Task:
        """
        Возвращает задачу по индексу.
        :param index: номер (позиция) задачи в очереди
        """
        return self._tasks[index]

    def filter_by_status(self, status: str):
        """
        Лениво фильтрует задачи по статусу.
        :param status: статус для отбора
        """
        for item in self._tasks:
            if item.status == status:
                yield item

    def filter_by_min_priority(self, min_priority: int):
        """
        Лениво фильтрует задачи по минимальному приоритету.
        :param min_priority: нижняя граница приоритета (включая ее)
        """
        for it in self._tasks:
            if it.priority >= min_priority:
                yield it

    def ready_tasks_stream(self):
        """
        Лениво возвращает только готовые задачи.
        :return: Generator[Task, None, None]
        """
        for task in self._tasks:
            if task.is_ready:
                yield task
