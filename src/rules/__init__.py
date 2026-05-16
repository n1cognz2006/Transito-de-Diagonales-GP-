from .speeding import SpeedingRule
from .no_stop import NoStopRule
from .wrong_way import WrongWayRule
from .harsh_brake import HarshBrakeRule
from .no_yield import NoYieldRule
from .tailgating import TailgatingRule
from .erratic import ErraticDrivingRule

ALL_RULES = [
    SpeedingRule,
    NoStopRule,
    WrongWayRule,
    HarshBrakeRule,
    NoYieldRule,
    TailgatingRule,
    ErraticDrivingRule,
]
