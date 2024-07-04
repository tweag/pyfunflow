from typing import Iterable
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
