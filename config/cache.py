from typing import Any, Callable, Dict, Optional, Tuple
from fastapi_cache import FastAPICache
from starlette.requests import Request
from starlette.responses import Response


def custom_repo_key_builder(
    func: Callable,
    namespace: str = "",
    *,
    request: Optional[Request] = None,
    response: Optional[Response] = None,
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
):
    key_parts = [namespace, func.__name__] + [str(p) for p in args[1:]]
    return ":".join(key_parts)


async def invalidate_get_contacts_repo_cache(user_id: int):
    await FastAPICache.clear(namespace=f"get_contacts_repo:get_contacts:{user_id}:*")