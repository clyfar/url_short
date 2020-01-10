#!/usr/bin/env python
# Author: Geoffrey Golliher (brokenway@gmail.com)

import unittest

from hash_lib import HashBuilder


class TestHashBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = HashBuilder(32)

class TestHashBuilderFunctions(TestHashBuilder):

    def test_build_hash(self):
        # Tests the encoded hash.
        index = 20
        h = self.builder.build_hash(index)
        self.assertEqual(h, 'TzYYu')
        index = 0
        h = self.builder.build_hash(index)
        self.assertFalse(h)

    def test_hash(self):
        # Tests the un-encoded hash.
        index = 20
        h = self.builder.hash(index)
        self.assertEqual(h, 671088640)

    def test_hash_key(self):
        # Tests the reversibility of the hash.
        index = 20
        h = 671088640
        k = self.builder.hash_key(h)
        self.assertEqual(k, index)

    def test_index_from_hash(self):
        # Tests the reversibility of the encoded hash.
        index = 20
        h = self.builder.build_hash(index)
        k = self.builder.index_from_hash(h)
        self.assertEqual(k, index)

    def test_encode(self):
        # Tests encoding a hash.
        index = 20
        h = self.builder.hash(index)
        k = self.builder.encode(h)
        self.assertEqual(h, 671088640)
        self.assertEqual(k, 'TzYYu')

    def test_decode(self):
        # Tests decoding a hash.
        index = 20
        h = self.builder.hash(index)
        k = self.builder.encode(h)
        d = self.builder.decode(k)
        self.assertEqual(h, 671088640)
        self.assertEqual(k, 'TzYYu')
        self.assertEqual(d, 671088640)

if __name__ == '__main__':
    unittest.main()
