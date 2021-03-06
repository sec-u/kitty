# -*- coding: utf-8 -*-
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
Tests for complex, full templates.
'''
from kitty.model.low_level.field import Static, String, Delimiter, BitField, Group, Dynamic
from kitty.model.low_level.field import RandomBits, RandomBytes, Calculated, CalculatedBits
from kitty.model.low_level.field import Clone, CalculatedStr, Hash, CalculatedInt
from kitty.model.low_level.field import ElementCount, IndexOf, Checksum, Size
from kitty.model.low_level.container import Container, ForEach, Conditional, If, IfNot
from kitty.model.low_level.container import Meta, Pad, Repeat, OneOf, TakeFrom, Template
from kitty.model.low_level.container import Trunc
from kitty.model.low_level.encoder import ENC_INT_DEC, ENC_STR_BASE64_NO_NL
from kitty.model.low_level.aliases import SizeInBytes, Sha256
from common import BaseTestCase


class ComplexTest(BaseTestCase):

    def setUp(self):
        super(ComplexTest, self).setUp(None)

    def testDefaultValueWhenNotMutated(self):
        '''
        Check that the default value, before mutation, is as the expected data
        '''
        expected_data = 'Th3 L33ter '
        uut = Template(
            name='uut',
            fields=[
                String('Th'),
                BitField(value=3, length=20, encoder=ENC_INT_DEC),
                Static(' '),
                Container(
                    name='leeter ',
                    fields=[
                        Dynamic(key='hmm', default_value='L3'),
                        String('\xde\xd7\xab', encoder=ENC_STR_BASE64_NO_NL),  # 3ter
                        RandomBytes(' ', min_length=1, max_length=100)
                    ])
            ])
        self.assertEqual(uut.render().tobytes(), expected_data)
        uut.mutate()
        uut.reset()
        self.assertEqual(uut.render().tobytes(), expected_data)

    def testMultipleDependenciesDefaultValue(self):
        expected_data = (
            '\x00\x00\x00\x74' +
            'HAMBURGER' +
            '\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa' +
            '\xf3\xfe\xa2g8\xd6\xc1\xc2K\xef\x89\xe3\xd7\xcfh\xbaH\xf8\x83\x08JS\x82\xa5\x86f\x82\x9b\x18\xc5r\xa9'
        )
        uut = Template(
            name='uut',
            fields=[
                SizeInBytes(sized_field='uut', length=32, name='size'),
                Pad(
                    name='content',
                    fields=[
                        String(value='HAMBURGER'),
                    ],
                    pad_length=640,
                    pad_data='\xaa'),
                Sha256(depends_on='content', name='hash'),
            ])
        self.assertEqual(uut.render().tobytes(), expected_data)
        uut.mutate()
        uut.reset()
        self.assertEqual(uut.render().tobytes(), expected_data)
