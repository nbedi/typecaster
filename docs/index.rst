
.. include:: ../README.rst

|

===============
Getting started
===============

To start, install typecaster with pip::

    pip install typecaster
    
Create a podcast:

.. code-block:: python

    from typecaster import Podcast
    
    my_podcast = Podcast(title='My Podcast', link='http://mypodcast.com', 
                         author='Me', description='My typecaster podcast', 
                         output_path='.')

Manually add and publish an episode to the podcast:

.. code-block:: python

    # Load synthesizer arguments and credentials
    import json
    synth_args = json.load(open('params.json'))

    # Add episode
    episode_text = open('script.txt').read()
    my_podcast.add_episode(episode_text, text_format='plain', title='Episode 1', 
                           author='Me', synth_args=synth_args)

    # Publish episode to RSS feed
    my_podcast.publish('Episode 1')

Schedule dynamically generated episodes on your podcast:

Note: scheduling will end when the process ends. This works best when run
inside an existing application. Daemonizing scheduled jobs may be a feature in
the future.

.. code-block:: python

    from datetime import datetime
    
    def get_episode_text():
        datestamp = datetime.utcnow().strftime('%Y%m%d')
        return open('script_' + datestamp + '.txt').read()

    cron_args = { 'hour': 6 }  # At 6 am every day

    my_podcast.add_scheduled_job(text_source=get_episode_text, 
                                 text_format='plain', cron_args=cron_args, 
                                 title='typecaster Episode', author='Me')

    # Pause scheduled job
    my_podcast.scheduled_jobs['typecaster Episode'].pause()

    # Resume scheduled job
    my_podcast.scheduled_jobs['typecaster Episode'].resume()

IBM API
=======

At the moment, typecaster only supports `IBM Watson's text-to-speech API <http://www.ibm.com/smarterplanet/us/en/ibmwatson/developercloud/text-to-speech.html>`_ 
as a synthesizer. To use the API, you must get credentials from IBM and pass 
them as `synth_args <#typecaster.models.Podcast.add_episode>`_.

Right now, the API is free to use for the first million characters every month.
That is about 7000 words per day. Additional characters are $0.02 per thousand.
The API can accept 7 different languages and has a selection of voices for
each language.

Learn more about getting credentials at `IBM's developer cloud <http://www.ibm.com/smarterplanet/us/en/ibmwatson/developercloud/doc/getting_started/gs-credentials.shtml>`_.

Read `documentation <http://www.ibm.com/smarterplanet/us/en/ibmwatson/developercloud/doc/text-to-speech/index.shtml>`_
on the text-to-speech API to learn about all possible `synth_args <#typecaster.models.Podcast.add_episode>`_.

========
Examples
========

Podcasts built with typecaster:

  - `NYT Morning Briefing <https://nwp.neilbedi.com>`_ (`iTunes <https://itunes.apple.com/us/podcast/nytimes-morning-briefing-by/id1043147305>`_)

===
API
===

Models
======

.. automodule:: typecaster.models
    :members:

Utils
=====

.. automodule:: typecaster.utils
    :members:
    
SSML
====    

.. automodule:: typecaster.ssml
    :members:
   
=======
License
=======

.. include:: ../LICENSE

==================
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
