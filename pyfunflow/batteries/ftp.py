from typing import BinaryIO, TypedDict

from pyfunflow.core import Flow, RefBack


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
