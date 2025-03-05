"""Create Command.

Function for creating a command from a dictionary of user inputs.
"""

import typing


def format_command_env_vars(
    cmd_kwargs: typing.Dict[str, typing.Union[bool, str, float, int]],
) -> list[str]:
    """Create a list of strings representing environment variables to a command from a dictionary of kwarg key:value pairs.

    Parameters
    ----------
    cmd_kwargs : typing.Dict[str, typing.Union[bool, str, float, int]]
        The variables to pass to the command, in a dictionary

    Returns
    -------
    cmd_list : list[str]
        A list of strings representing a command

    """
    cmd_list = []
    for kwarg, val in cmd_kwargs.items():
        kwarg = kwarg.strip("-")
        if len(kwarg) == 1:
            if isinstance(val, bool) and val:
                cmd_list += [f"-{kwarg}"]
            else:
                cmd_list += [f"-{kwarg}", str(val)]
        else:
            kwarg = kwarg.replace("_", "-")
            if isinstance(val, bool) and val:
                cmd_list += [f"--{kwarg}"]
            else:
                # This is ridiculous, but for some reason for the specific option '--n-threads', MOOSE will only accept formatting
                # like '--n-threads=4', and does not recognise '--n-threads 4'. According to the docstring of the command line tool,
                # all other arguments work correctly with the '--a b' formatting, just not that one!
                # Could change them all to be formatted as '--a=b', but then mpiexec doesn't recognise any arguments provided in that form >:(
                if kwarg == "n-threads":
                    cmd_list += [f"--{kwarg}={val}"]
                else:
                    cmd_list += [f"--{kwarg}", str(val)]

    return cmd_list
