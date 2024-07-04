from pyfunflow.core import Flow, RefBack


class LogFlow(Flow[None]):
    def __init__[O](self, message: str | RefBack[O, str]) -> None:
        super().__init__(type(None))
        self.message = message
