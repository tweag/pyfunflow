from pyfunflow.core import Dispatcher, Flow, ResultStore


def run_sequential_local[O](
    flow: Flow[O],
    dispatcher: Dispatcher,
) -> O:
    result_store = ResultStore()
    # run flow in order
    for subflow in flow.__getsubflows__():
        interpreter = dispatcher(subflow)
        subflow_result = interpreter(result_store, subflow)
        result_store.set(subflow, subflow_result)

    final_flow = subflow
    final_result = result_store.get(final_flow)
    return final_result
