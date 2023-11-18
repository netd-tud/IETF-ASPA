from enum import Enum
import config
from definitions import *
from simplified import *
from draft import *
from optimized import *
from optimizedZeroBased import *


def testASPACase(label: str, aspa: ASPAObject, path: ASPath, direction: ASPADirection):
    config.enableDebugLogging = True
    
    log(f"========== {label} ==========")
    draftRes = verifyASPathDraft16(aspa, path, direction)
    log(f"Returned {draftRes.name}")
    
    log("\nApplying optimized algo...")
    optRes = verifyASPathEfficient(aspa, path, direction)
    log(f"Returned {optRes.name}")
    
    log("\nApplying optimized zero-based algo...")
    optRes0 = verifyASPathEfficientZeroBased(aspa, path, direction)
    log(f"Returned {optRes0.name}")
    
    log("\nApplying simplified algo...")
    simpleRes = verifyASPathSimplified(aspa, path, direction)
    log(f"Returned {simpleRes.name}")

    print(f"\n{label}:")
    print(f"\t - draft-16 \t: {draftRes.name}")
    print(f"\t - optimized \t: {optRes.name}")
    print(f"\t - optimized0 \t: {optRes0.name}")
    print(f"\t - simplified \t: {simpleRes.name}")
    log("\n\n")
    
    if optRes != draftRes:
        raise ValueError(f"{label}: Expected {draftRes.name}, but result was {optRes.name}.")
        
    if optRes0 != draftRes:
        raise ValueError(f"{label}: Expected {draftRes.name}, but result was {optRes0.name}.")
        
    if simpleRes != draftRes:
        raise ValueError(f"{label}: Expected {draftRes.name}, but result was {simpleRes.name}.")
    


# == EXAMPLES ==
# Verifying AS has ASN 10
    
# Example_1 (Valid)
#          30   40
#      20           70
#  10                   80 (origin)
    
testASPACase(
    label="Ex1",
    aspa={
        80: [70],
        70: [40],
        20: [30],
    },
    path=[20, 30, 40, 70, 80],
    direction=ASPADirection.DOWNSTREAM,
)

# Example 2  (Invalid)
#          30       40
#      20       90      70
#  10                       80 (origin)

testASPACase(
    label="Ex2",
    aspa={
        80: [70],
        70: [40],
        20: [30],
        90: [30, 40],
    },
    path=[20, 30, 90, 40, 70, 80],
    direction=ASPADirection.DOWNSTREAM,
)

# Example 2b  (Invalid)
#          30       40
#      20       90      70
#  10                       80 (origin)

testASPACase(
    label="Ex2b",
    aspa={
        80: [70],
        70: [40],
        20: [30],
        90: [30, 40],
        30: [],
        40: [],
    },
    path=[20, 30, 90, 40, 70, 80],
    direction=ASPADirection.DOWNSTREAM,
)

# Example 3a (Unkown)
#          30   90  40
#      20               70
#  10                       80 (origin)

testASPACase(
    label="Ex3a",
    aspa={
        80: [70],
        70: [40],
        20: [30],
    },
    path=[20, 30, 90, 40, 70, 80],
    direction=ASPADirection.DOWNSTREAM,
)

# Example 3b (Unkown)
#          30   90  100 40
#      20                 70
#  10                         80 (origin)

testASPACase(
    label="Ex3b",
    aspa={
        80: [70],
        70: [40],
        20: [30],
    },
    path=[20, 30, 90, 100, 40, 70, 80],
    direction=ASPADirection.DOWNSTREAM,
)

# Example 3c (Invalid)
#          30   90  100 40
#      20                 70
#  10                         80 (origin)

testASPACase(
    label="Ex3c",
    aspa={
        80: [70],
        70: [40],
        20: [30],
        30: [],
        40: []
    },
    path=[20, 30, 90, 100, 40, 70, 80],
    direction=ASPADirection.DOWNSTREAM,
)

# Example 3d (??)
#          30   90  100 40
#      20                 70
#  10                         80 (origin)

testASPACase(
    label="Ex3d",
    aspa={
        80: [70],
        70: [40],
        20: [30],
        30: [],
        90: []
    },
    path=[20, 30, 90, 100, 40, 70, 80],
    direction=ASPADirection.DOWNSTREAM,
)

# Example 3f (??)
#          30   90  100 40
#      20                 70
#  10                         80 (origin)

testASPACase(
    label="Ex3f",
    aspa={
        80: [70],
        70: [40],
        20: [30],
        100: [],
        90: []
    },
    path=[20, 30, 90, 100, 40, 70, 80],
    direction=ASPADirection.DOWNSTREAM,
)

# Example 4 (Invalid)
#  10                               80 (origin)
#    100   30    40     50    60 70

testASPACase(
    label="Ex4",
    aspa={
        70: [80]
    },
    path=[100, 30, 40, 50, 60, 70, 80],
    direction=ASPADirection.UPSTREAM,
)

# Example 4 (Invalid)
#  10                            80 (origin)
#    100                      70
#      30    40     50    60

testASPACase(
    label="Ex4-fixed",
    aspa={
        70: [80],
        60: [70],
        30: [100],
    },
    path=[100, 30, 40, 50, 60, 70, 80],
    direction=ASPADirection.UPSTREAM,
)

# Example 5 (Valid)
# 10
#   20
#      30
#         40 (origin)

testASPACase(
    label="Ex5",
    aspa={
        40: [30],
        30: [20],
    },
    path=[20, 30, 40],
    direction=ASPADirection.UPSTREAM,
)

# Example 6 (Invalid)
#         50         90
#       40  60 70 80    100
#     30                    110
#   20                          120
# 10

testASPACase(
    label="Ex6",
    aspa={
        120:  [110],
        110:  [100],
        100:  [90],
        80: [90],
        60: [50],
        40: [50],
        30: [40],
        20: [30],
    },
    path=[20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120],
    direction=ASPADirection.DOWNSTREAM,
)

# Example 7 (Invalid)
# Read From Right: 100 -> U -> 90 -> U -> 80 -> U -> 70 -> U -> 60 -> U -> 50
# Read from Left: 50 -> U -> 60 -> U -> 70 -> U -> 80 -> P+ -> 90 -> P+ -> 100
#                         100
#                      90     110
#         50 60 70 80             120
#       40                           130
#     30                                140
#   20
# 10

testASPACase(
    label="Ex7",
    aspa={
        20: [30],
        30: [40],
        40: [50],
        80: [90],
        90: [100],
        110: [100],
        120: [110],
        130: [120],
        140: [130],
    },
    path=[20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140],
    direction=ASPADirection.DOWNSTREAM,
)

#   20
# 10
# Example 8 (trivially valid)

testASPACase(
    label="Ex8",
    aspa={},
    path=[20],
    direction=ASPADirection.DOWNSTREAM,
)

# 10
#   20
# Example 9 (trivially valid)

testASPACase(
    label="Ex9",
    aspa={},
    path=[20],
    direction=ASPADirection.UPSTREAM,
)

#   20 30
# Example 11 (trivially valid)

testASPACase(
    label="Ex11",
    aspa={
        20: [],
        30: []
    },
    path=[20, 30],
    direction=ASPADirection.DOWNSTREAM,
)

#   20 30
# Example 12 (Unknown)

testASPACase(
    label="Ex12",
    aspa={},
    path=[20, 30],
    direction=ASPADirection.UPSTREAM,
)

#   20
#       30
#           40 <-| 50
#                    60
# Example 13 (invalid)

testASPACase(
    label="Ex13",
    aspa={
        60: [50],
        50: [],
        40: [30],
        30: [20],
        20: []
    },
    path=[20, 30, 40, 50, 60],
    direction=ASPADirection.UPSTREAM,
)

#   20
#       30
#           40 
#               50
#                    60
# Example 14 (invalid)

testASPACase(
    label="Ex13",
    aspa={
        60: [50],
        50: [40, 60],
        40: [30, 50],
        30: [   40],
        20: [30]
    },
    path=[20, 30, 40, 50, 60],
    direction=ASPADirection.UPSTREAM,
)

#   20
#       30
#           40 
#               50
#                    60
# Example 14 (invalid)

testASPACase(
    label="Ex14",
    aspa={
        60: [50, 20],
        50: [40, 60],
        40: [30, 50],
        30: [   40],
        20: [30]
    },
    path=[20, 30, 40, 50, 60],
    direction=ASPADirection.UPSTREAM,
)