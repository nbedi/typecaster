
import os
import shutil
import responses
from datetime import datetime
import unittest
from time import sleep
from pydub import AudioSegment
import xml.etree.ElementTree as ET

from typecaster.models import Podcast


def catch_requests():
    # Catch synthesize requests and insert test .wav file as response
    with open("tests/test_files/test.wav", "rb") as test:
        test_response = test.read()

    responses.add(responses.GET, 'https://stream.watsonplatform.net/text-to-speech/api/v1/synthesize',
                  body=test_response, status=200)


class TestModels(unittest.TestCase):
    @responses.activate
    def setUp(self):
        catch_requests()

        self.synth_args = {'username': '', 'password': ''}
        self.output_path = '.test_models'
        self.podcast = Podcast(title='Test Podcast', link='http://test.com', author='Test Author',
                               description='This is a test podcast', output_path=self.output_path)

    @responses.activate
    def test_podcast_add_episode(self):
        catch_requests()

        episode_title = 'Test Episode 1'
        self.podcast.add_episode('hello', 'plain', episode_title, 'Test Episode Author', synth_args=self.synth_args)

        # Check mp3 file
        path = self.output_path + '/' + episode_title.lower().replace(' ', '_') + '.mp3'
        self.assertTrue(os.path.isfile(path))

    @responses.activate
    def test_podcast_add_episode_value_error(self):
        catch_requests()

        episode_title = 'Test Episode 1'
        self.podcast.add_episode('hello', 'plain', episode_title, 'Test Episode Author', synth_args=self.synth_args)
        with self.assertRaises(ValueError):
            self.podcast.add_episode('goodbye', 'html', episode_title, 'Test Episode Author 2', synth_args=self.synth_args)

    @responses.activate
    def test_podcast_publish(self):
        catch_requests()

        episode_title = 'Test Episode 1'
        self.podcast.add_episode('hello', 'plain', episode_title, 'Test Episode Author', synth_args=self.synth_args)
        self.podcast.publish(episode_title)

        # Check RSS feed
        xml = ET.parse(self.output_path + '/feed.xml')
        root = xml.getroot()
        channel = root.find('channel')
        items = channel.findall('item')
        self.assertEquals(1, len(items))

        self.assertEquals(episode_title, items[0].find('title').text)

    @responses.activate
    def test_podcast_publish_warning(self):
        catch_requests()

        episode_title = 'Test Episode 1'
        self.podcast.add_episode('hello', 'plain', episode_title, 'Test Episode Author', synth_args=self.synth_args)
        self.podcast.publish(episode_title)

        with self.assertRaises(Warning):
            self.podcast.publish(episode_title)

    def test_podcast_publish_type_error(self):
        with self.assertRaises(TypeError):
            self.podcast.publish(1)

    @responses.activate
    def test_podcast_unpublish(self):
        catch_requests()

        episode_title = 'Test Episode 1'
        self.podcast.add_episode('hello', 'plain', episode_title, 'Test Episode Author', synth_args=self.synth_args)
        self.podcast.publish(episode_title)
        self.podcast.unpublish(episode_title)
        # Check RSS feed
        xml = ET.parse(self.output_path + '/feed.xml')
        root = xml.getroot()
        channel = root.find('channel')
        items = channel.findall('item')
        self.assertEquals(0, len(items))

    @responses.activate
    def test_podcast_unpublish_sequence(self):
        catch_requests()

        episode_title = 'Test Episode 1'
        self.podcast.add_episode('hello', 'plain', episode_title, 'Test Episode Author', synth_args=self.synth_args)
        episode_title_2 = 'Test Episode 2'
        self.podcast.add_episode('hello', 'plain', episode_title_2, 'Test Episode Author', synth_args=self.synth_args)
        self.podcast.publish([episode_title, episode_title_2])
        self.podcast.unpublish([episode_title, episode_title_2])
        # Check RSS feed
        xml = ET.parse(self.output_path + '/feed.xml')
        root = xml.getroot()
        channel = root.find('channel')
        items = channel.findall('item')
        self.assertEquals(0, len(items))

    @responses.activate
    def test_podcast_unpublish_warning(self):
        catch_requests()

        episode_title = 'Test Episode 1'
        self.podcast.add_episode('hello', 'plain', episode_title, 'Test Episode Author', synth_args=self.synth_args)

        with self.assertRaises(Warning):
            self.podcast.unpublish(episode_title)

    def test_podcast_unpublish_type_error(self):
        with self.assertRaises(TypeError):
            self.podcast.unpublish(1)

    @responses.activate
    def test_podcast_add_scheduled_job(self):
        catch_requests()

        times = []

        def scheduled_text():
            now = datetime.utcnow()
            times.append(now)
            return str(now)

        cron_args = {'second': '*/2'}

        title = 'scheduled'
        self.podcast.add_scheduled_job(scheduled_text, cron_args, 'plain', title, 'me', synth_args=self.synth_args)
        sleep(3)

        # Check mp3 files
        episode_titles = []
        for time in times:
            episode_title = title + '_' + time.strftime('%Y%m%d%H%M%S')
            episode_titles.append(episode_title)
            path = self.output_path + '/' + episode_title + '.mp3'
            self.assertTrue(os.path.isfile(path))

        self.podcast.publish(episode_titles)

        # Check RSS feed
        xml = ET.parse(self.output_path + '/feed.xml')
        root = xml.getroot()
        channel = root.find('channel')
        items = channel.findall('item')
        self.assertEquals(len(episode_titles), len(items))

        for episode_title, item in zip(episode_titles, items):
            self.assertEquals(episode_title, item.find('title').text)

        self.podcast._scheduler.shutdown()

    def test_podcast_add_scheduled_job_type_error(self):
        with self.assertRaises(TypeError):
            self.podcast.add_scheduled_job('error', {'hour': '1'}, 'plain', 'title', 'me')

    @responses.activate
    def test_episode_text_getter(self):
        catch_requests()

        episode_title = 'Test Episode 1'
        self.podcast.add_episode('hello', 'plain', episode_title, 'Test Episode Author', sentence_break=' ', synth_args=self.synth_args)
        self.assertEquals(self.podcast.episodes[episode_title].text, 'hello')

    @responses.activate
    def test_episode_text_setter(self):
        catch_requests()

        episode_title = 'Test Episode 1'
        self.podcast.add_episode('hello', 'plain', episode_title, 'Test Episode Author', sentence_break=' ', synth_args=self.synth_args)
        self.podcast.publish(episode_title)

        before_audio = AudioSegment.from_mp3(self.output_path + '/test_episode_1.mp3')
        before_length = len(before_audio)

        self.podcast.episodes[episode_title].text = 'hello ' * 51

        after_audio = AudioSegment.from_mp3(self.output_path + '/test_episode_1.mp3')
        after_length = len(after_audio)

        self.assertGreater(after_length, before_length * 50)

    def tearDown(self):
        if self.podcast._scheduler.running:
            self.podcast._scheduler.shutdown()

        if os.path.exists(self.output_path):
            shutil.rmtree(self.output_path)
