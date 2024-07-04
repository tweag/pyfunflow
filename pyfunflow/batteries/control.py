from typing import Iterable
from pyfunflow.core import Flow


class SequenceFlow[O](Flow[O]):
    def __init__(self, flows: list[Flow], final_flow: Flow[O]) -> None:
        super().__init__(final_flow._output_type)
        self.flows = flows + [final_flow]

    def __getsubflows__(self) -> Iterable[Flow]:
        for flow in self.flows:
            yield from flow.__getsubflows__()
