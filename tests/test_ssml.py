#!/usr/bin/env python

import unittest

from typecaster import ssml


class TestSSML(unittest.TestCase):
    def setUp(self):
        self.plain = 'hello. goodbye!'
        self.html = '<h1>hello</h1>'
        self.plain_ssml = 'hello. goodbye!'
        self.html_ssml = '<prosody rate="slow" volume="95"><break time="1s" />hello</prosody>'

    def test_from_none(self):
        none_ssml = ssml.convert_to_ssml(self.plain, text_format=None)

        self.assertEquals(none_ssml, self.plain)

    def test_from_plain(self):
        plain_ssml = ssml.convert_to_ssml(self.plain, 'plain')

        self.assertEquals(plain_ssml, self.plain_ssml)

    def test_from_html(self):
        html_ssml = ssml.convert_to_ssml(self.html, 'html')

        self.assertEquals(html_ssml, self.html_ssml)

    def test_from_not_found(self):
        with self.assertRaises(ValueError):
            not_found_ssml = ssml.convert_to_ssml(self.plain, 'not found')  # noqa
