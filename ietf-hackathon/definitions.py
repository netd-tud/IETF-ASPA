from enum import Enum
from typing import List, Dict, TypeAlias
import config

ASPAObject: TypeAlias = Dict[int, List[int]]
ASPath: TypeAlias = List[int]


def log(msg: str):
    if config.enableDebugLogging:
        print(msg)


def inclusiveRange(start, stop):
    return range(start, stop + 1)


def inclusiveRangeInverse(start, stop):
    return range(start, stop - 1, -1)


# Returns AS index in AS_PATH and ASN
def describeAS(aspa: ASPAObject, asPath: ASPath, i: int, N: int):
    if i == 0:
        return "0"
    elif i > N:
        return f"N+{i - N}"
    return f"#{i}:{asPath[N - i]}"


class ASPAVerificationResult(Enum):
    UNKNOWN = 0
    INVALID = 1
    VALID = 2


class ASPADirection(Enum):
    UPSTREAM = 0
    DOWNSTREAM = 1


class Hop(Enum):
    # No Attestation
    nA = "nA"

    # Not Provider+
    nP = "nP+"

    # Provider+
    P = "P+"


# 5. Hop Check Function
def _hop(aspa: ASPAObject, asPath: ASPath, i: int, j: int, N: int):
    if not (i >= 1 and i <= N and j >= 1 and j <= N):
        raise ValueError(f"Invalid AS_PATH ASN position: i={i} j={j}, must between 1 and N={N}")
    if asPath[N - i] not in aspa:
        return Hop.nA
    if asPath[N - j] in aspa[asPath[N - i]]:
        return Hop.P
    else:
        return Hop.nP


# Prints and returns AS index in AS_PATH and ASN
def hopAndLog(aspa: ASPAObject, asPath: ASPath, i: int, j: int, N: int) -> Hop:
    res = _hop(aspa, asPath, i, j, N)
    log(f"Hop {describeAS(aspa, asPath, i, N)} C->P {describeAS(aspa, asPath, j, N)} is {res.value}")
    return res
