from enum import Enum
from definitions import *

# Performs draft-ietf-sidrops-aspa-verification-16 verification algorithm
# on an AS_PATH
def verifyASPathDraft16(aspa: ASPAObject, asPath: ASPath, direction: ASPADirection) -> ASPAVerificationResult:
    # See citation at the end of the file
    def describe(i: int):
        return describeAS(aspa, asPath, i, N)
    
    def hop(i: int, j: int) -> Hop:
        return hopAndLog(aspa, asPath, i, j, N)
    
    N = len(asPath)
    
    if N == 0:
        raise ValueError("AS_PATH cannot have length zero")
        
    if direction == ASPADirection.UPSTREAM:
        # Section 6.1. Algorithm for Upstream Paths
        log("Applying draft-ietf-sidrops-aspa-verification-16 6.1 Upstream algorithm...")
        
        # 3. If N = 1, then the procedure halts with the outcome "Valid". Else, continue.
        if N == 1:
            log("N=1, trivially VALID AS_PATH.")
            return ASPAVerificationResult.VALID
        
        # 4. At this step, N ≥ 2. 
        assert(N >= 2)
        
        # If there is an i such that 2 ≤ i ≤ N and 
        # hop(AS(i-1), AS(i)) = "Not Provider+", 
        # then the procedure halts with the outcome "Invalid". 
        # Else, continue.
        for i in inclusiveRange(2, N):
            if hop(i - 1, i) == Hop.nP:
                log("nP+ on upstream path, INVALID AS_PATH.")
                return ASPAVerificationResult.INVALID
            
        # If there is an i such that 2 ≤ i ≤ N and 
        # hop(AS(i-1), AS(i)) = "No Attestation", 
        # then the procedure halts with the outcome "Unknown". 
        for i in inclusiveRange(2, N):
            if hop(i - 1, i) == Hop.nA:
                log("nA on upstream path, UNKNOWN AS_PATH.")
                return ASPAVerificationResult.UNKNOWN
            
        # Else, the procedure halts with the outcome "Valid".
        return ASPAVerificationResult.VALID
    
    elif direction == ASPADirection.DOWNSTREAM:
        # Section 6.2.2. Formal Procedure for Verification of Downstream Paths
        log("Applying draft-ietf-sidrops-aspa-verification-16 6.2.2 Downstream algorithm...")
        
        # 3. If 1 ≤ N ≤ 2, then the procedure halts with the outcome "Valid". Else, continue.
        if N <= 2:
            log("N <= 2, trivially VALID AS_PATH.")
            return ASPAVerificationResult.VALID
        
        # 4. At this step, N ≥ 3.
        assert(N >= 3)
        
        # Given the above-mentioned ordered sequence, 
        # find the lowest value of u (2 ≤ u ≤ N) for which 
        # hop(AS(u-1), AS(u)) = "Not Provider+". Call it u_min. 
        # If no such u_min exists, set u_min = N+1. 
        u_min = N + 1
        for u in inclusiveRange(2, N):
            if hop(u - 1, u) == Hop.nP:
                u_min = u
                break
            
        log(f"u_min = {describe(u_min)}")
        
        # Find the highest value of v (N-1 ≥ v ≥ 1) for which 
        # hop(AS(v+1), AS(v)) = "Not Provider+". Call it v_max. 
        # If no such v_max exists, then set v_max = 0. 
        v_max = 0
        for v in inclusiveRangeInverse(N - 1, 1):
            if hop(v + 1, v) == Hop.nP:
                v_max = v
                break
            
        log(f"v_max = {describe(v_max)}")
        
        # If u_min ≤ v_max, then the procedure halts with the outcome "Invalid". 
        # Else, continue.
        if u_min <= v_max:
            log("u_min <= v_max, INVALID AS_PATH.")
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
            log("L - K <= 1, VALID AS_PATH.")
            return ASPAVerificationResult.VALID
        
        # Else, the procedure halts with the outcome "Unknown".
        return ASPAVerificationResult.UNKNOWN
    
    raise ValueError("Invalid ASPA direction")
    
    
# Comments in verifyASPADraft16:
# @techreport{ietf-sidrops-aspa-verification-16,
#     number =    {draft-ietf-sidrops-aspa-verification-16},
#     type =      {Internet-Draft},
#     institution =   {Internet Engineering Task Force},
#     publisher = {Internet Engineering Task Force},
#     note =      {Work in Progress},
#     url =       {https://datatracker.ietf.org/doc/draft-ietf-sidrops-aspa-verification/16/},
#         author =    {Alexander Azimov and Eugene Bogomazov and Randy Bush and Keyur Patel and Job Snijders and Kotikalapudi Sriram},
#     title =     {{BGP AS\_PATH Verification Based on Autonomous System Provider Authorization (ASPA) Objects}},
#     pagetotal = 23,
#     year =      2023,
#     month =     aug,
#     day =       29,
#     abstract =  {This document describes procedures that make use of Autonomous System Provider Authorization (ASPA) objects in the Resource Public Key Infrastructure (RPKI) to verify the Border Gateway Protocol (BGP) AS\_PATH attribute of advertised routes. This type of AS\_PATH verification provides detection and mitigation of route leaks and improbable AS paths. It also provides protection, to some degree, against prefix hijacks with forged-origin or forged-path-segment.},
# }