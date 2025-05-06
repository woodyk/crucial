# File: dispatcher.py
# Description: Dynamically resolve and execute tool functions based on schema/tool name
# Author: Ms. White
# Created: 2025-05-06
# Modified: 2025-05-06 13:14:05

import importlib
import os

TOOLS_PACKAGE = "crucial.tools"

def dispatch(action_name, params):
    """
    Given an action name (e.g. 'canvas_draw_line') and a dictionary of parameters,
    dynamically import the corresponding module from tools/ and invoke the function.
    
    Returns the result of the tool function.
    """
    try:
        module_name = f"{TOOLS_PACKAGE}.{action_name}"
        mod = importlib.import_module(module_name)
        func = getattr(mod, action_name)
        return func(**params)
    except ModuleNotFoundError:
        raise Exception(f"Tool module '{module_name}' not found.")
    except AttributeError:
        raise Exception(f"Function '{action_name}' not defined in '{module_name}'.")
    except Exception as e:
        raise Exception(f"Error dispatching '{action_name}': {e}")
