import inspect
from io import StringIO
from pyfunflow.core import Flow, RefBack


def _make_edges(flow: Flow):
    edges: list[tuple[str, str]] = []
    for subflow in flow.__getsubflows__():
        subflow_init = inspect.signature(subflow.__init__)
        for init_param in subflow_init.parameters.keys():
            try:
                param = getattr(subflow, init_param)
            except:
                continue

            if isinstance(param, RefBack):
                upstream = param.back
                edges.append((upstream.__class__.__name__, subflow.__class__.__name__))

    return edges


def make_dot(flow: Flow) -> str:
    edges = _make_edges(flow)

    builder: StringIO = StringIO()

    builder.write("digraph G {\n")
    for upstream, downstream in edges:
        builder.write(f'"{upstream}" -> "{downstream}"\n')
    builder.write("}")

    return builder.getvalue()
