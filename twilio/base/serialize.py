import datetime
import json
from typing import Union, Dict, Any, Optional, List

from twilio.base import values


def iso8601_date(d: Union[datetime.datetime, datetime.date, str, "values.Values"]) -> Union[str, "values.Values", None]:
    """
    Return a string representation of a date that the Twilio API understands
    Format is YYYY-MM-DD. Returns None if d is not a string, datetime, or date
    """
    if d == values.unset:
        return d
    elif isinstance(d, datetime.datetime):
        return str(d.date())
    elif isinstance(d, datetime.date):
        return str(d)
    elif isinstance(d, str):
        return d
    return None


def iso8601_datetime(d: Union[datetime.datetime, datetime.date, str, "values.Values"]) -> Union[str, "values.Values", None]:
    """
    Return a string representation of a date that the Twilio API understands
    Format is YYYY-MM-DD. Returns None if d is not a string, datetime, or date
    """
    if d == values.unset:
        return d
    elif isinstance(d, datetime.datetime) or isinstance(d, datetime.date):
        return d.strftime("%Y-%m-%dT%H:%M:%SZ")
    elif isinstance(d, str):
        return d
    return None


def prefixed_collapsible_map(m: Union[Dict[str, Any], "values.Values"], prefix: str) -> Dict[str, Any]:
    """
    Return a dict of params corresponding to those in m with the added prefix
    """
    if m == values.unset:
        return {}

    def flatten_dict(d: Dict[str, Any], result: Optional[Dict[str, Any]] = None, prv_keys: Optional[List[str]] = None) -> Dict[str, Any]:
        if result is None:
            result = {}

        if prv_keys is None:
            prv_keys = []

        for k, v in d.items():
            if isinstance(v, dict):
                flatten_dict(v, result, prv_keys + [k])
            else:
                result[".".join(prv_keys + [k])] = v

        return result

    if isinstance(m, dict):
        flattened = flatten_dict(m)
        return {"{}.{}".format(prefix, k): v for k, v in flattened.items()}

    return {}


def boolean_to_string(bool_or_str: Union[bool, str, "values.Values", None]) -> Union[str, "values.Values", None]:
    if bool_or_str == values.unset:
        return bool_or_str

    if bool_or_str is None:
        return bool_or_str

    if isinstance(bool_or_str, str):
        return bool_or_str.lower()

    return "true" if bool_or_str else "false"


def object(obj: Any) -> Union[str, Any]:
    """
    Return a jsonified string represenation of obj if obj is jsonifiable else
    return obj untouched
    """
    if isinstance(obj, dict) or isinstance(obj, list):
        return json.dumps(obj)
    return obj


def map(lst: Any, serialize_func: Any) -> Any:
    """
    Applies serialize_func to every element in lst
    """
    if not isinstance(lst, list):
        return lst
    return [serialize_func(item) for item in lst]
    return [serialize_func(e) for e in lst]
