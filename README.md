# pyfunflow

Declarative workflows in Python.

> [!WARNING]
> This is a Proof of Concept, currently Work In Progress.


## What are declarative workflows?

In most workflow libraries, you write your program as a sequence of implementations.
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

Using `pyfunflow`, you _declare_ a workflow:

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

In this example, getting the FTP password in Airflow is both declared _and_ implemented by `get_ftp_password` at once.
In order to pull the FTP password from somewhere else (e.g. a secret manager), we would need to change the workflow entirely,
even though what we really care about in this workflow is the idea of fetching a secret not how.
Airflow hard-codes the meaning of a task together with how to actually perform the task, leading to high coupling.
This makes workflows harder to run in different environment, e.g. locally for testing.

In `pyfunflow`, only the intent of the workflow is conveyed.
The workflow can read the secret from an environment variable, a file or a secret manager, we don't care about it. 
It will be up to the running environment to decide that!

In `pyfunflow`, flows that compose a workflow are all "just data", without behavior attached (yet).

## Usage

Requirements:
- Python 3.12+

Install `pyfunflow`

```sh
# TODO: push to PyPI
pip install pyfunflow
```

Instantiate a `Flow` from the pre-defined ones:

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
