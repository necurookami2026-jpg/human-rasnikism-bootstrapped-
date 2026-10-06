import tempfile
from pathlib import Path
import unittest
from tools.media_standardize import convert,digest
try:
    from PIL import Image
except ImportError:Image=None

@unittest.skipIf(Image is None,'Optional desktop Pillow is not installed')
class StandardizeTests(unittest.TestCase):
    def test_jpeg_pixels_original_and_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/'download.jpg';Image.new('RGB',(20,15),(20,70,110)).save(source)
            before=source.read_bytes();result=convert(source,root/'out')
            with Image.open(source) as a,Image.open(root/'out'/result['output']) as b:self.assertEqual(a.tobytes(),b.tobytes())
            self.assertEqual(source.read_bytes(),before);self.assertEqual(convert(source,root/'out'),result)
            (root/'out'/result['output']).write_bytes(b'changed')
            with self.assertRaises(ValueError):convert(source,root/'out')
    def test_animated_and_symlink_not_flattened(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/'animated.gif';Image.new('RGB',(3,3),'red').save(source,save_all=True,append_images=[Image.new('RGB',(3,3),'blue')])
            with self.assertRaises(ValueError):convert(source,root/'out')
            link=root/'link';link.symlink_to(source)
            with self.assertRaises(ValueError):convert(link,root/'out')

class AudioVideoTests(unittest.TestCase):
    def test_lossless_video_and_audio(self):
        import shutil,subprocess
        if Image is None or not shutil.which('ffmpeg') or not shutil.which('ffprobe'):self.skipTest('Optional desktop codecs absent')
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for name,options in [('video.mp4',['-f','lavfi','-i','color=c=blue:s=32x32:r=5','-t','0.4','-c:v','mpeg4']),('audio.wav',['-f','lavfi','-i','sine=frequency=440:sample_rate=44100','-t','0.1']),('float.wav',['-f','lavfi','-i','sine=frequency=440:sample_rate=44100','-t','0.1','-c:a','pcm_f32le'])]:
                source=root/name;subprocess.run(['ffmpeg','-nostdin','-v','error',*options,str(source)],check=True)
                before=digest(source);result=convert(source,root/'out')
                self.assertTrue(result['verified']);self.assertEqual(digest(source),before)
                self.assertTrue(result['output'].endswith('.mkv' if name.startswith('video') else '.wav' if name.startswith('float') else '.flac'))
