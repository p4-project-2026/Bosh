from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable, Optional


@dataclass
class LogCase:
    path: Optional[str] = None
    data: dict[str, Any] = field(default_factory=dict)

    def set(self, path: str, **data: Any) -> None:
        self.path = path
        self.data = data


def logged(start: Callable[..., str], success: dict[str, Callable[..., str]]):
    def decorator(fn):
        @wraps(fn)
        def wrapper(self, *args, **kwargs):
            log_case = LogCase()

            vvvprint(f"{self.__class__.__name__}: {start(self, *args, **kwargs)}")

            try:
                result = fn(self, *args, log_case=log_case, **kwargs)
            except Exception as e:
                vvvprint(f"{self.__class__.__name__}: Failed: {e}")
                raise

            if log_case.path is not None:
                message_builder = success.get(log_case.path)

                if message_builder is None:
                    raise Exception(
                        f"No success log message for path '{log_case.path}'"
                    )

                vvvprint(
                    f"{self.__class__.__name__}: "
                    f"{message_builder(self, *args, **kwargs, **log_case.data)}"
                )

            return result

        return wrapper

    return decorator