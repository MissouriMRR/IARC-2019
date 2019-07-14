from .box import Box
from .net_testing import NetTesting
from .systems_check import systems_check

ROUTINES = {
    "box": Box,
    "systems_check": systems_check,
    "net_testing": NetTesting
}
