from enum import Enum
from definitions import *


# Optimized AS_PATH verification algorithm using zero based array
# where the origin AS has index N - 1 and the latest AS in the AS_PATH
# has index 0.
# Doesn't check any hop twice.
def verifyASPathOptimizedZeroBased(
    aspa: ASPAObject, asPath: ASPath, direction: ASPADirection
) -> ASPAVerificationResult:
    def describe(i: int):
        return describeAS(aspa, asPath, N - i, N)

    def hop(i: int, j: int) -> Hop:
        return hopAndLog(aspa, asPath, N - i, N - j, N)

    N: int = len(asPath)

    if N == 0:
        raise ValueError("AS_PATH cannot have length zero")

    if N == 1:
        log("N = 1, trivially VALID AS_PATH.")
        return ASPAVerificationResult.VALID

    if N == 2 and direction == ASPADirection.DOWNSTREAM:
        log("N = 2, trivially VALID AS_PATH")
        return ASPAVerificationResult.VALID

    # =====================
    # FIND UP AND DOWN RAMP
    # =====================

    # Find up-ramp end
    R = N - 1
    while R > 0 and (lastHopRight := hop(R, R - 1)) == Hop.P:
        R -= 1

    log(f"UP-RAMP: ends at {describe(R)}.")
    log("............. UP done ............")

    if direction == ASPADirection.UPSTREAM and R == 0:
        log("UP-RAMP: complete customer-provider chain, VALID upstream AS_PATH.")
        return ASPAVerificationResult.VALID

    foundNPFromRight: bool = False
    foundNPFromLeft: bool = False

    L: int = 0
    if direction == ASPADirection.DOWNSTREAM:
        # Find down-ramp end
        while L < R and (lastHopLeft := hop(L, L + 1)) == Hop.P:
            L += 1

        assert L <= R
        log(f"DOWN-RAMP: ends at {describe(L)}.")
        log("............. DOWN done ............")

        # If gap does not exist (sharp tip) or is just a single hop wide,
        # there's no way to create a route leak, return VALID.
        # CAUTION: L is smaller than R, because the array is zero-based.
        if R - L <= 1:
            log(f"GAP: gap is {R - L} wide, that's a VALID AS_PATH.")
            return ASPAVerificationResult.VALID

    # ===========================
    # CHECK FOR OPPOSING nP+ HOPS
    # ===========================

    # I. FROM RIGHT
    # --------------
    # Check if there's a nP+ hop in the gap from the right (facing left).
    # a, The next hop right after the up-ramp was already retrieved from the database,
    #    so just check if that hop was nP+.
    # b, Also, don't check last hop before down-ramp starts
    #    because there must be a hop of space in order for two
    #    nP+ hops to oppose each other.
    # c, RR points to the left end of the hop last checked.
    # d, Checking stops if the hop is nP+.

    #        Last chance of finding a relevant nP+ hop
    #           /
    #   L      /\                  R
    #   * -- * -- * . . . . . * -- *
    #  /    L+1              R-1    \
    # *       |<------------------|  *
    # 0                             N-1
    RR: int = R
    if lastHopRight == Hop.nP:
        foundNPFromRight = True
        log(f"Found nP+ from right!")
    else:
        while RR > (L + 1 if direction == ASPADirection.DOWNSTREAM else 0):
            c = RR
            RR -= 1
            if hop(c, RR) == Hop.nP:
                log("Found nP+ from right!")
                foundNPFromRight = True
                break

    log(f"Stopped at {describe(RR)}")
    log("............. |<---- nP+ ? -----| done ............")

    # II. FROM LEFT
    # --------------
    # Check if there's a nP+ hop in the gap from the right (facing left).
    if direction == ASPADirection.DOWNSTREAM and foundNPFromRight:
        # a, There's no need to check for an nP+ from the left if we
        #    didn't find an nP+ from the right before.
        # b, The next hop right after the down-ramp was already retrieved from the database,
        #    so just check if that hop was nP+.
        # c, LL points to the right end of the hop last checked.
        # d, Checking stops if the hop is nP+.
        #
        #                    Last chance of finding a relevant nP+ hop
        #                       /
        #  L    LL             /\
        #   * -- * . . . . . * -- * . . . . .
        #  /    L+1               RR
        # *       |------------->|
        # 0
        LL: int = L + 1
        if lastHopLeft == Hop.nP:
            foundNPFromLeft = True
            log("Found nP+ from left!")
        else:
            while LL < RR:
                c = LL
                LL += 1
                if hop(c, LL) == Hop.nP:
                    log("Found nP+ from left!")
                    foundNPFromLeft = True
                    break

        log(f"Stopped at {describe(LL)}")
        log("............. |----- nP+ ? ---->| done ............")

    if direction == ASPADirection.DOWNSTREAM and foundNPFromLeft and foundNPFromRight:
        log("GAP: nP+ in opposing directions, INVALID AS_PATH.")
        return ASPAVerificationResult.INVALID

    elif direction == ASPADirection.UPSTREAM and foundNPFromRight:
        log("UP: nP+ in upstream customer-provider chain, INVALID AS_PATH.")
        return ASPAVerificationResult.INVALID

    return ASPAVerificationResult.UNKNOWN
