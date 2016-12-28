#!/usr/bin/env python
# Author: Geoffrey Golliher (ggolliher@katch.com)

import string


class HashBuilder(object):
    def __init__(self, key_space):
        self.alphabet = string.lowercase + string.uppercase + '1234567890'
        self.key_space = key_space
        self.mapping = range(self.key_space)

    def build_hash(self, n):
        """Retrieves an encoded hash.

        Args:
            n, Int representing the index of the hash.

        Returns:
            String, A fully encoded hash.
        """
        if n < 1:
            return False
        return self.encode(self.hash(n))

    def index_from_hash(self, st):
        """Retrieves the hash key from a particular hash.

        Args:
            st, A string hash.

        Returns:
            Int representing the index of the hash.
        """
        return self.hash_key(self.decode(st))

    def hash(self, n):
        result = 0
        # Walk the blocksize
        for i, c in enumerate(reversed(self.mapping)):
            # Logical and of n and 1 * (2**i)
            if n & (1 << i):
                # Logical or of n and 1 * (2**c)
                result |= 1 << c
        return result

    def hash_key(self, n):
        """Returns the key for the passed in hash."""
        result = 0
        # We do the same things here as with hash. The difference is
        # we reverse the index and the count of the enumerate output.
        for i, c in enumerate(reversed(self.mapping)):
            if n & (1 << c):
                result |= 1 << i
        return result

    def encode(self, x):
        """Returns the encoded integer built from the hash function."""
        return '{}'.format(self.__encode(x))

    def __encode(self, x):
        # Recursively works out a divmod hashed sequence.
        # The encoding is reversable. This function is private.
        n = len(self.alphabet)
        if x < n:
            return self.alphabet[x]
        return self.__encode(int(x / n)) + self.alphabet[int(x % n)]

    def decode(self, x):
        """Decodes a given string to the constituent integer.

        Args:
            x: An integer

        Returns:
            Integer: An integer representing the numerical value of the hash.
        """
        n = len(self.alphabet)
        result = 0
        for i, c in enumerate(reversed(x)):
            result += self.alphabet.index(c) * (n ** i)
        return result
