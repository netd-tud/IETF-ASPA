#                 ASPA Playground
#
#       _____________________________________
#         A S P A  :   R O U T E   L E A K S
#            1     :             0
#       -------------------------------------
#
#
#
#       ^^                          |\++++++\
#     __|__/          ASPA          |+\++++++\
#    / /\        ASPA      ASPA     +++\++++++\
#     /  \_ ASPA               ASPA     \++++++\
#                                  ASPA  \++++++\
#                                       AS\++++++\
#                                          |+++++|
#                                          |+++++|
#                                          +++++++

from enum import Enum
from structs import ASPADirection, ASPAVerificationResult, Hop


from simple import new_algorithm
from draft import draft_algorithm
from optimized import optimized_algorithm


# Test
def testASPACase(case):
    # if case["label"] != 'Ex4':
    #    return

    global results
    draft_res = draft_algorithm(case["aspa"], case["path"], case["direction"])
    optimized_res = optimized_algorithm(case["aspa"], case["path"], case["direction"])
    simple_res = new_algorithm(case["aspa"], case["path"], case["direction"])

    if simple_res != optimized_res or simple_res != draft_res or optimized_res != case["expect"]:
        print(case["label"])

    print(
        case["label"],
        "DRAFT:",
        draft_res.name,
        "OPTIMIZED:",
        optimized_res.name,
        "SIMPLE:",
        simple_res.name,
        "EXPECTED:",
        case["expect"].name,
    )


# == EXAMPLES ==
# Verifying AS has ASN 10

# Example_1 (Valid)
#          30   40
#      20           70
#  10                   80 (origin)

testASPACase(
    {
        "label": "Ex1",
        "aspa": {
            80: [70],
            70: [40],
            20: [30],
        },
        "path": [20, 30, 40, 70, 80],
        "direction": ASPADirection.DOWNSTREAM,
        "expect": ASPAVerificationResult.VALID,
    }
)

# Example 2  (Unknown)
#          30       40
#      20       90      70
#  10                       80 (origin)

testASPACase(
    {
        "label": "Ex2",
        "aspa": {
            80: [70],
            70: [40],
            20: [30],
            90: [30, 40],
        },
        "path": [20, 30, 90, 40, 70, 80],
        "direction": ASPADirection.DOWNSTREAM,
        "expect": ASPAVerificationResult.UNKNOWN,
    }
)

# Example 2b  (Invalid)
#          30       40
#      20       90      70
#  10                       80 (origin)

testASPACase(
    {
        "label": "Ex2b",
        "aspa": {
            80: [70],
            70: [40],
            20: [30],
            90: [30, 40],
            30: [],
            40: [],
        },
        "path": [20, 30, 90, 40, 70, 80],
        "direction": ASPADirection.DOWNSTREAM,
        "expect": ASPAVerificationResult.INVALID,
    }
)

# Example 3 (Unkown)
#          30   90  40
#      20               70
#  10                       80 (origin)

testASPACase(
    {
        "label": "Ex3",
        "aspa": {
            80: [70],
            70: [40],
            20: [30],
        },
        "path": [20, 30, 90, 40, 70, 80],
        "direction": ASPADirection.DOWNSTREAM,
        "expect": ASPAVerificationResult.UNKNOWN,
    }
)

# Example 4 (Invalid)
#  10                               80 (origin)
#    100   30    40     50    60 70

testASPACase(
    {
        "label": "Ex4",
        "aspa": {70: [80]},
        "path": [100, 30, 40, 50, 60, 70, 80],
        "direction": ASPADirection.UPSTREAM,
        "expect": ASPAVerificationResult.INVALID,
    }
)

# Example 4 (Invalid)
#  10                            80 (origin)
#    100                      70
#      30    40     50    60

testASPACase(
    {
        "label": "Ex4-fixed",
        "aspa": {
            70: [80],
            60: [70],
            30: [100],
        },
        "path": [100, 30, 40, 50, 60, 70, 80],
        "direction": ASPADirection.UPSTREAM,
        "expect": ASPAVerificationResult.INVALID,
    }
)

# Example 5 (Valid)
# 10
#   20
#      30
#         40 (origin)

testASPACase(
    {
        "label": "Ex5",
        "aspa": {
            40: [30],
            30: [20],
        },
        "path": [20, 30, 40],
        "direction": ASPADirection.UPSTREAM,
        "expect": ASPAVerificationResult.VALID,
    }
)

# Example 6 (Invalid)
#         50         90
#       40  60 70 80    100
#     30                    110
#   20                          120
# 10

testASPACase(
    {
        "label": "Ex6",
        "aspa": {
            120: [110],
            110: [100],
            100: [90],
            80: [90],
            60: [50],
            40: [50],
            30: [40],
            20: [30],
        },
        "path": [20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120],
        "direction": ASPADirection.DOWNSTREAM,
        "expect": ASPAVerificationResult.INVALID,
    }
)

# Example 7 (Unknown)
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
    {
        "label": "Ex7",
        "aspa": {
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
        "path": [20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140],
        "direction": ASPADirection.DOWNSTREAM,
        "expect": ASPAVerificationResult.UNKNOWN,
    }
)

#   20
# 10
# Example 8 (trivially valid)

testASPACase(
    {
        "label": "Ex8",
        "aspa": {},
        "path": [20],
        "direction": ASPADirection.DOWNSTREAM,
        "expect": ASPAVerificationResult.VALID,
    }
)

# 10
#   20
# Example 9 (trivially valid)

testASPACase(
    {
        "label": "Ex9",
        "aspa": {},
        "path": [20],
        "direction": ASPADirection.UPSTREAM,
        "expect": ASPAVerificationResult.VALID,
    }
)

#     30
#   20
# 10
# Example 11 (trivially valid)

testASPACase(
    {
        "label": "Ex11",
        "aspa": {},
        "path": [20, 30],
        "direction": ASPADirection.DOWNSTREAM,
        "expect": ASPAVerificationResult.VALID,
    }
)

# 10
#   20  30
# Example 12 (Invalid)
testASPACase(
    {
        "label": "Ex12",
        "aspa": {},
        "path": [20, 30],
        "direction": ASPADirection.UPSTREAM,
        "expect": ASPAVerificationResult.UNKNOWN,
    }
)

# Example 13 (Unknown)
#               70
#            60    80
#         50         90   100  110
#       40                          120
#     30                                130
#   20
# 10

testASPACase(
    {
        "label": "Ex13",
        "aspa": {20: [30], 30: [40], 40: [50], 50: [60], 60: [70], 90: [80], 80: [70], 130: [120], 120: [110]},
        "path": [20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130],
        "direction": ASPADirection.DOWNSTREAM,
        "expect": ASPAVerificationResult.UNKNOWN,
    }
)

# Example 14 (Unknown)
#               70
#            60    80
#         50         90         110
#       40                100       120
#     30                                130
#   20
# 10

testASPACase(
    {
        "label": "Ex14",
        "aspa": {
            20: [30],
            30: [40],
            40: [50],
            50: [60],
            60: [70],
            90: [80],
            80: [70],
            130: [120],
            120: [110],
            100: [90, 110],
            110: [200],
        },
        "path": [20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130],
        "direction": ASPADirection.DOWNSTREAM,
        "expect": ASPAVerificationResult.INVALID,
    }
)
