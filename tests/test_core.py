from pyfunflow.core import Flow, RefBack


def test_instantiate():
    class DummyFlow(Flow[int]):
        def __init__(self, x: int) -> None:
            self.x = x
            super().__init__(int)

    flow = DummyFlow(1)
    output = flow.output.map(lambda x: x + 1)
    assert isinstance(output, RefBack)
    assert output.back is flow
