from enum import Enum


class ASPADirection(Enum):
    UPSTREAM = 0
    DOWNSTREAM = 1


class Hop(Enum):
    nA = "nA"
    nP = "nP+"
    P = "P+"


class ASPAVerificationResult(Enum):
    UNKNOWN = 0
    INVALID = 1
    VALID = 2


def inclusiveRange(start, stop):
    return range(start, stop + 1)


def inclusiveRangeInverse(start, stop):
    return range(start, stop - 1, -1)
