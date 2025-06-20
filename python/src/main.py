# -*- coding: utf-8 -*-
import subprocess
import re
import sys
import os

"""
mkvinfo 输出示例：

+ EBML head
|+ EBML version: 1
|+ EBML read version: 1
|+ Maximum EBML ID length: 4
|+ Maximum EBML size length: 8
|+ Document type: matroska
|+ Document type version: 4
|+ Document type read version: 2
+ Segment: size 274249883
|+ Seek head (subentries will be skipped)
|+ EBML void: size 4027
|+ Segment information
| + Timestamp scale: 1000000
| + Multiplexing application: libebml v1.4.5 + libmatroska v1.7.1
| + Writing application: mkvmerge v88.0 ('All I Know') 64-bit
| + Duration: 00:50:50.154000000
| + Date: 2025-01-11 23:48:03 UTC
| + Title: Astrid et Rapha毛lle - Hantise - Partie 1
| + Segment UID: 0x65 0x1f 0xcb 0x54 0xf4 0xdd 0x3e 0x34 0x48 0x92 0x42 0x41 0x2b 0x63 0x13 0xf2
|+ Tracks
| + Track
|  + Track number: 1 (track ID for mkvmerge & mkvextract: 0)
|  + Track UID: 2575079188186478636
|  + Track type: video
|  + "Lacing" flag: 0
|  + Language: und
|  + Codec ID: V_MPEGH/ISO/HEVC
|  + Codec's private data: size 2460 (HEVC profile: Main @L3.1)
|  + Default duration: 00:00:00.040000000 (25.000 frames/fields per second for a video track)
|  + Language (IETF BCP 47): und
|  + Video track
|   + Pixel width: 1280
|   + Pixel height: 720
|   + Display width: 1280
|   + Display height: 720
|   + Video color information
|    + Color matrix coefficients: 1
|    + Horizontal chroma siting: 1
|    + Vertical chroma siting: 2
|    + Color range: 1
|    + Color transfer: 1
|    + Color primaries: 1
| + Track
|  + Track number: 2 (track ID for mkvmerge & mkvextract: 1)
|  + Track UID: 13850073446527536543
|  + Track type: audio
|  + Language: fre
|  + Codec ID: A_AAC
|  + Codec's private data: size 5
|  + Default duration: 00:00:00.021333333 (46.875 frames/fields per second for a video track)
|  + Language (IETF BCP 47): fr
|  + Name: Stereo
|  + Audio track
|   + Sampling frequency: 48000
|   + Channels: 2
| + Track
|  + Track number: 3 (track ID for mkvmerge & mkvextract: 2)
|  + Track UID: 947796297657437544
|  + Track type: subtitles
|  + "Lacing" flag: 0
|  + Codec ID: S_TEXT/UTF8
|  + Language (IETF BCP 47): en
|+ EBML void: size 1142
|+ Cluster
"""

def parse_mkvinfo_output(output):
    root = {
        'name': 'root',
        'value': None,
        'level': 0,
        'children': []
    }
    stack = []
    cur_parent = root
    stack.append(cur_parent)

    for line in output.splitlines():
        if line.startswith('+'):
            level = 1
        else:
            match = re.match(r'\|\s*\+', line)
            if match:
                level = match.end() - match.start()
            else:
                continue
        line = line.replace('|', '').replace('+', '').strip()
        name_value = line.split(':', 1)
        name = name_value[0].strip()
        value = name_value[1].strip() if len(name_value) > 1 else None

        node = {'name': name, 'value': value, 'children': [], 'level': level}

        while len(stack) > 0 and stack[-1]['level'] >= level:
            stack.pop()

        if len(stack) > 0 and stack[-1]['level'] + 1 == level:
            cur_parent = stack[-1]
            cur_parent['children'].append(node)
            stack.append(node)
        else:
            raise Exception('Invalid tree structure')

    return root

def find_tracks_node(node):
    if node['name'] == 'Tracks':
        return node
    for child in node['children']:
        result = find_tracks_node(child)
        if result:
            return result
    return None

def parse_tracks(tracks):
    ret = []
    for track in tracks['children']:
        item = {}
        for p in track['children']:
            item[p['name']] = p['value']
        ret.append(item)
    return ret

def extract_subtitle_tracks_from_tree(root):
    tracks = parse_tracks(find_tracks_node(root))

    subtitle_tracks = []
    for track in tracks:
        if track['Track type'] != 'subtitles':
            continue

        track_id = re.search(r'track ID for mkvmerge & mkvextract: (\d+)', track['Track number']).group(1)
        format = track['Codec ID']
        language = track['Language (IETF BCP 47)']

        subtitle_tracks.append({'track_id': track_id, 'format': format, 'language': language})

    return subtitle_tracks

def get_subtitle_tracks(mkv_file):
    result = subprocess.run(['mkvinfo', '--ui-language', 'en', mkv_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = result.stdout

    tree = parse_mkvinfo_output(output)
    subtitle_tracks = extract_subtitle_tracks_from_tree(tree)
    return subtitle_tracks

def extract_single_subtitle(mkv_file, track):
    format_mapping = {
        'S_TEXT/UTF8': 'srt',
        'S_TEXT/ASS': 'ass',
        'S_TEXT/SSA': 'ssa'
    }
    track_id = track['track_id']
    format = format_mapping.get(track['format'], 'srt')
    language = track['language']
    output_file = f"{mkv_file.rsplit('.', 1)[0]}_{language}.{format}"
    subprocess.run(['mkvextract', 'tracks', mkv_file, f"{track_id}:{output_file}"])

def extract_all_subtitles(mkv_file, subtitle_tracks):
    for track in subtitle_tracks:
        extract_single_subtitle(mkv_file, track)

def convert_smb_path(path):
    if os.name == 'nt':
        return path.replace('/', '\\')
    else:
        return path.replace('\\', '/')

def main_cli():
    if len(sys.argv) < 2:
        print("Usage: main.py <mkv_file>")
        sys.exit(1)

    mkv_file = sys.argv[1]
    subtitle_tracks = get_subtitle_tracks(mkv_file)
    extract_all_subtitles(mkv_file, subtitle_tracks)

if __name__ == "__main__":
    if "--gui" in sys.argv:
        from gui import main_gui
        main_gui()
    else:
        main_cli()
