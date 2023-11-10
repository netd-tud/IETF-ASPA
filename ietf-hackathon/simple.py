# Experimental ASPA AS_PATH VALIDATION ALGORITHM

from enum import Enum
from typing import List, Dict
from structs import Hop, ASPAVerificationResult, ASPADirection


def new_algorithm(aspa: Dict[int, List[int]], as_path: List[int], direction: ASPADirection) -> ASPAVerificationResult:
    if len(as_path) == 0:
        return ASPAVerificationResult.INVALID

    # note that as_path is ordered in the sense that -1 is the receiving as and N - 1 is the origin as

    N: int = len(as_path)

    def hop(i: int, j: int) -> Hop:
        if direction == ASPADirection.DOWNSTREAM and (-1, 0) == (i, j):
            return Hop.P
        if direction == ASPADirection.UPSTREAM and (0, -1) == (i, j):
            return Hop.P

        if as_path[i] not in aspa:
            return Hop.nA
        if as_path[j] in aspa[as_path[i]]:
            return Hop.P
        else:
            return Hop.nP

    R: int = N - 1
    while R >= -1 and hop(R, R - 1) == Hop.P:
        R -= 1

    L: int = -1
    while L < N and hop(L, L + 1) == Hop.P:
        L += 1

    if R - L <= 1:
        return ASPAVerificationResult.VALID

    found_valley_left: bool = False
    found_valley_right: bool = False

    I: int = L

    while I < R and not (found_valley_left := (hop(I, I + 1) == Hop.nP)):
        I += 1

    J: int = R
    while J >= L and not (found_valley_right := (hop(J, J - 1) == Hop.nP)):
        J -= 1

    if found_valley_right and (found_valley_left or direction == ASPADirection.UPSTREAM):
        return ASPAVerificationResult.INVALID

    return ASPAVerificationResult.UNKNOWN
