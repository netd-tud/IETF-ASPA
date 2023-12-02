# Experimental ASPA AS_PATH VALIDATION ALGORITHM

from enum import Enum
from typing import List, Dict
from definitions import *


def verifyASPathSimplified(aspa: ASPAObject, asPath: ASPath, direction: ASPADirection) -> ASPAVerificationResult:
    N = len(asPath)

    if N == 0:
        raise ValueError("AS_PATH cannot have length zero")

    def hop(i: int, j: int) -> Hop:
        if (N + 1, N) == (i, j):
            return Hop.P if direction == ASPADirection.DOWNSTREAM else Hop.nA
        elif (N, N + 1) == (i, j):
            return Hop.P if direction == ASPADirection.UPSTREAM else Hop.nA

        if asPath[N - i] not in aspa:
            return Hop.nA
        if asPath[N - j] in aspa[asPath[N - i]]:
            return Hop.P
        else:
            return Hop.nP

    R: int = 1
    while R < N + 1 and hop(R, R + 1) == Hop.P:
        R += 1

    L: int = N + 1
    while L > R and hop(L, L - 1) == Hop.P:
        L -= 1

    if L - R <= 1:
        return ASPAVerificationResult.VALID

    foundNPFromRight: bool = False
    RR: int = R
    while RR < L - 1 and not foundNPFromRight:
        RR += 1
        foundNPFromRight = hop(RR - 1, RR) == Hop.nP

    foundNPFromLeft: bool = False
    LL: int = L
    while LL > RR and not foundNPFromLeft:
        LL -= 1
        foundNPFromLeft = hop(LL + 1, LL) == Hop.nP

    if foundNPFromRight and (foundNPFromLeft or direction == ASPADirection.UPSTREAM):
        return ASPAVerificationResult.INVALID

    return ASPAVerificationResult.UNKNOWN
