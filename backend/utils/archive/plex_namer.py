import re
from pathlib import Path

def rename_to_plex_format(original_filename, metadata):
    ext = Path(original_filename).suffix
    name = re.sub(r'[\\\\/:*?"<>|]', '', metadata['title'])
    if metadata['type'] == 'movie':
        return f"{name} ({metadata['year']}){ext}"
    else:
        season = metadata.get('season', '01')
        episode = metadata.get('episode', '01')
        return f"{name} - S{season.zfill(2)}E{episode.zfill(2)}{ext}"