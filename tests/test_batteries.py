from pyfunflow.batteries import run_sequential_local
from pyfunflow.core import Flow


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

    def dispatcher(flow):
        assert isinstance(flow, AddOneFlow)

        def add_one(result_store, flow):
            if isinstance(flow.x, int):
                return flow.x + 1
            else:
                return flow.x.map_(result_store.get(flow.x.back)) + 1

        return add_one

    # when
    result = run_sequential_local(flow, dispatcher)

    # then
    EXPECTED = 2
    assert result == EXPECTED
