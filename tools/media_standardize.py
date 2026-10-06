"""Preserve downloaded originals and make verified, lossless standard renditions."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

MAX_BYTES=512*1024*1024

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def convert(source, output):
    source=Path(source);output=Path(output)
    if source.is_symlink() or not source.is_file() or not 0<source.stat().st_size<=MAX_BYTES:
        raise ValueError('Source must be a regular file of 1–512 MiB.')
    output.mkdir(parents=True,exist_ok=True)
    if output.is_symlink():raise ValueError('Output must not be a symlink.')
    before=digest(source)
    receipt=output/(source.name+'.'+before[:12]+'.json')
    if receipt.exists():
        existing=json.loads(receipt.read_text())
        target=output/existing['output']
        if target.is_file() and digest(target)==existing['output_sha256']:return existing
        raise ValueError('Existing rendition integrity mismatch; original preserved.')
    try:
        from PIL import Image,ImageOps
        with Image.open(source) as image:
            if getattr(image,'n_frames',1)>1:raise ValueError('Animated images retained as originals; no frame flattening.')
            image.load()
            if image.mode not in ('RGB','RGBA','L','LA','I;16'):
                raise ValueError('Unsupported colour mode retained as original.')
            pixels=ImageOps.exif_transpose(image)
            suffix='.tiff';kind='lossless decoded image';profile=image.info.get('icc_profile')
            with tempfile.TemporaryDirectory(dir=output) as temp:
                tmp=Path(temp)/'image.tiff'
                pixels.save(tmp,format='TIFF',compression='tiff_deflate',icc_profile=profile)
                with Image.open(tmp) as restored:
                    restored.load()
                    if restored.mode!=pixels.mode or restored.size!=pixels.size or restored.tobytes()!=pixels.tobytes():raise ValueError('TIFF pixel verification failed.')
                data=tmp.read_bytes()
    except ImportError:raise ValueError('Install Pillow for image conversion.')
    except __import__('PIL').UnidentifiedImageError:
        probe=subprocess.run(['ffprobe','-v','error','-show_streams','-of','json',str(source.resolve())],capture_output=True,check=True,timeout=30)
        streams=json.loads(probe.stdout)['streams']
        if any(s['codec_type'] not in ('video','audio') for s in streams):raise ValueError('Unsupported additional streams retained as original.')
        formats=[s.get('sample_fmt','') for s in streams if s['codec_type']=='audio']
        floating=any(f.startswith(('flt','dbl')) for f in formats)
        pcm='pcm_f64le' if any(f.startswith('dbl') for f in formats) else 'pcm_f32le' if floating else 'pcm_s32le'
        audio_codec=pcm if floating else 'flac'
        video=any(s['codec_type']=='video' for s in streams)
        suffix='.mkv' if video else '.wav' if floating else '.flac';kind='lossless decoded audiovisual' if video else 'lossless decoded audio'
        with tempfile.TemporaryDirectory(dir=output) as temp:
            tmp=Path(temp)/('media'+suffix)
            command=['ffmpeg','-nostdin','-v','error','-i',str(source.resolve()),'-map','0']
            command+=['-c:v','ffv1','-level','3','-c:a',audio_codec] if video else ['-c:a',audio_codec]
            subprocess.run(command+[str(tmp)],check=True,timeout=600)
            # Compare decoded frame/sample hashes, not compressed bytes.
            def hashes(path):
                result=subprocess.run(['ffmpeg','-nostdin','-v','error','-i',str(path),'-map','0','-c:a',pcm,'-c:v','rawvideo','-f','streamhash','-hash','sha256','-'],capture_output=True,check=True,timeout=600)
                return [line.strip() for line in result.stdout.splitlines() if line and not line.startswith(b'#')]
            if hashes(source.resolve())!=hashes(tmp):raise ValueError('Decoded audiovisual verification failed; original retained.')
            data=tmp.read_bytes()
    if digest(source)!=before:raise ValueError('Source changed during conversion.')
    target=output/(source.name+'.'+before[:12]+suffix)
    with target.open('xb') as stream:stream.write(data)
    result={'source':source.name,'source_sha256':before,'output':target.name,'output_sha256':digest(target),'kind':kind,'verified':True,'original_retained':True,'detail_recovered':False}
    with receipt.open('x') as stream:json.dump(result,stream,indent=2)
    return result

def watch(root,once=False):
    root=Path(root).resolve();root.mkdir(parents=True,exist_ok=True)
    sizes={};done=set()
    while True:
        for path in sorted(root.iterdir()):
            if not path.is_file() or path.is_symlink() or path.suffix in ('.crdownload','.part','.tmp'):continue
            signature=(path.stat().st_size,path.stat().st_mtime_ns)
            if sizes.get(path)!=signature:sizes[path]=signature;continue
            if (path,signature) in done:continue
            try:print(json.dumps(convert(path,root/'standardized')),flush=True)
            except Exception as error:print(json.dumps({'source':path.name,'error':str(error),'original_retained':True}),flush=True)
            done.add((path,signature))
        if once:return
        time.sleep(2)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('source',type=Path);parser.add_argument('--output',type=Path);parser.add_argument('--watch',action='store_true');args=parser.parse_args()
    if args.watch:watch(args.source)
    else:print(json.dumps(convert(args.source,args.output or args.source.parent/'standardized'),indent=2))
if __name__=='__main__':main()
