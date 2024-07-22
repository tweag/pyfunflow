from pyfunflow.batteries.control import BranchFlow, SequenceFlow
from pyfunflow.batteries.diagram import make_dot
from pyfunflow.core import Flow, RefBack


class Constant(Flow[int]):
    def __init__(self, value: int):
        super().__init__(_output_type=int)
        self.value = value


class IsEven(Flow[bool]):
    def __init__(self, value: int | RefBack[int, int]):
        super().__init__(_output_type=bool)
        self.value = value


class Increment(Flow[int]):
    def __init__(self, value: int | RefBack[int, int]):
        super().__init__(_output_type=int)
        self.value = value


class Double(Flow[int]):
    def __init__(self, value: int | RefBack[int, int]):
        super().__init__(_output_type=int)
        self.value = value


flow = SequenceFlow(
    flows=[
        (constant := Constant(1)),
        (
            branching := BranchFlow(
                condition=IsEven(constant.output),
                flow_false=Increment(constant.output),
                flow_true=SequenceFlow(
                    flows=[
                        (double := Double(constant.output)),
                    ],
                    final_flow=Increment(double.output),
                ),
            )
        ),
    ],
    final_flow=Increment(branching.output),
)

dot_str = make_dot(flow)
print(dot_str)
