import inspect
from io import StringIO
from pyfunflow.batteries.control import BranchFlow, SequenceFlow
from pyfunflow.core import Flow, RefBack
from dataclasses import dataclass


@dataclass
class Node:
    id_: str
    label: str


@dataclass
class Edge:
    downstream: str
    upstream: str
    type_: str
    label: str | None


def _get_first_last_subflows(flow: Flow):
    subflows = list(flow.__getsubflows__())
    return subflows[0], subflows[-1]


def _make_edges(flow: Flow):
    nodes: list[Node] = []
    edges: list[Edge] = []

    for subflow in flow.__getsubflows__():
        subflow_init = inspect.signature(subflow.__init__)

        nodes.append(Node(id_=str(id(subflow)), label=subflow.__class__.__name__))

        # link SequenceFlow flows
        if isinstance(subflow, SequenceFlow):
            # link each last subsubflow the the next first
            previous_last_subsubflow = None
            for sequence_subflow in subflow.flows:
                first_subsubflow = next(iter(sequence_subflow.__getsubflows__()))
                if previous_last_subsubflow is not None:
                    edges.append(
                        Edge(
                            downstream=str(id(previous_last_subsubflow)),
                            upstream=str(id(first_subsubflow)),
                            type_="sequence",
                            label=None,
                        )
                    )
                previous_last_subsubflow = list(sequence_subflow.__getsubflows__())[-1]

            edges.append(
                Edge(
                    downstream=str(id(subflow.flows[-1])),
                    upstream=str(id(subflow)),
                    type_="sequence",
                    label=None,
                )
            )

        # link BranchFlow flows
        if isinstance(subflow, BranchFlow):
            flow_true_first, flow_true_last = _get_first_last_subflows(
                subflow.flow_true
            )
            edges.append(
                Edge(
                    downstream=str(id(subflow.condition)),
                    upstream=str(id(flow_true_first)),
                    type_="branching",
                    label=None,
                )
            )
            edges.append(
                Edge(
                    downstream=str(id(flow_true_last)),
                    upstream=str(id(subflow)),
                    type_="branching",
                    label=None,
                )
            )
            flow_false_first, flow_false_last = _get_first_last_subflows(
                subflow.flow_false
            )
            edges.append(
                Edge(
                    downstream=str(id(subflow.condition)),
                    upstream=str(id(flow_false_first)),
                    type_="branching",
                    label=None,
                )
            )
            edges.append(
                Edge(
                    downstream=str(id(flow_false_last)),
                    upstream=str(id(subflow)),
                    type_="branching",
                    label=None,
                )
            )

        # link by inputs passed
        for init_param in subflow_init.parameters.keys():
            try:
                param = getattr(subflow, init_param)
            except:
                continue

            if isinstance(param, RefBack):
                upstream = param.back
                edges.append(
                    Edge(
                        downstream=str(id(upstream)),
                        upstream=str(id(subflow)),
                        type_="inputs",
                        label=init_param,
                    )
                )

    return nodes, edges


def make_dot(flow: Flow) -> str:
    nodes, edges = _make_edges(flow)

    builder: StringIO = StringIO()

    builder.write("digraph G {\n")
    for node in nodes:
        builder.write(f'"{node.id_}" [label="{node.label}"]\n')

    for edge in edges:
        label = f' [label="{edge.label}"]' if edge.label else None
        style = " [style=dashed]" if edge.type_ in ["sequence", "branching"] else None
        builder.write(
            f'"{edge.downstream}" -> "{edge.upstream}"{style or ""}{label or ""}\n'
        )
    builder.write("}")

    return builder.getvalue()
