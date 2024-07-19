from typing import Any, Callable, cast
from pyfunflow.batteries import run_sequential_local
from pyfunflow.batteries.control import (
    BranchFlow,
    SequenceFlow,
    interpret_branch_flow,
    interpret_sequence_flow,
)
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


def test_run_local_branch():
    """
    Test that we can run a BranchFlow locally.
    """

    # given
    class AddFlow(Flow[int]):
        def __init__(self, x: int | RefBack[int, int], y: int) -> None:
            self.x = x
            self.y = y
            super().__init__(int)

    class IsEvenFlow(Flow[bool]):
        def __init__(self, x: int | RefBack[int, int]) -> None:
            self.x = x
            super().__init__(bool)

    flow12 = SequenceFlow(
        flows=[
            (
                previous := SequenceFlow(
                    flows=[],
                    final_flow=AddFlow(2, 0),
                )
            )
        ],
        final_flow=BranchFlow(
            condition=IsEvenFlow(previous.output),
            flow_true=AddFlow(previous.output, 10),
            flow_false=AddFlow(previous.output, 100),
        ),
    )

    flow101 = SequenceFlow(
        flows=[
            (
                previous := SequenceFlow(
                    flows=[],
                    final_flow=AddFlow(1, 0),
                )
            )
        ],
        final_flow=BranchFlow(
            condition=IsEvenFlow(previous.output),
            flow_true=AddFlow(previous.output, 10),
            flow_false=AddFlow(previous.output, 100),
        ),
    )

    def interpret_add(result_store: ResultStore, flow: AddFlow):
        x = flow.x if isinstance(flow.x, int) else result_store.get(flow.x.back)
        return x + flow.y

    def interpret_is_even(result_store: ResultStore, flow: IsEvenFlow):
        if isinstance(flow.x, int):
            return flow.x % 2 == 0
        else:
            return flow.x.map_(result_store.get(flow.x.back)) % 2 == 0

    def dispatcher[F](flow: F) -> Callable[[ResultStore, F], Any]:
        if isinstance(flow, AddFlow):
            return cast(Callable[[ResultStore, F], Any], interpret_add)
        elif isinstance(flow, IsEvenFlow):
            return cast(Callable[[ResultStore, F], Any], interpret_is_even)
        elif isinstance(flow, SequenceFlow):
            return cast(Callable[[ResultStore, F], Any], interpret_sequence_flow)
        elif isinstance(flow, BranchFlow):
            return cast(Callable[[ResultStore, F], Any], interpret_branch_flow)
        else:
            raise ValueError(f"Unknown flow type: {flow}")

    # when
    result12 = run_sequential_local(flow12, dispatcher)

    # then
    EXPECTED12 = 12
    assert result12 == EXPECTED12

    # when
    result101 = run_sequential_local(flow101, dispatcher)

    # then
    EXPECTED101 = 101
    assert result101 == EXPECTED101
