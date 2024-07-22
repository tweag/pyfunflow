from pyfunflow.batteries.control import SequenceFlow
from pyfunflow.batteries.diagram import make_dot


def test_make_dot():
    from pyfunflow.core import Flow, RefBack

    class A(Flow[None]):
        def __init__(self):
            super().__init__(_output_type=type(None))
            pass

    class B(Flow[None]):
        def __init__(self, a: RefBack):
            super().__init__(_output_type=type(None))
            self.a = a

    flow = SequenceFlow(
        flows=[
            (a := A()),
        ],
        final_flow=B(a=a.output),
    )

    dot_str = make_dot(flow)

    assert (
        dot_str
        == """digraph G {
"A"
"B"
"SequenceFlow"
"A" -> "B" [label="a"]
"A" -> "B" [style=dashed]
"B" -> "SequenceFlow" [style=dashed]
}"""
    )
