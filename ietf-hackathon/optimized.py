from enum import Enum
from structs import ASPADirection, ASPAVerificationResult, Hop
from simple import new_algorithm


#  Simplified AS_PATH verification algorithm
def optimized_algorithm(aspa, asPath, direction) -> ASPAVerificationResult:
    fromProvider: bool = direction == ASPADirection.DOWNSTREAM

    def hop(i, j):
        if not (i >= 1 and i <= N and j >= 1 and j <= N):
            raise ValueError(f"Invalid AS_PATH ASN position: i={i} j={j}, must between 1 and N={N}")
        if asPath[N - i] not in aspa:
            return Hop.nA
        if asPath[N - j] in aspa[asPath[N - i]]:
            return Hop.P
        else:
            return Hop.nP

    # print("Applying new algo...")
    N = len(asPath)

    if N == 0:
        raise ValueError("AS_PATH cannot have length zero")

    if N == 1:
        # print("N = 1, trivially VALID AS_PATH.")
        return ASPAVerificationResult.VALID

    if N == 2 and fromProvider:
        # print("N = 2, trivially VALID AS_PATH")
        return ASPAVerificationResult.VALID

    # Start at origin AS
    # Find provider next to inflection point in up-ramp customer-provider chain
    R = 1
    while R < N and hop(R, R + 1) == Hop.P:
        R += 1

    # print(f"UP: {describe(R)} is last provider next to inflection point, customer is {describe(R-1)}")
    # print("............. UP done ............")

    if not fromProvider and R == N:
        # print("UP: complete customer-provider chain, VALID upstream AS_PATH.")
        return ASPAVerificationResult.VALID

    # Start at verifying AS
    # Find provider next to inflection point in down-ramp customer-provider chain
    # Note, we can stop checking one hop before the inflection point on the right
    # because a single nA/nP+ Hop is allowed (There's no way to create a route leak)
    hasValleyLeft = False
    hasValleyRight = False

    L = N
    LL = L

    if fromProvider:
        while L > R and hop(L, L - 1) == Hop.P:
            L -= 1

        # print(f"DOWN: {describe(L)} is last provider next to inflection point, customer is {describe(L+1)}")
        # print("............. DOWN done ............")

        # If gap does not exist (sharp tip) or is just a single hop wide,
        # there's no way to create a route leak, return VALID.
        if L - R <= 1:
            # print(f"GAP: gap is {L - R} wide, that's a VALID AS_PATH.")
            return ASPAVerificationResult.VALID

        # Check if there's a nP hop in the gap facing right
        while LL > R and not (hasValleyLeft := (hop(LL, LL - 1) == Hop.nP)):
            LL -= 1

        # print(f"LEFT-TO-RIGHT: found nP+ in Gap: {hasValleyLeft}")

    # Check if there's a nP hop in the gap facing left
    # Note, we can stop checking if we've reached a nP hop
    # found using the loop above
    RR = R
    while RR < LL and not (hasValleyRight := (hop(RR, RR + 1) == Hop.nP)):
        RR += 1

    # print(f"RIGHT-TO-LEFT: found nP+ in Gap: {hasValleyRight}")

    if fromProvider and hasValleyRight and hasValleyLeft:
        # print(f"GAP: nP+ in opposing directions, INVALID AS_PATH.")
        return ASPAVerificationResult.INVALID

    elif (not fromProvider) and hasValleyRight:
        # print("GAP: nP in upstream customer-provider chain, INVALID AS_PATH.")
        return ASPAVerificationResult.INVALID

    return ASPAVerificationResult.UNKNOWN
