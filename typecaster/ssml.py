#!/usr/bin/env python

from six.moves import reduce

html_to_ssml_maps = {
    '<h1>': '<prosody rate="slow" volume="95"><break time="1s" />',
    '</h1>': '</prosody>',
    '<h2>': '<prosody rate="slow" volume="94"><break time="1s" />',
    '</h2>': '</prosody>',
    '<h3>': '<prosody rate="slow" volume="93"><break time="1s" />',
    '</h3>': '</prosody>',
    '<p>': '<break time="0.5s" /><paragraph>',
    '</p>': '</paragraph>',
    '<b>': '<emphasis>',  # Emphasis not supported by IBM API
    '</b>': '</emphasis>'
}


def convert_to_ssml(text, text_format):
    """
    Convert text to SSML based on the text's current format. NOTE: This module
    is extremely limited at the moment and will be expanded.

    :param text:
        The text to convert.
    :param text_format:
        The text format of the text. Currently supports 'plain', 'html' or None
        for skipping SSML conversion.
    """
    if text_format is None:
        return text
    elif text_format == 'plain':
        return plain_to_ssml(text)
    elif text_format == 'html':
        return html_to_ssml(text)
    else:
        raise ValueError(text_format + ': text format not found.')


def plain_to_ssml(text):
    """
    Incomplete. Returns inputted text.
    """
    ssml_text = text
    return ssml_text


def html_to_ssml(text):
    """
    Replaces specific html tags with probable SSML counterparts.
    """
    ssml_text = reduce(lambda x, y: x.replace(y, html_to_ssml_maps[y]), html_to_ssml_maps, text)
    return ssml_text
