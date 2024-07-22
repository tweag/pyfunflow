import inspect
from io import StringIO
from pyfunflow.batteries.control import BranchFlow, SequenceFlow
from pyfunflow.core import Flow, RefBack
from dataclasses import dataclass


@dataclass
class Edge:
    downstream: str
    upstream: str
    type_: str
    label: str | None


def _make_edges(flow: Flow):
    nodes: list[str] = []
    edges: list[Edge] = []

    for subflow in flow.__getsubflows__():
        subflow_init = inspect.signature(subflow.__init__)

        nodes.append(subflow.__class__.__name__)

        # link SequenceFlow flows
        if isinstance(subflow, SequenceFlow):
            # link each last subsubflow the the next first
            previous_last_subsubflow = None
            for sequence_subflow in subflow.flows:
                first_subsubflow = next(iter(sequence_subflow.__getsubflows__()))
                if previous_last_subsubflow is not None:
                    edges.append(
                        Edge(
                            downstream=previous_last_subsubflow.__class__.__name__,
                            upstream=first_subsubflow.__class__.__name__,
                            type_="sequence",
                            label=None,
                        )
                    )
                previous_last_subsubflow = list(sequence_subflow.__getsubflows__())[-1]

            edges.append(
                Edge(
                    downstream=subflow.flows[-1].__class__.__name__,
                    upstream=subflow.__class__.__name__,
                    type_="sequence",
                    label=None,
                )
            )

        # link BranchFlow flows
        if isinstance(subflow, BranchFlow):
            edges.append(
                Edge(
                    downstream=subflow.condition.__class__.__name__,
                    upstream=subflow.flow_true.__class__.__name__,
                    type_="branching",
                    label=None,
                )
            )
            edges.append(
                Edge(
                    downstream=subflow.condition.__class__.__name__,
                    upstream=subflow.flow_false.__class__.__name__,
                    type_="branching",
                    label=None,
                )
            )
            edges.append(
                Edge(
                    downstream=subflow.flow_true.__class__.__name__,
                    upstream=subflow.__class__.__name__,
                    type_="branching",
                    label=None,
                )
            )
            edges.append(
                Edge(
                    downstream=subflow.flow_false.__class__.__name__,
                    upstream=subflow.__class__.__name__,
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
                        downstream=upstream.__class__.__name__,
                        upstream=subflow.__class__.__name__,
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
        builder.write(f'"{node}"\n')

    for edge in edges:
        label = f' [label="{edge.label}"]' if edge.label else None
        style = " [style=dashed]" if edge.type_ in ["sequence", "branching"] else None
        builder.write(
            f'"{edge.downstream}" -> "{edge.upstream}"{style or ""}{label or ""}\n'
        )
    builder.write("}")

    return builder.getvalue()
