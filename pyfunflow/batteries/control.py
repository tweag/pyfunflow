from typing import Iterable, Union, cast
from pyfunflow.core import Flow, ResultStore


class SequenceFlow[O](Flow[O]):
    def __init__(self, flows: list[Flow], final_flow: Flow[O]) -> None:
        super().__init__(final_flow._output_type)
        self.flows = flows + [final_flow]

    def __getsubflows__(self) -> Iterable[Flow]:
        for flow in self.flows:
            yield from flow.__getsubflows__()
        yield self


def interpret_sequence_flow(result_store: ResultStore, flow: SequenceFlow):
    return result_store.get(flow.flows[-1])


class BranchFlow[O1, O2](Flow[O1 | O2]):
    def __init__(
        self,
        condition: Flow[bool],
        flow_true: Flow[O1],
        flow_false: Flow[O2],
    ) -> None:
        super().__init__(
            cast(
                type[O1 | O2],
                Union[flow_true._output_type, flow_false._output_type],
            ),
        )
        self.condition = condition
        self.flow_true = flow_true
        self.flow_false = flow_false

    def __getsubflows__(self) -> Iterable[Flow]:
        yield from self.condition.__getsubflows__()
        yield from self.flow_true.__getsubflows__()
        yield from self.flow_false.__getsubflows__()
        yield self


def interpret_branch_flow[O1, O2](
    result_store: ResultStore,
    flow: BranchFlow[O1, O2],
) -> O1 | O2:
    if result_store.get(flow.condition):
        return result_store.get(flow.flow_true)
    else:
        return result_store.get(flow.flow_false)
