import os
import click
import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi

# from utils.init_app import LANG


@click.command()
@click.option(
    "--video_id",
    help="Video ID of the youtube video to check and index if not found. It can be found in url.\
    For instance, https://www.youtube.com/watch?v=2pWv7GOvuf0 has the video_id '2pWv7GOvuf0'"
)
# @click.option(
#     "--lang",
#     help="Languages(comma separated string) in which transcript needs to be pulled."
# )
def get_srt(video_id):
    """
    Fetch transcript and save it.
    """
    LANG = ['en', 'en-US', 'en-GB', ]
    # LANG = os.environ.get('LANG')
    print(f"DEBUG: parameters-- video_id-{video_id} | lang-{LANG}\n\n")
    srt = YouTubeTranscriptApi.get_transcript(video_id, languages=LANG)
    df_srt = pd.DataFrame(srt)
    df_srt.to_csv("./app_data/raw_tscript_"+video_id+".csv", index=False)
    print("INFO: rows,cols in original transcript data: ", pd.read_csv("./app_data/raw_tscript_"+video_id+".csv").shape)



if __name__ == "__main__":
    get_srt()
