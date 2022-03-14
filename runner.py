import sys
import os
import csv


distances_true = {}
distances_false = {}


def update_maps(condition_num, d_true, d_false):
    global distances_true, distances_false

    if condition_num in distances_true.keys():
        distances_true[condition_num] = min(
            distances_true[condition_num], d_true)
    else:
        distances_true[condition_num] = d_true

    if condition_num in distances_false.keys():
        distances_false[condition_num] = min(
            distances_false[condition_num], d_false)
    else:
        distances_false[condition_num] = d_false


def evaluate_condition(num, op, lhs, rhs):
   
    global distances_true, distances_false
    distance_true = 0
    distance_false = 0
    
    if num == '*' and op == '*' and lhs == '*' and rhs == '*':
        return distances_true

    if isinstance(lhs, str):
        lhs = ord(lhs)
    if isinstance(rhs, str):
        rhs = ord(rhs)

    if op == "Eq":
        if lhs == rhs:
            distance_false = 1
        else:
            distance_true = abs(lhs - rhs)

    elif op == "NotEq":
        if lhs != rhs:
            distance_false = abs(lhs - rhs)
        else:
            distance_true = 1

    elif op == "Lt":
        if lhs < rhs:
            distance_false = rhs - lhs
        else:
            distance_true = lhs - rhs + 1

    elif op == "LtE":
        if lhs <= rhs:
            distance_false = rhs - lhs + 1
        else:
            distance_true = lhs - rhs

    elif op == "Gt":
        if lhs > rhs:
            distance_false = lhs - rhs
        else:
            distance_true = rhs - lhs + 1

    elif op == "GtE":
        if lhs >= rhs:
            distance_false = lhs - rhs + 1
        else:
            distance_true = rhs - lhs

    elif op == "In":
        minimum = sys.maxsize
        for elem in rhs:
            distance = abs(lhs - elem)
            if distance < minimum:
                minimum = distance

        distance_true = minimum
        if distance_true == 0:
            distance_false = 1

    update_maps(num, distance_true, distance_false)

    if distance_true == 0:
        return True
    else:
        return False
