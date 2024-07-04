# pyfunflow

Declarative composable typed workflows in Python.

> [!WARNING]
> This is a proof of concept currently being worked on.
> Do not use in production.

> [!WARNING]
> Please consider this a research project.
> Its development may stop anytime without announcement or warning.

## Why `pyfunflow`?

### Declarative

In most workflow libraries, one writes their workflow as a sequence of _implementations_.
For example in Airflow:

```python
# Airflow code
with DAG(
    'ftp_download_dag',
    description='Pull a secret then download a file via FTP',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:
    @task
    def get_ftp_password():
        return os.getenv('FTP_PASSWORD')

    @task
    def download_file_from_ftp(ftp_password):
        ftp_hook = FTPHook(host="ftp.example.com", user="user", password=ftp_password)
        ftp_hook.retrieve_file('/path/to/remote/file', '/path/to/local/file')

    # Define dependencies
    ftp_password = get_ftp_password()
    download_file_from_ftp(ftp_password)
```

In the Airflow example above, getting the FTP password is both declared _and_ implemented by `get_ftp_password` at once.
In order to pull the FTP password from somewhere else (e.g. a secret manager), we would need to change the workflow entirely,
even though what we really care about in this workflow is the idea of fetching a secret not how.
Airflow hard-codes the meaning of a task together with how to actually perform the task, leading to high coupling.
This makes workflows harder to run in different environment, e.g. locally for testing.

Using `pyfunflow`, you _declare_ a workflow regardless of its implementation:

```python
# pyfunflow code
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
```

In `pyfunflow`, flows that compose a workflow are all "just data", without behavior attached (yet).
Only the intent of the workflow is conveyed, not how that intent is fulfilled.
When it runs, the workflow can read the secret from an environment variable, a file or a secret manager, we don't care about it (yet). 
It will be up to the running environment to decide how each flow!

### Composable

In `pyfunflow` both tasks and workflows are "flows".
It is possible to define two workflows separately, and put them together afterwards to make a more complex workflow.

### Typed

Both inputs and output a flow are typed, providing helpful editor features such as auto-completion, and validating the structure of your workflow.

```python
flow = SequenceFlow(
    flows=[
        (get_ftp_password := SecretFlow(name="ftp-password")),
    ],
    final_flow=FtpFlow(
        host="ftp.example.com",
        user="user",
        # the transformed output of the previous flow is type-checked
        password=get_ftp_password.output.map(lambda x: x["value"]),
        path="/path/to/remote/file",
    ),
)
```

## Usage

Requirements:
- Python 3.12+

Install `pyfunflow`.

```sh
pip install git+https://github.com/tweag/pyfunflow
```

Instantiate a `Flow` from the pre-defined ones.

```python
# from ./examples/hello_world.py
from pyfunflow import LogFlow


flow = LogFlow(message="Hello, world!")
```

See [`examples/hello_world.py`](./examples/hello_world.py) for a complete example that runs the flow.

You can also define your own types of `Flow`s and combine them together!

## Development

Requirements:
- Python 3.12+
- `poetry`

Clone this repository.
Then install Python dependencies.

```sh
poetry install
```

Tools used for this project:
- formatting with `ruff`
- linting with `ruff`
- type checking with `pyright`
- testing with `pytest`

## Credits

This work was heavily inspired by [`tweag/funflow`](https://github.com/tweag/funflow).
