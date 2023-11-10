from enum import Enum
from structs import ASPADirection, ASPAVerificationResult, Hop, inclusiveRange, inclusiveRangeInverse
from simple import new_algorithm


# Performs draft-ietf-sidrops-aspa-verification-16 verification algorithm
# on an AS_PATH
def draft_algorithm(aspa, asPath, direction: ASPADirection) -> ASPAVerificationResult:
    def hop(i, j):
        if not (i >= 1 and i <= N and j >= 1 and j <= N):
            raise ValueError(f"Invalid AS_PATH ASN position: i={i} j={j}, must between 1 and N={N}")
        if asPath[N - i] not in aspa:
            return Hop.nA
        if asPath[N - j] in aspa[asPath[N - i]]:
            return Hop.P
        else:
            return Hop.nP

    N = len(asPath)

    if N == 0:
        raise ValueError("AS_PATH cannot have length zero")

    if direction == ASPADirection.UPSTREAM:
        # Section 6.1. Algorithm for Upstream Paths
        # print("Applying draft-ietf-sidrops-aspa-verification-16 6.1 Upstream algorithm...")

        # 3. If N = 1, then the procedure halts with the outcome "Valid". Else, continue.
        if N == 1:
            # print("N=1, trivially VALID AS_PATH.")
            return ASPAVerificationResult.VALID

        # 4. At this step, N ≥ 2.
        assert N >= 2

        # If there is an i such that 2 ≤ i ≤ N and
        # hop(AS(i-1), AS(i)) = "Not Provider+",
        # then the procedure halts with the outcome "Invalid".
        # Else, continue.
        for i in inclusiveRange(2, N):
            if hop(i - 1, i) == Hop.nP:
                # print("nP+ on upstream path, INVALID AS_PATH.")
                return ASPAVerificationResult.INVALID

        # If there is an i such that 2 ≤ i ≤ N and
        # hop(AS(i-1), AS(i)) = "No Attestation",
        # then the procedure halts with the outcome "Unknown".
        for i in inclusiveRange(2, N):
            if hop(i - 1, i) == Hop.nA:
                # print("nP+ on upstream path, UNKNOWN AS_PATH.")
                return ASPAVerificationResult.UNKNOWN

        # Else, the procedure halts with the outcome "Valid".
        return ASPAVerificationResult.VALID

    elif direction == ASPADirection.DOWNSTREAM:
        # Section 6.2.2. Formal Procedure for Verification of Downstream Paths
        # print("Applying draft-ietf-sidrops-aspa-verification-16 6.2.2 Downstream algorithm...")

        # 3. If 1 ≤ N ≤ 2, then the procedure halts with the outcome "Valid". Else, continue.
        if N <= 2:
            # print("N <= 2, trivially VALID AS_PATH.")
            return ASPAVerificationResult.VALID

        # 4. At this step, N ≥ 3.
        assert N >= 3

        # Given the above-mentioned ordered sequence,
        # find the lowest value of u (2 ≤ u ≤ N) for which
        # hop(AS(u-1), AS(u)) = "Not Provider+". Call it u_min.
        # If no such u_min exists, set u_min = N+1.
        u_min = N + 1
        for u in inclusiveRange(2, N):
            if hop(u - 1, u) == Hop.nP:
                u_min = u
                break

        # print(f"u_min = {describe(u_min)}")

        # Find the highest value of v (N-1 ≥ v ≥ 1) for which
        # hop(AS(v+1), AS(v)) = "Not Provider+". Call it v_max.
        # If no such v_max exists, then set v_max = 0.
        v_max = 0
        for v in inclusiveRangeInverse(N - 1, 1):
            if hop(v + 1, v) == Hop.nP:
                v_max = v
                break

        # print(f"v_max = {describe(v_max)}")

        # If u_min ≤ v_max, then the procedure halts with the outcome "Invalid".
        # Else, continue.
        if u_min <= v_max:
            # print("u_min <= v_max, INVALID AS_PATH.")
            return ASPAVerificationResult.INVALID

        # 5. Up-ramp: For 2 ≤ i ≤ N, determine the largest K such that
        # hop(AS(i-1), AS(i)) = "Provider+" for each i in the range
        # 2 ≤ i ≤ K. If such a largest K does not exist, then set K = 1.
        K = 1
        for i in inclusiveRange(2, N):
            if hop(i - 1, i) == Hop.P:
                K += 1
            else:
                break

        # 6. Down-ramp: For N-1 ≥ j ≥ 1, determine the smallest L such that
        # hop(AS(j+1), AS(j)) = "Provider+" for each j in the range
        # N-1 ≥ j ≥ L. If such smallest L does not exist, then set L = N.
        L = N
        for j in inclusiveRangeInverse(N - 1, 1):
            if hop(j + 1, j) == Hop.P:
                L -= 1
            else:
                break

        # 7. If L-K ≤ 1, then the procedure halts with the outcome "Valid".
        if L - K <= 1:
            # print("L - K <= 1, VALID AS_PATH.")
            return ASPAVerificationResult.VALID

        # Else, the procedure halts with the outcome "Unknown".
        return ASPAVerificationResult.UNKNOWN

    raise ValueError("Invalid ASPA direction")
