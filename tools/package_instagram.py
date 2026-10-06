"""Build the original Chrome extension ZIP deterministically."""
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
ROOT=Path(__file__).resolve().parents[1]
def build():
    target=ROOT/'releases'/'instagram-orange.zip'
    target.parent.mkdir(exist_ok=True)
    with ZipFile(target,'w') as archive:
        for source in sorted((ROOT/'extensions'/'instagram-orange').iterdir()):
            if not source.is_file():
                continue
            info=ZipInfo(source.name,date_time=(2026,1,1,0,0,0))
            info.compress_type=ZIP_DEFLATED
            info.external_attr=0o644 << 16
            archive.writestr(info,source.read_bytes())
    return target
if __name__=='__main__':
    print(build())
