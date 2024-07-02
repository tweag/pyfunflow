from typing import Any, Callable, cast
from pyfunflow import LogFlow, ResultStore, run_sequential_local


flow = LogFlow(message="Hello, world!")


def interpret_log_flow(
    result_store: ResultStore,
    flow: LogFlow,
) -> None:
    message: str
    if isinstance(flow.message, str):
        message = flow.message
    else:
        message = flow.message.map_(result_store.get(flow.message.back))

    print(message)
    return None


def dispatcher[F](flow: F) -> Callable[[ResultStore, F], Any]:
    if isinstance(flow, LogFlow):
        return cast(Callable[[ResultStore, F], Any], interpret_log_flow)
    else:
        raise ValueError("No interpreter for flow: " + str(flow))


run_sequential_local(flow=flow, dispatcher=dispatcher)
