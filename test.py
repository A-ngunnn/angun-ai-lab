# function to calculate average of a list of numbers

from typing import List, Union

def calculate_average(numbers: List[Union[int, float]]) -> float:
    """
    Calculate the average of a list of numbers.

    Args:
        numbers: A list of numeric values (integers or floats).

    Returns:
        The average of the numbers as a float, or 0.0 if the list is empty.
    """
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)


