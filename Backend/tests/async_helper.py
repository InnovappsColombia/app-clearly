"""
CLEARLY — Test Async Runner Helper
Executes async coroutines without relying on Windows IOCP / socketpair loopback bindings.
"""

def run_sync(coro):
    """
    Drives a Python coroutine to completion synchronously.
    Handles nested coroutines via __await__ stack unwinding.
    """
    stack = [coro.__await__() if hasattr(coro, "__await__") else coro]
    val = None
    while stack:
        top = stack[-1]
        try:
            val = top.send(val)
            if hasattr(val, "__await__"):
                stack.append(val.__await__())
                val = None
            elif hasattr(val, "send"):
                stack.append(val)
                val = None
        except StopIteration as e:
            stack.pop()
            val = e.value
    return val

