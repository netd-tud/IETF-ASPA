# Experimental ASPA AS_PATH VALIDATION ALGORITHM

from enum import Enum
from typing import List, Dict
from definitions import *


def verifyASPathSimplified2(aspa: ASPAObject, asPath: ASPath, direction: ASPADirection) -> ASPAVerificationResult:
    N = len(asPath)
        
    if N == 0:
        raise ValueError("AS_PATH cannot have length zero")

    def hop(i: int, j: int) -> Hop:
        return hopAndLog(aspa, asPath, i, j, N)

    # up-ramp detection
    U: int = 1
    while U < N and hop(U, U + 1) == Hop.P:
        U += 1
            
    # down-ramp detection
    D: int = N
    if direction == ASPADirection.DOWNSTREAM:
        while D > U and hop(D, D - 1) == Hop.P:
            D -= 1
            
    if U == N and direction == ASPADirection.UPSTREAM or D - U <= 1 and direction == ASPADirection.DOWNSTREAM:
        return ASPAVerificationResult.VALID
    
    foundNPFromRight: bool = False
    UU: int = U
    while UU < (D-1 if direction == ASPADirection.DOWNSTREAM else N) and not foundNPFromRight:
        foundNPFromRight = hop(UU, UU + 1) == Hop.nP
        UU += 1
            
    foundNPFromLeft: bool = False
    if direction == ASPADirection.DOWNSTREAM:
        DD: int = D
        while DD > UU and not foundNPFromLeft:
            foundNPFromLeft = hop(DD, DD - 1) == Hop.nP
            DD -= 1
                    
    if foundNPFromRight and (foundNPFromLeft or direction == ASPADirection.UPSTREAM):
        return ASPAVerificationResult.INVALID

    return ASPAVerificationResult.UNKNOWN
