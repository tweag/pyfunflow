from typing import BinaryIO, TypedDict, Iterable

from pyfunflow.core import Dispatcher, Flow, RefBack, ResultStore


class SecretFlowOutput(TypedDict):
    value: str


class SecretFlow(Flow[SecretFlowOutput]):
    def __init__[O](
        self,
        name: str | RefBack[O, str],
    ) -> None:
        super().__init__(SecretFlowOutput)
        self.name = name


class FtpFlowOutput(TypedDict):
    content: BinaryIO


class FtpFlow(Flow[FtpFlowOutput]):
    def __init__[O1, O2, O3, O4](
        self,
        host: str | RefBack[O1, str],
        user: str | RefBack[O2, str],
        password: str | RefBack[O3, str],
        path: str | RefBack[O4, str],
    ) -> None:
        super().__init__(FtpFlowOutput)
        self.host = host
        self.user = user
        self.password = password
        self.path = path


class LogFlow(Flow[None]):
    def __init__[O](self, message: str | RefBack[O, str]) -> None:
        super().__init__(type(None))
        self.message = message


class SequenceFlow[O](Flow[O]):
    def __init__(self, flows: list[Flow], final_flow: Flow[O]) -> None:
        super().__init__(final_flow._output_type)
        self.flows = flows + [final_flow]

    def __getsubflows__(self) -> Iterable[Flow]:
        for flow in self.flows:
            yield from flow.__getsubflows__()


def run_sequential_local[O](
    flow: Flow[O],
    dispatcher: Dispatcher,
) -> O:
    result_store = ResultStore()
    # run flow in order
    for subflow in flow.__getsubflows__():
        interpreter = dispatcher(subflow)
        subflow_result = interpreter(result_store, subflow)
        result_store.set(subflow, subflow_result)

    final_flow = subflow
    final_result = result_store.get(final_flow)
    return final_result
