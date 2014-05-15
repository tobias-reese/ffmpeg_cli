#!/uar/bin/python

import argparse
from datetime import datetime
import re
from ffmpegwrapper.ffmpeg import Input, FFmpeg, Stream, Output
from os.path import splitext
from ffmpegwrapper.filter import VideoFilter

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="input file to encode.")
parser.add_argument("-d", "--debug", help="print resulting command and exit", action="store_true")
parser.add_argument("-c", "--crop", help="add cropping. w:h:xoff:yoff:")
parser.add_argument("-s", "--size", help="set size (wxh, 1920x1024)")
parser.add_argument("-cd", "--crop-detect", help="show cropdetect for 10 sek", action="store_true")
parser.add_argument("-ac", "--audio-channels", nargs="*", help="audio channels to add in order with languages (0:deu, 1:eng)")
args = parser.parse_args()

input_video = Input(args.input.encode('utf-8'))
stream1 = Stream()
stream1.add_parameter('-threads', '5')
stream1.add_parameter('-vcodec', 'libx264')
stream1.add_parameter('-crf', '23')
stream1.add_parameter('-acodec', 'ac3')
stream1.add_parameter('-ab', '192k')
if args.size:
    stream1.add_parameter('-s', args.size)
stream1.add_parameter('-y', '')
stream1.add_mapping('0:0')

audio_streams = []

if args.audio_channels and len(args.audio_channels) > 0:
    for i in xrange(0, len(args.audio_channels)):
        aentry = args.audio_channels[i].split(':')
        if len(aentry) != 2:
            exit("Wrong audio channel format: " + args.audio_channels[i])
        stream = Stream(stream_index=i, stream_type='a')
        stream.set_metadata('language', aentry[1])
        stream.add_mapping('0:' + aentry[0])
        audio_streams.append(stream)



#
# stream2 = Stream(stream_index=0, stream_type='a')
# stream2.set_metadata('language', 'deu')
# stream2.add_mapping('0:2')
#
# stream3 = Stream(stream_index=1, stream_type='a')
# stream3.set_metadata('language', 'eng')
# stream2.add_mapping('0:1')

filter = VideoFilter()
filter.hqdn3d(5, 3)

if args.crop_detect:
    filter.cropdetect()
elif args.crop:
    crop_settings = args.crop.split(':')
    filter.crop(crop_settings[0], crop_settings[1], crop_settings[2], crop_settings[3])

input_file_name, input_file_extension = splitext(args.input)
# output = Output(input_file_name + u".mp4", filter, stream1, stream2, stream3)
output = Output(input_file_name + u".mp4", filter, stream1)
for stream in audio_streams:
    output.append(stream)

ffmpeg = FFmpeg('ffmpeg', input_video, output)

if args.debug:
    print list(ffmpeg)
else:
    proc = ffmpeg.run()
    start = datetime.now()
    while proc.process.poll() is None:
        for line in proc.readlines():
            if args.crop_detect:
                if (datetime.now() - start).total_seconds() > 10:
                    proc.process.kill()
                m = re.search('.*crop=(.*)', line)
                if m:
                    print m.group(1)
            else:
                print line
