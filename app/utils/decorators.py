"""
Decorators for MIC2E API
"""

import logging
import traceback
from functools import wraps
from typing import Callable

from fastapi import HTTPException

logger = logging.getLogger(__name__)


def handle_exceptions(func: Callable) -> Callable:
    """
    Decorator to automatically handle exceptions and raise HTTPException.

    Args:
        func: The function to wrap

    Returns:
        Wrapped function that handles exceptions
    """

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            # Re-raise HTTPExceptions as they are already properly formatted
            raise
        except ValueError as e:
            # Handle validation errors with 400 status
            logger.warning(f"Validation error in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except PermissionError as e:
            # Handle permission errors with 403 status
            logger.warning(f"Permission error in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=403, detail=str(e))
        except FileNotFoundError as e:
            # Handle file not found errors with 404 status
            logger.warning(f"File not found in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            # Handle all other exceptions with 500 status
            logger.error(f"Unhandled exception in {func.__name__}: {str(e)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            error_detail = str(e)
            raise HTTPException(status_code=500, detail=error_detail)

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTTPException:
            # Re-raise HTTPExceptions as they are already properly formatted
            raise
        except ValueError as e:
            # Handle validation errors with 400 status
            logger.warning(f"Validation error in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except PermissionError as e:
            # Handle permission errors with 403 status
            logger.warning(f"Permission error in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=403, detail=str(e))
        except FileNotFoundError as e:
            # Handle file not found errors with 404 status
            logger.warning(f"File not found in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            # Handle all other exceptions with 500 status
            logger.error(f"Unhandled exception in {func.__name__}: {str(e)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            error_detail = str(e)
            raise HTTPException(status_code=500, detail=error_detail)

    # Return appropriate wrapper based on whether the function is async
    if (
        func.__name__.startswith("async_")
        or hasattr(func, "__code__")
        and func.__code__.co_flags & 0x80
    ):
        return async_wrapper
    else:
        return sync_wrapper


def handle_exceptions_with_status(status_code: int = 500):
    """
    Decorator to handle exceptions with a specific HTTP status code.

    Args:
        status_code: HTTP status code to return for exceptions

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                # Re-raise HTTPExceptions as they are already properly formatted
                raise
            except Exception as e:
                logger.error(f"Exception in {func.__name__}: {str(e)}")
                logger.error(f"Traceback:\n{traceback.format_exc()}")
                raise HTTPException(status_code=status_code, detail=str(e))

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except HTTPException:
                # Re-raise HTTPExceptions as they are already properly formatted
                raise
            except Exception as e:
                logger.error(f"Exception in {func.__name__}: {str(e)}")
                logger.error(f"Traceback:\n{traceback.format_exc()}")
                raise HTTPException(status_code=status_code, detail=str(e))

        # Return appropriate wrapper based on whether the function is async
        if (
            func.__name__.startswith("async_")
            or hasattr(func, "__code__")
            and func.__code__.co_flags & 0x80
        ):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def validate_required_params(*required_params: str):
    """
    Decorator to validate that required parameters are present in the request.

    Args:
        *required_params: Names of required parameters

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Check if any required parameters are missing
            missing_params = []
            for param in required_params:
                if param not in kwargs or kwargs[param] is None:
                    missing_params.append(param)

            if missing_params:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required parameters: {', '.join(missing_params)}",
                )

            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Check if any required parameters are missing
            missing_params = []
            for param in required_params:
                if param not in kwargs or kwargs[param] is None:
                    missing_params.append(param)

            if missing_params:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required parameters: {', '.join(missing_params)}",
                )

            return func(*args, **kwargs)

        # Return appropriate wrapper based on whether the function is async
        if (
            func.__name__.startswith("async_")
            or hasattr(func, "__code__")
            and func.__code__.co_flags & 0x80
        ):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
