def remap(value, start_range, end_range):
    """Convert given value from one range to another.

    :param value: the value to remap to end_range
    :type value: int
    :param start_range: range that given value is within
    :type start_range: tuple[min, max]
    :param end_range: range to convert given value to
    :type end_range: tuple[min, max]
    :return: the remapped value
    :rtype: int
    """
    # https://stackoverflow.com/questions/1969240/mapping-a-range-of-values-to-another
    # Figure out how 'wide' each range is
    start_max = start_range[1]
    start_min = start_range[0]
    end_max = end_range[1]
    end_min = end_range[0]
    start_span = start_max - start_min
    end_span = end_max - end_min

    # Convert the left range into a 0-1 range (float)
    value_scaled = float(value - start_min) / float(start_span)

    # Convert the 0-1 range into a value in the right range.
    return end_min + (value_scaled * end_span)


def clamp(min_value, value, max_value):
    """Limit given value between a min and max value.
    Alternate to using QBound.
    :param min_value: the lowest value the given value can be
    :type min_value: int or float
    :param value: the value to keep between min_value and max_value
    :type value: int or float
    :param max_value: the highest value the given value can be
    :type max_value: int or float
    :return: the clamped value
    :rtype: int or float
    """
    return max(min(value, max_value), min_value)


def lerp(pt1, pt2, t):
    """Lerp function from KisAlgebra2D."""
    return pt1 + (pt2 - pt1) * t
