from typing import Any, Callable, Protocol, Iterable


class RefBack[U, V]:
    def __init__(self, back: "Flow[U]", map_: Callable[[U], V]) -> None:
        self.back = back
        self.map_ = map_

    def map[T](self, f: Callable[[V], T]) -> "RefBack[U, T]":
        return RefBack(back=self.back, map_=lambda x: f(self.map_(x)))


class Flow[O]:
    def __init__(self, _output_type: type[O]) -> None:
        self._output_type = _output_type

    @property
    def output(self) -> RefBack[O, O]:
        return RefBack(self, map_=lambda x: x)

    def __getsubflows__(self) -> Iterable["Flow"]:
        # by default, iterating over a flow returns itself
        yield self


class ResultStore:
    def __init__(self) -> None:
        self.results = {}

    def set[O](self, flow: Flow[O], result: O) -> None:
        self.results[flow] = result

    def get[O](self, flow: Flow[O]) -> O:
        return self.results[flow]


class Dispatcher(Protocol):
    def __call__[F](self, flow: F) -> Callable[[ResultStore, F], Any]: ...
