"""
gaia/utils/processing.py
Throttled multiprocessing helpers for GAIA Supercomputer.
Leaves 2 CPU cores free so your Mac stays responsive.
"""
import os
from concurrent.futures import ProcessPoolExecutor

# Always leave 2 cores free for the operating system and other apps
MAX_WORKERS = max(1, os.cpu_count() - 2)


def run_parallel(func, tasks: list) -> list:
    """
    Run a list of tasks in parallel using the throttled worker pool.

    Args:
        func:  A picklable function to call for each task.
        tasks: A list of arguments to pass to func (one per task).

    Returns:
        List of results in the same order as tasks.
    """
    if not tasks:
        return []

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(func, tasks))

    return results
