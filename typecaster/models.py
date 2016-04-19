#!/usr/bin/env python

import os
import six
from collections import Sequence
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

from typecaster.ssml import convert_to_ssml
from typecaster.utils import text_to_speech, build_rss_feed


class Podcast(object):
    """
    The model that holds the information for a complete podcast.

    :param title:
        The title of the podcast.
    :param link:
        The URL of the podcast.
    :param author:
        The author of the podcast.
    :param description:
        A description of the podcast.
    :param output_path:
        The path to the directory that will hold the podcast's mp3 files and RSS
        feed.
    :param language:
        The language of the podcast. Defaults to 'en-us'.
    :param subtitle:
        The subtitle of the podcast. Defaults to None.
    :param owner_name:
        The name of the podcast's owner. Defaults to None.
    :param owner_email:
        The email address of the podcast's owner. Defaults to None.
    :param image:
        The path to the preview image of the podcast. Defaults to None.
    :param categories:
        A sequence of strings indicating iTunes categories. Defaults to an empty
        sequence.
    :param copyright:
        The copyright of the podcast. Defaults to None.
    :param episodes:
        A dictionary of titles mapped to Episode models for each episode in the
        podcast.
    :param scheduled_jobs:
        A dictionary of titles mapped to scheduled jobs stored in the
        :class:`Podcast`.
    """
    def __init__(self, title, link, author, description, output_path, language='en-us',
                 subtitle=None, owner_name=None, owner_email=None, image=None, categories=[], copyright=None):
        self.title = title
        self.link = link
        self.author = author
        self.description = description
        self.output_path = output_path
        self.language = language
        self.subtitle = subtitle
        self.owner_name = owner_name
        self.owner_email = owner_email
        self.image = image
        self.categories = categories
        self.copyright = copyright

        self.episodes = {}
        self.scheduled_jobs = {}
        self.update_rss_feed()
        self._scheduler = BackgroundScheduler()

    def add_episode(self, text, text_format, title, author, summary=None,
                    publish_date=None, synthesizer='watson', synth_args=None, sentence_break='. '):
        """
        Add a new episode to the podcast.

        :param text:
            See :meth:`Episode`.
        :param text_format:
            See :meth:`Episode`.
        :param title:
            See :meth:`Episode`.
        :param author:
            See :meth:`Episode`.
        :param summary:
            See :meth:`Episode`.
        :param publish_date:
            See :meth:`Episode`.
        :param synthesizer:
            See :meth:`typecaster.utils.text_to_speech`.
        :param synth_args:
            See :meth:`typecaster.utils.text_to_speech`.
        :param sentence_break:
            See :meth:`typecaster.utils.text_to_speech`.
        """
        if title in self.episodes:
            raise ValueError('"' + title + '" already exists as an episode title.')

        link = self.output_path + '/' + title.replace(' ', '_').lower() + '.mp3'
        episode_text = convert_to_ssml(text, text_format)
        new_episode = Episode(episode_text, text_format, title, author, link, summary, publish_date, synthesizer, synth_args, sentence_break)

        self.episodes[title] = new_episode

    def add_scheduled_job(self, text_source, cron_args, text_format, title, author, summary=None,
                          synthesizer='watson', synth_args=None, sentence_break='. '):
        """
        Add and start a new scheduled job to dynamically generate podcasts.

        Note: scheduling will end when the process ends. This works best when run
        inside an existing application.

        :param text_source:
            A function that generates podcast text. Examples: a function that
            opens a file with today's date as a filename or a function that
            requests a specific url and extracts the main text.
            Also see :meth:`Episode`.
        :param cron_args:
            A dictionary of cron parameters. Keys can be: 'year', 'month',
            'day', 'week', 'day_of_week', 'hour', 'minute' and 'second'. Keys
            that are not specified will be parsed as 'any'/'*'.
        :param text_format:
            See :meth:`Episode`.
        :param title:
            See :meth:`Episode`. Since titles need to be unique, a
            timestamp will be appended to the title for each episode.
        :param author:
            See :meth:`Episode`.
        :param summary:
            See :meth:`Episode`.
        :param publish_date:
            See :meth:`Episode`.
        :param synthesizer:
            See :meth:`typecaster.utils.text_to_speech`.
        :param synth_args:
            See :meth:`typecaster.utils.text_to_speech`.
        :param sentence_break:
            See :meth:`typecaster.utils.text_to_speech`.
        """
        if not callable(text_source):
            raise TypeError('Argument "text" must be a function')

        def add_episode():
            episode_text = text_source()
            episode_title = title + '_' + datetime.utcnow().strftime('%Y%m%d%H%M%S')

            self.add_episode(episode_text, text_format, episode_title, author, summary, datetime.utcnow(), synthesizer, synth_args, sentence_break)

        self.scheduled_jobs[title] = self._scheduler.add_job(add_episode, 'cron', id=title, **cron_args)

        if not self._scheduler.running:
            self._scheduler.start()

    def publish(self, titles):
        """
        Publish a set of episodes to the Podcast's RSS feed.

        :param titles:
            Either a single episode title or a sequence of episode titles to
            publish.
        """
        if isinstance(titles, Sequence) and not isinstance(titles, six.string_types):
            for title in titles:
                self.episodes[title].publish()
        elif isinstance(titles, six.string_types):
            self.episodes[titles].publish()
        else:
            raise TypeError('titles must be a string or a sequence of strings.')

        self.update_rss_feed()

    def unpublish(self, titles):
        """
        Unpublish a set of episodes to the Podcast's RSS feed.

        :param titles:
            Either a single episode title or a sequence of episode titles to
            publish.
        """
        if isinstance(titles, Sequence) and not isinstance(titles, six.string_types):
            for title in titles:
                self.episodes[title].unpublish()
        elif isinstance(titles, six.string_types):
            self.episodes[titles].unpublish()
        else:
            raise TypeError('titles must be a string or a sequence of strings.')

        self.update_rss_feed()

    def update_rss_feed(self):
        """
        Updates RSS feed with any changes in Podcast model.
        """
        build_rss_feed(self)


class Episode(object):
    """
    The model that holds the information for a single podcast episode.

    :param text:
        The text of the episode that will be synthesized to audio.
    :param text_format:
        The format of input text. Can be 'html', 'plain' or None. None will
        skip converting to SSML.
    :param title:
        The title of the episode.
    :param author:
        The author of the episode.
    :param link:
        The URL to the mp3 file of the episode.
    :param summary:
        The summary of the episode. Defaults to None.
    :param publish_date:
        The publish date of the episode. If None, set to datetime.utcnow().
        Defaults to None.
    :param published:
        An indicator of whether the episode is published or not.
    :param synthesizer:
        See :meth:`typecaster.utils.text_to_speech`.
    :param synth_args:
        See :meth:`typecaster.utils.text_to_speech`.
    """
    def __init__(self, text, text_format, title, author, link, summary=None, publish_date=None, synthesizer='watson', synth_args=None, sentence_break='. '):
        self.text_format = text_format
        self.title = title
        self.author = author
        self.link = link
        self.summary = summary

        if publish_date is None:
            self.publish_date = datetime.utcnow()
        else:
            self.publish_date = publish_date

        self.published = False
        self.length = 0
        self.duration = 0
        self.synthesizer = synthesizer
        self.synth_args = synth_args
        self.sentence_break = sentence_break

        self._text = convert_to_ssml(text, self.text_format)

        self.render_audio()

    @property
    def text(self):
        """
        Get the text of the episode.
        """
        return self._text

    @text.setter
    def text(self, value):
        """
        Set the text of the episode. This will rerender the episode's audio.
        """
        self._text = value

        self.render_audio()

    def render_audio(self):
        """
        Synthesize audio from the episode's text.
        """
        segment = text_to_speech(self._text, self.synthesizer, self.synth_args, self.sentence_break)

        milli = len(segment)
        seconds = '{0:.1f}'.format(float(milli) / 1000 % 60).zfill(2)
        minutes = '{0:.0f}'.format((milli / (1000 * 60)) % 60).zfill(2)
        hours = '{0:.0f}'.format((milli / (1000 * 60 * 60)) % 24).zfill(2)
        self.duration = hours + ':' + minutes + ':' + seconds

        segment.export(self.link, format='mp3')
        self.length = os.path.getsize(self.link)

    def publish(self):
        """
        Mark an episode as published.
        """
        if self.published is False:
            self.published = True
        else:
            raise Warning(self.title + ' is already published.')

    def unpublish(self):
        """
        Mark an episode as not published.
        """
        if self.published is True:
            self.published = False
        else:
            raise Warning(self.title + ' is already not published.')
