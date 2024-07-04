from typing import TypedDict

from pyfunflow.core import Flow, RefBack


class SecretFlowOutput(TypedDict):
    value: str


class SecretFlow(Flow[SecretFlowOutput]):
    def __init__[O](
        self,
        name: str | RefBack[O, str],
    ) -> None:
        super().__init__(SecretFlowOutput)
        self.name = name
