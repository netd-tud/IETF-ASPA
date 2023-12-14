from enum import Enum
import config
from definitions import *
from simplified import *
from simplified2 import *
from draft import *
from optimized import *
from optimizedZeroBased import *

REFERENCE_IMPL_ID = "draft-16"
REFERENCE_IMPL = verifyASPathDraft16

def testASPACase(label: str, aspa: ASPAObject, path: ASPath, direction: ASPADirection):
    config.enableDebugLogging = False

    impls = {
        REFERENCE_IMPL_ID: REFERENCE_IMPL,
        "optimized": verifyASPathOptimized,
        "optimized0": verifyASPathOptimizedZeroBased,
        "simplified": verifyASPathSimplified,
        "simplified2": verifyASPathSimplified2
    }

    results = {}

    log(f"========== {label} ==========")

    for (implID, impl) in impls.items():
        log(f"==== Running '{implID}' impl... ====")
        results[implID] = impl(aspa, path, direction)
        log(f"Returned {results[implID].name}\n")

    print(f"\n'{label}':")

    # Print each implementation's result before checking if the result
    # doesn't match the reference impl's return value.
    for (implID, result) in results.items():
        print(f"\t - {implID} \t: {result.name}")

    log("\n\n")

    # Compare results to reference value
    for (implID, result) in results.items():
        if implID == REFERENCE_IMPL_ID:
            continue

        if result != results[REFERENCE_IMPL_ID]:
            raise ValueError(f"{label}: {implID} -- Expected {results[REFERENCE_IMPL_ID].name}, but result was {result.name}.")

# == EXAMPLES ==
# Verifying AS has ASN 10

# Example 1 (valid)
#          30   40
#  10  20           70
#                       80 (origin)

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

# Example 2 (unknown)
#          30       40
#  10   20       90      70
#                           80 (origin)

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

# Example 2b (invalid)
#          30*      40*
#  10  20       90      70
#                           80 (origin)

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

# Example 3a (unknown)
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

# Example 3b (unknown)
#          30   90  100 40
#  10  20                 70
#                            80 (origin)

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
#       30*  90  100  40*
#     20                 70
#  10                      80 (origin)

testASPACase(
    label="Ex3c",
    aspa={80: [70], 70: [40], 20: [30], 30: [], 40: []},
    path=[20, 30, 90, 100, 40, 70, 80],
    direction=ASPADirection.DOWNSTREAM,
)

# Example 3d (unknown)
#         30*  40* 100? 90?
#  10  20                  70
#                            80 (origin)

testASPACase(
    label="Ex3d",
    aspa={80: [70], 70: [90], 20: [30], 30: [], 40: []},
    path=[20, 30, 40, 100, 90, 70, 80],
    direction=ASPADirection.DOWNSTREAM,
)

# Example 3f (unknown)
#          30   40  100 90
#  10  20                 70
#                            80 (origin)

testASPACase(
    label="Ex3f",
    aspa={80: [70], 70: [90], 20: [30], 100: [], 40: []},
    path=[20, 30, 40, 100, 90, 70, 80],
    direction=ASPADirection.DOWNSTREAM,
)

# Example 4 (invalid)
#  10                               80 (origin)
#    20   30    40    50   60   70

testASPACase(
    label="Ex4",
    aspa={70: [80]},
    path=[20, 30, 40, 50, 60, 70, 80],
    direction=ASPADirection.UPSTREAM,
)

# Example 4 (invalid)
#  10                      80 (origin)
#    20                70
#      30  40  50  60

testASPACase(
    label="Ex4-fixed",
    aspa={
        70: [80],
        60: [70],
        30: [20],
    },
    path=[20, 30, 40, 50, 60, 70, 80],
    direction=ASPADirection.UPSTREAM,
)

# Example 5 (valid)
# 10  20
#        30
#           40 (origin)

testASPACase(
    label="Ex5",
    aspa={
        40: [30],
        30: [20],
    },
    path=[20, 30, 40],
    direction=ASPADirection.UPSTREAM,
)

# Example 6 (invalid)
#         50         90
#       40  60 70 80   100
#     30                  110
#   20                       120
# 10

testASPACase(
    label="Ex6",
    aspa={
        120: [110],
        110: [100],
        100: [90],
        80: [90],
        60: [50],
        40: [50],
        30: [40],
        20: [30],
    },
    path=[20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120],
    direction=ASPADirection.DOWNSTREAM,
)

# Example 7 (unknown)
# read from right: 100 -U-> 90 -U-> 80 -U-> 70 -U-> 60 -U-> 50
# read from left: 50 -U-> 60 -U-> 70 -U-> 80 -P+-> 90 -P+-> 100
#
#                        100
#                     90     110
#         50 60 70 80           120
#       40                         130
#     30                              140
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

# Example 8 (trivially valid)
#   20
# 10

testASPACase(
    label="Ex8",
    aspa={},
    path=[20],
    direction=ASPADirection.DOWNSTREAM,
)

# Example 9 (trivially valid)
# 10
#   20

testASPACase(
    label="Ex9",
    aspa={},
    path=[20],
    direction=ASPADirection.UPSTREAM,
)

# Example 11 (trivially valid)
#   20 30

testASPACase(
    label="Ex11",
    aspa={20: [], 30: []},
    path=[20, 30],
    direction=ASPADirection.DOWNSTREAM,
)

# Example 12 (Unknown)
#   20 30

testASPACase(
    label="Ex12",
    aspa={},
    path=[20, 30],
    direction=ASPADirection.UPSTREAM,
)

# Example 13 (invalid)
#   20
#      30
#         40  50
#               60

testASPACase(
    label="Ex13",
    aspa={60: [50], 50: [], 40: [30], 30: [20], 20: []},
    path=[20, 30, 40, 50, 60],
    direction=ASPADirection.UPSTREAM,
)

# Example 14 (invalid)
#     30 <> 40 <> 50 <> 60
#  20         

testASPACase(
    label="Ex14",
    aspa={60: [50], 50: [40, 60], 40: [30, 50], 30: [40], 20: [30]},
    path=[20, 30, 40, 50, 60],
    direction=ASPADirection.UPSTREAM,
)

# Example 15 (invalid)
#       30 <> 40 <> 50 <> 60
#   20

testASPACase(
    label="Ex15",
    aspa={60: [50, 20], 50: [40, 60], 40: [30, 50], 30: [40], 20: [30]},
    path=[20, 30, 40, 50, 60],
    direction=ASPADirection.UPSTREAM,
)



# Example 16 (invalid)
#     20   30
# 10           40

testASPACase(
    label="Ex16",
    aspa={
        10: [20],
        20: [100],
        40: [30],
    },
    path=[10, 20, 30, 40],
    direction=ASPADirection.UPSTREAM,
)

# Example 17 (invalid)
#                 X
#     20      40
# 10      30

testASPACase(
    label="Ex17",
    aspa={10: [20], 20: [100], 40: [30, 50], 50: [40]},
    path=[10, 20, 30, 40],
    direction=ASPADirection.UPSTREAM,
)

# Example 18 (invalid)
#  30  20*  40

testASPACase(
    label="Ex18",
    aspa= { 20: [] },
    path = [30, 20, 40],
    direction=ASPADirection.UPSTREAM,
)
