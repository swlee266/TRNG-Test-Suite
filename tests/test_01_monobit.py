import numpy as np
import math

def monobit_test(binary):
    """ Tests the proportion of 1s to 0s in the entire binary sequence.

    Returns:
        s (int): test statistic
        p (float) : p-value for the test
        sucecss (bool): test passed/failed
    """

    # binary tricks to compute popcount of u32-bit numpy array
    ones = binary.packed.view(np.uint32)
    ones = ones - ((ones >> 1) & 0x55555555)
    ones = (ones & 0x33333333) + ((ones>> 2) & 0x33333333)
    ones = (((ones + (ones >> 4) & 0xF0F0F0F) * 0x1010101) & 0xffffffff) >> 24
    
    s = 2 * np.sum(ones) - binary.n

    p = math.erfc(s/(math.sqrt(float(binary.n))*math.sqrt(2.0)))
    success = p >= 0.01

    return [p, success]