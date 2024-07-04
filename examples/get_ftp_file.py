from typing import Any, Callable, cast
from io import BytesIO
from pyfunflow import (
    FtpFlowOutput,
    SecretFlow,
    FtpFlow,
    SecretFlowOutput,
    SequenceFlow,
    ResultStore,
    run_sequential_local,
)
from pyfunflow.batteries.control import interpret_sequence_flow


flow = SequenceFlow(
    flows=[
        (get_ftp_password := SecretFlow(name="ftp-password")),
    ],
    final_flow=FtpFlow(
        host="ftp.example.com",
        user="user",
        password=get_ftp_password.output.map(lambda x: x["value"]),
        path="/path/to/remote/file",
    ),
)


def interpret_secret_flow(
    result_store: ResultStore,
    flow: SecretFlow,
) -> SecretFlowOutput:
    secret_name: str
    if isinstance(flow.name, str):
        secret_name = flow.name
    else:
        secret_name = flow.name.map_(result_store.get(flow.name.back))

    if secret_name != "ftp-password":
        raise ValueError("No such secret: " + secret_name)

    return {"value": "some_password"}


def interpret_ftp_flow(
    result_store: ResultStore,
    flow: FtpFlow,
) -> FtpFlowOutput:
    host: str
    if isinstance(flow.host, str):
        host = flow.host
    else:
        host = flow.host.map_(result_store.get(flow.host.back))

    user: str
    if isinstance(flow.user, str):
        user = flow.user
    else:
        user = flow.user.map_(result_store.get(flow.user.back))

    password: str
    if isinstance(flow.password, str):
        password = flow.password
    else:
        password = flow.password.map_(result_store.get(flow.password.back))

    path: str
    if isinstance(flow.path, str):
        path = flow.path
    else:
        path = flow.path.map_(result_store.get(flow.path.back))

    if password != "some_password":
        raise ValueError("Incorrect password")

    print(f"Downloading {path} from {user}@{host}...")

    content = BytesIO(b"Hello world")
    return {"content": content}


def dispatcher[F](flow: F) -> Callable[[ResultStore, F], Any]:
    if isinstance(flow, SecretFlow):
        return cast(Callable[[ResultStore, F], Any], interpret_secret_flow)
    elif isinstance(flow, FtpFlow):
        return cast(Callable[[ResultStore, F], Any], interpret_ftp_flow)
    if isinstance(flow, SequenceFlow):
        return cast(Callable[[ResultStore, F], Any], interpret_sequence_flow)
    else:
        raise ValueError("No interpreter for flow: " + str(flow))


result = run_sequential_local(
    flow=flow,
    dispatcher=dispatcher,
)

print(result["content"].read().decode())
