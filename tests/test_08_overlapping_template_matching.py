import numpy as np
from multiprocessing.dummy import Pool as ThreadPool
import multiprocessing as mp
import scipy.special as ss
from functools import partial

def overlapping_template_matching_test(binary, m=9, K=5):

        def get_prob(u, x):
            out = 1.0 * np.exp(-x)
            if u != 0:
                out = 1.0 * x * np.exp(2 * -x) * (2 ** -u) * ss.hyp1f1(u + 1, 2, x)
            return out

        bits = binary.unpacked
        n = len(bits)
        M =  1032
        N = n // M

        blocks = bits[:N*M].reshape(N,M)

        template = np.ones(m, dtype=np.uint8)
        template = np.packbits(template).view(np.uint16)
        
        if n > 10_000_000:
            with ThreadPool(mp.cpu_count()) as p:
                matches = np.array([*p.imap(partial(overlapping_matches, m=m, template=template), blocks)])
        else:
            matches = np.array([overlapping_matches(block, m, template) for block in blocks])
        # matches = np.array([template_matches(block) for block in blocks])
        lmbda = (M-m+1)/(2**m)
        nu = lmbda/2

        vs = np.array([len(matches[matches == i]) for i in range(6)])
        vs[5] = len(matches[matches >= 5])
        # pis = np.array([0.364091, 0.185659, 0.139381, 0.100571, 0.070432, 0.139865])
        pis = [get_prob(i, nu) for i in range(5)]
        pis = np.array([*pis, 1-sum(pis)])
        
        chisq = sum((vs - N*pis)**2 / (N*pis))

        p = ss.gammaincc(K/2, chisq/2)

        success = (p >= 0.01)
        
        return [p, success]

def overlapping_matches(block, m, template):
    strides = np.packbits(np.lib.stride_tricks.as_strided(block, shape=((block.size - m + 1), m), strides=(block.itemsize,block.itemsize)), axis=1).view(np.uint16).reshape(-1)
    return np.count_nonzero(strides == template)