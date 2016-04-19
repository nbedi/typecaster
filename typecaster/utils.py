#!/usr/bin/env python

import os
import requests
from pydub import AudioSegment
import xml.etree.ElementTree as ET

watson_url = 'https://stream.watsonplatform.net/text-to-speech/api/v1/synthesize'


def text_to_speech(text, synthesizer, synth_args, sentence_break):
    """
    Converts given text to a pydub AudioSegment using a specified speech
    synthesizer. At the moment, IBM Watson's text-to-speech API is the only
    available synthesizer.

    :param text:
        The text that will be synthesized to audio.
    :param synthesizer:
        The text-to-speech synthesizer to use.  At the moment, 'watson' is the
        only available input.
    :param synth_args:
        A dictionary of arguments to pass to the synthesizer. Parameters for
        authorization (username/password) should be passed here.
    :param sentence_break:
        A string that identifies a sentence break or another logical break in
        the text. Necessary for text longer than 50 words. Defaults to '. '.
    """
    if len(text.split()) < 50:
        if synthesizer == 'watson':
            with open('.temp.wav', 'wb') as temp:
                temp.write(watson_request(text=text, synth_args=synth_args).content)
            response = AudioSegment.from_wav('.temp.wav')
            os.remove('.temp.wav')
            return response
        else:
            raise ValueError('"' + synthesizer + '" synthesizer not found.')
    else:
        segments = []
        for i, sentence in enumerate(text.split(sentence_break)):
            if synthesizer == 'watson':
                with open('.temp' + str(i) + '.wav', 'wb') as temp:
                    temp.write(watson_request(text=sentence, synth_args=synth_args).content)
                segments.append(AudioSegment.from_wav('.temp' + str(i) + '.wav'))
                os.remove('.temp' + str(i) + '.wav')
            else:
                raise ValueError('"' + synthesizer + '" synthesizer not found.')

        response = segments[0]
        for segment in segments[1:]:
            response = response + segment

        return response


def watson_request(text, synth_args):
    """
    Makes a single request to the IBM Watson text-to-speech API.

    :param text:
        The text that will be synthesized to audio.
    :param synth_args:
        A dictionary of arguments to add to the request. These should include
        username and password for authentication.
    """
    params = {
        'text': text,
        'accept': 'audio/wav'
    }
    if synth_args is not None:
        params.update(synth_args)

    if 'username' in params:
        username = params.pop('username')
    else:
        raise Warning('The IBM Watson API requires credentials that should be passed as "username" and "password" in "synth_args"')
    if 'password' in params:
        password = params.pop('password')
    else:
        raise Warning('The IBM Watson API requires credentials that should be passed as "username" and "password" in "synth_args"')

    return requests.get(watson_url, auth=(username, password), params=params)


def build_rss_feed(podcast):
    """
    Builds a podcast RSS feed and returns an xml file.

    :param podcast:
        A Podcast model to build the RSS feed from.
    """
    if not os.path.exists(podcast.output_path):
        os.makedirs(podcast.output_path)

    rss = ET.Element('rss', attrib={'xmlns:itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd', 'version': '2.0'})

    channel = ET.SubElement(rss, 'channel')
    ET.SubElement(channel, 'title').text = podcast.title
    ET.SubElement(channel, 'link').text = podcast.link
    ET.SubElement(channel, 'copyright').text = podcast.copyright
    ET.SubElement(channel, 'itunes:subtitle').text = podcast.subtitle
    ET.SubElement(channel, 'itunes:author').text = podcast.author
    ET.SubElement(channel, 'itunes:summary').text = podcast.description
    ET.SubElement(channel, 'description').text = podcast.description

    owner = ET.SubElement(channel, 'itunes:owner')
    ET.SubElement(owner, 'itunes:name').text = podcast.owner_name
    ET.SubElement(owner, 'itunes:email').text = podcast.owner_email

    ET.SubElement(channel, 'itunes:image').text = podcast.image

    for category in podcast.categories:
        ET.SubElement(channel, 'itunes:category').text = category

    for episode in sorted(podcast.episodes.values(), key=lambda x: x.publish_date):
        if episode.published is True:
            item = ET.SubElement(channel, 'item')
            ET.SubElement(item, 'title').text = episode.title
            ET.SubElement(item, 'author').text = episode.author
            ET.SubElement(item, 'summary').text = episode.summary
            ET.SubElement(item, 'enclosure', attrib={'url': podcast.link + '/' + episode.link, 'length': str(episode.length), 'type': 'audio/x-mp3'})
            ET.SubElement(item, 'guid').text = podcast.link + '/' + episode.link
            ET.SubElement(item, 'pubDate').text = episode.publish_date.strftime('%a, %d %b %Y %H:%M:%S UTC')
            ET.SubElement(item, 'itunes:duration').text = episode.duration

    tree = ET.ElementTree(rss)
    with open(podcast.output_path + '/feed.xml', 'wb') as feed:
        tree.write(feed)
