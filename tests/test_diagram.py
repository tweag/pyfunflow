from pyfunflow.batteries.control import SequenceFlow, BranchFlow
from pyfunflow.batteries.diagram import make_dot
from pyfunflow.core import Flow, RefBack


def test_make_dot():
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


def test_make_dot_condition():
    class Condition(Flow[bool]):
        def __init__(self):
            super().__init__(_output_type=bool)

    class Left(Flow[None]):
        def __init__(self):
            super().__init__(_output_type=type(None))

    class Right(Flow[None]):
        def __init__(self):
            super().__init__(_output_type=type(None))

    flow = BranchFlow(
        condition=Condition(),
        flow_false=Left(),
        flow_true=Right(),
    )

    dot_str = make_dot(flow)

    assert (
        dot_str
        == """digraph G {
"Condition"
"Right"
"Left"
"BranchFlow"
"Condition" -> "Right" [style=dashed]
"Condition" -> "Left" [style=dashed]
"Right" -> "BranchFlow" [style=dashed]
"Left" -> "BranchFlow" [style=dashed]
}"""
    )
