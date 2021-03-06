# Copyright (C) 2016 Cisco Systems, Inc. and/or its affiliates. All rights reserved.
#
# This file is part of Kitty.
#
# Kitty is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Kitty is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Kitty.  If not, see <http://www.gnu.org/licenses/>.

'''
Tests for low level encoders:
'''
from kitty.model.low_level.encoder import BitFieldMultiByteEncoder
from kitty.model.low_level.encoder import StrFuncEncoder, StrEncodeEncoder
from kitty.model.low_level.encoder import StrBase64NoNewLineEncoder, StrNullTerminatedEncoder
from kitty.model.low_level import BitField
from kitty.core import KittyException
from bitstring import Bits
from common import BaseTestCase


class BitFieldMultiByteEncoderTest(BaseTestCase):

    def setUp(self, cls=None):
        super(BitFieldMultiByteEncoderTest, self).setUp(cls)

    def _multibyte_len(self, num):
        num_bits = len(bin(num)) - 2
        num_bytes = num_bits / 7
        if num_bits % 7 != 0:
            num_bytes += 1
        return num_bytes*8

    def _test(self, bitfield):
        expected_len = self._multibyte_len(bitfield._default_value)
        # bitfield.mutate()
        rendered = bitfield.render()
        self.assertEquals(expected_len, len(rendered))

    def testUnsignedLength8(self):
        bitfield = BitField(
            0xaa,
            length=8,
            signed=False,
            max_value=255,
            encoder=BitFieldMultiByteEncoder()
        )
        self._test(bitfield)

    def testUnsignedLength16(self):
        bitfield = BitField(
            1234,
            length=16,
            signed=False,
            encoder=BitFieldMultiByteEncoder()
        )
        self._test(bitfield)

    def testUnsignedLength32(self):
        bitfield = BitField(
            1234,
            length=32,
            signed=False,
            encoder=BitFieldMultiByteEncoder()
        )
        self._test(bitfield)

    def testUnsignedLength64(self):
        bitfield = BitField(
            78945,
            length=64,
            signed=False,
            encoder=BitFieldMultiByteEncoder()
        )
        self._test(bitfield)

    def testUnsignedLength11(self):
        bitfield = BitField(
            14,
            length=11,
            signed=False,
            encoder=BitFieldMultiByteEncoder()
        )
        self._test(bitfield)

    def testBitFieldMultiByteEncoderSignedUnsupported(self):
        with self.assertRaises(KittyException):
            BitField(
                -12,
                length=8,
                signed=True,
                max_value=127,
                encoder=BitFieldMultiByteEncoder()
            )


class StrFuncEncoderTest(BaseTestCase):

    def setUp(self, cls=StrFuncEncoder):
        super(StrFuncEncoderTest, self).setUp(cls)

    def _encode_func(self, s):
        return s.encode('hex')

    def get_default_encoder(self):
        return self.cls(self._encode_func)

    def testReturnValueIsBits(self):
        uut = self.get_default_encoder()
        encoded = uut.encode('abc')
        self.assertIsInstance(encoded, Bits)

    def testExceptionIfInputIsInt(self):
        uut = self.get_default_encoder()
        with self.assertRaises(KittyException):
            uut.encode(1)

    def testExceptionIfInputIsList(self):
        uut = self.get_default_encoder()
        with self.assertRaises(KittyException):
            uut.encode([])

    def testExceptionIfInputIsStringList(self):
        uut = self.get_default_encoder()
        with self.assertRaises(KittyException):
            uut.encode(['a', 'b', 'c'])

    def testCorrectValueEncoded(self):
        value = 'abcd'
        expected_encoded = self._encode_func(value)
        uut = self.get_default_encoder()
        encoded = uut.encode(value).tobytes()
        self.assertEqual(encoded, expected_encoded)

    def testEmptyValueEncoded(self):
        value = ''
        expected_encoded = self._encode_func(value)
        uut = self.get_default_encoder()
        encoded = uut.encode(value).tobytes()
        self.assertEqual(encoded, expected_encoded)


class StrEncodeEncoderTest(StrFuncEncoderTest):

    def setUp(self, cls=StrEncodeEncoder):
        super(StrEncodeEncoderTest, self).setUp(cls)
        self.encoding = 'hex'

    def _encode_func(self, s):
        return s.encode('hex')

    def get_default_encoder(self):
        return self.cls(self.encoding)


class StrBase64NoNewLineEncoderTest(StrFuncEncoderTest):

    def setUp(self, cls=StrBase64NoNewLineEncoder):
        super(StrBase64NoNewLineEncoderTest, self).setUp(cls)

    def _encode_func(self, s):
        return s.encode('base64')[:-1]

    def get_default_encoder(self):
        return self.cls()


class StrNullTerminatedEncoderTest(StrFuncEncoderTest):

    def setUp(self, cls=StrNullTerminatedEncoder):
        super(StrNullTerminatedEncoderTest, self).setUp(cls)

    def _encode_func(self, s):
        return s + '\x00'

    def get_default_encoder(self):
        return self.cls()

