import asyncio
import uuid
from contextlib import _AsyncGeneratorContextManager

from db import Status, TaskModel, connection_maker
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection


async def fetch_task(
        worker_id: uuid.UUID,
        conn_manager: _AsyncGeneratorContextManager[AsyncConnection],
) -> TaskModel | None:
    async with conn_manager as conn:
        select_query = await conn.execute(
            text(
                """
                    UPDATE tasks
                    SET
                        status = :new_status,
                        worker_id = :worker_id
                    WHERE id = (
                            SELECT id
                            FROM tasks
                            WHERE status = :old_status
                            FOR UPDATE SKIP LOCKED
                            LIMIT 1
                    )
                    RETURNING *
                """,
            ),
            {
                "new_status": Status.PROCESSING,
                "worker_id": worker_id,
                "old_status": Status.PENDING,
            },
        )

        query_row = select_query.fetchone()
        if not query_row:
            return None

        return TaskModel(
            **query_row._asdict(),
        )


async def confirm_comleted_task(
        task_id: uuid.UUID,
        conn_manager: _AsyncGeneratorContextManager[AsyncConnection],
) -> None:
    async with conn_manager as conn:
        await conn.execute(
            text(
                """
                    UPDATE tasks
                    SET
                        status = :status
                    WHERE id = :task_id
                """,
            ),
            {
                "status": Status.COMPLETED,
                "task_id": task_id,
            },
        )


async def working_process(worker_id: uuid.UUID) -> None:
    task = await fetch_task(worker_id, connection_maker())

    if not task:
        return

    await asyncio.sleep(5)   #working
    print(f"TASK {task.id} DONE")
    await confirm_comleted_task(task.id, connection_maker())


async def main() -> None:
    tasks = set()
    while True:
        tasks.add(asyncio.create_task(working_process(uuid.uuid4())))
        if len(tasks) >= 5:
            done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            tasks -= set(done)



asyncio.run(main())

# async def make_tasks():
#     async with connection_maker() as conn:
#         for i in range(1000):
#             await conn.execute(
#                 text(
#                 """
#                     INSERT INTO tasks (id, task_name, status, worker_id)
#                     VALUES (:id, :task_name, :status, :worker_id)
#                 """,
#                 ),
#                 {
#                     "id": uuid.uuid4(),
#                     "task_name": f"Task_{i}",
#                     "status": Status.PENDING.value,
#                     "worker_id": None,
#                 },
#             )











