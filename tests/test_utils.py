#!/usr/bin/env python

import os
import responses
import unittest
import shutil
from pydub import AudioSegment
from datetime import datetime

from typecaster import utils
import xml.etree.ElementTree as ET


class Object(object):
    pass


def catch_requests():
    # Catch synthesize requests and insert test .wav file as response
    with open("tests/test_files/test.wav", "rb") as test:
        test_response = test.read()

    responses.add(responses.GET, 'https://stream.watsonplatform.net/text-to-speech/api/v1/synthesize',
                  body=test_response, status=200)


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.podcast = Object()
        self.podcast.title = 'Test Podcast'
        self.podcast.link = 'http://test.com'
        self.podcast.author = 'Test Author'
        self.podcast.description = 'This is a test podcast'
        self.podcast.output_path = '.test_utils'
        self.podcast.language = 'en-us'
        self.podcast.subtitle = None
        self.podcast.owner_name = None
        self.podcast.owner_email = None
        self.podcast.image = None
        self.podcast.categories = ['News', 'Sports']
        self.podcast.copyright = None

        self.podcast.episodes = {}
        self.podcast.episodes['Test Episode 1'] = Object()
        self.podcast.episodes['Test Episode 1'].text = 'hello'
        self.podcast.episodes['Test Episode 1'].text_format = 'plain'
        self.podcast.episodes['Test Episode 1'].title = 'Test Episode 1'
        self.podcast.episodes['Test Episode 1'].author = 'Test Episode Author'
        self.podcast.episodes['Test Episode 1'].published = True
        self.podcast.episodes['Test Episode 1'].summary = None
        self.podcast.episodes['Test Episode 1'].link = '.test/test_episode_1.mp3'
        self.podcast.episodes['Test Episode 1'].publish_date = datetime.utcnow()
        self.podcast.episodes['Test Episode 1'].length = 3884
        self.podcast.episodes['Test Episode 1'].duration = '00:00:0.9'
        self.podcast.episodes['Test Episode 1'].synth_args = {'username': '', 'password': ''}

        self.feed = ET.parse('tests/test_files/test_feed.xml')
        self.feed_string = ET.tostring(self.feed.getroot()).decode().replace(' ', '').replace('\n', '')

        self.synthesizer = 'watson'
        self.synth_args = {'username': '', 'password': ''}

        if not os.path.exists(self.podcast.output_path):
            os.makedirs(self.podcast.output_path)

    @responses.activate
    def test_text_to_speech(self):
        catch_requests()

        text = ('hello')

        audio = utils.text_to_speech(text=text, synthesizer=self.synthesizer, synth_args=self.synth_args, sentence_break='. ')
        sample = AudioSegment.from_wav('tests/test_files/test.wav')
        audio.export('.test_utils/test.mp3', format='mp3')

        self.assertEquals(len(audio), len(sample))

    @responses.activate
    def test_text_to_speech_synth_not_found(self):
        catch_requests()

        text = ('hello')

        with self.assertRaises(ValueError):
            audio = utils.text_to_speech(text=text, synthesizer='not found', synth_args=self.synth_args, sentence_break='. ')  # noqa

    @responses.activate
    def test_text_to_speech_sentence_break(self):
        catch_requests()

        text = ('hello ' * 51)

        audio = utils.text_to_speech(text=text, synthesizer=self.synthesizer, synth_args=self.synth_args, sentence_break=' ')
        sample = AudioSegment.from_wav('tests/test_files/test.wav')
        audio.export('.test_utils/test.mp3', format='mp3')

        self.assertGreater(len(audio), len(sample) * 50)

    @responses.activate
    def test_text_to_speech_break_synth_not_found(self):
        catch_requests()

        text = ('hello ' * 51)

        with self.assertRaises(ValueError):
            audio = utils.text_to_speech(text=text, synthesizer='not found', synth_args=self.synth_args, sentence_break=' ')  # noqa

    @responses.activate
    def test_text_to_speech_credential_warning(self):
        catch_requests()

        with self.assertRaises(Warning):
            audio = utils.text_to_speech(text='text', synthesizer=self.synthesizer, synth_args={}, sentence_break=' ')

        with self.assertRaises(Warning):
            audio = utils.text_to_speech(text='text', synthesizer=self.synthesizer, synth_args={'username': ''}, sentence_break=' ')  # noqa

    def test_build_rss_feed(self):
        # This test ignores the pubDate tag in the RSS feed.
        utils.build_rss_feed(self.podcast)

        feed = ET.parse('.test_utils/feed.xml')
        feed_root = feed.getroot()

        items = feed_root.find('channel').findall('item')
        for item in items:
            item.remove(item.find('pubDate'))

        feed_string = ET.tostring(feed_root).decode().replace(' ', '')

        self.assertEquals(feed_string, self.feed_string)

    def tearDown(self):
        if os.path.exists('.temp.wav'):
            os.remove('.temp.wav')
        if os.path.exists('.test_utils/'):
            shutil.rmtree('.test_utils/')
