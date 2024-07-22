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
        final_flow=(b := B(a=a.output)),
    )

    dot_str = make_dot(flow)

    assert (
        dot_str
        == f"""digraph G {{
"{id(a)}" [label="A"]
"{id(b)}" [label="B"]
"{id(flow)}" [label="SequenceFlow"]
"{id(a)}" -> "{id(b)}" [label="a"]
"{id(a)}" -> "{id(b)}" [style=dashed]
"{id(b)}" -> "{id(flow)}" [style=dashed]
}}"""
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
        condition=(condition := Condition()),
        flow_false=(flow_left := Left()),
        flow_true=(flow_right := Right()),
    )

    dot_str = make_dot(flow)

    assert (
        dot_str
        == f"""digraph G {{
"{id(condition)}" [label="Condition"]
"{id(flow_right)}" [label="Right"]
"{id(flow_left)}" [label="Left"]
"{id(flow)}" [label="BranchFlow"]
"{id(condition)}" -> "{id(flow_right)}" [style=dashed]
"{id(flow_right)}" -> "{id(flow)}" [style=dashed]
"{id(condition)}" -> "{id(flow_left)}" [style=dashed]
"{id(flow_left)}" -> "{id(flow)}" [style=dashed]
}}"""
    )
