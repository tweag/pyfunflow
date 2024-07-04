from typing import Any, Callable, cast
from pyfunflow.batteries import run_sequential_local
from pyfunflow.batteries.control import SequenceFlow, interpret_sequence_flow
from pyfunflow.core import Flow, RefBack, ResultStore


def test_run_local_sequential():
    """
    Test that we can run a simple flow locally and sequentially.
    """

    # given
    class AddOneFlow(Flow[int]):
        def __init__(self, x: int) -> None:
            self.x = x
            super().__init__(int)

    flow = AddOneFlow(1)

    def interpret_add_one(result_store, flow):
        if isinstance(flow.x, int):
            return flow.x + 1
        else:
            return flow.x.map_(result_store.get(flow.x.back)) + 1

    def dispatcher(flow):
        assert isinstance(flow, AddOneFlow)
        return interpret_add_one

    # when
    result = run_sequential_local(flow, dispatcher)

    # then
    EXPECTED = 2
    assert result == EXPECTED


def test_run_local_sequential_sequence_output():
    """
    Test that the output of a SequenceFlow is correct.
    """

    # given
    class AddOneFlow(Flow[int]):
        def __init__(self, x: int | RefBack[int, int]) -> None:
            self.x = x
            super().__init__(int)

    flow = SequenceFlow(
        flows=[
            (
                previous := SequenceFlow(
                    flows=[],
                    final_flow=AddOneFlow(1),
                )
            )
        ],
        final_flow=AddOneFlow(x=previous.output),
    )

    def interpret_add_one(result_store: ResultStore, flow: AddOneFlow):
        if isinstance(flow.x, int):
            return flow.x + 1
        else:
            return flow.x.map_(result_store.get(flow.x.back)) + 1

    def dispatcher[F](flow: F) -> Callable[[ResultStore, F], Any]:
        if isinstance(flow, AddOneFlow):
            return cast(Callable[[ResultStore, F], Any], interpret_add_one)
        elif isinstance(flow, SequenceFlow):
            return cast(Callable[[ResultStore, F], Any], interpret_sequence_flow)
        else:
            raise ValueError(f"Unknown flow type: {flow}")

    # when
    result = run_sequential_local(flow, dispatcher)

    # then
    EXPECTED = 3
    assert result == EXPECTED
