"""Compile Ostar reading editions from canonical Markdown; no dependency install."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
EDITIONS = {
    'MAKKAKAH': ('Makkakah', 'Purpose → stewardship → resources → care → observed effects → next review.'),
    'AANTONYMMAKKAKAH': ('Aantonymmakkakah', 'Issue → assumptions → alternative framing → affected people → repair or release → review.'),
    'JURISDICTION-REVIEW': ('Jurisdiction review — UNREVIEWED', 'Activity → potentially applicable jurisdictions → authoritative sources → rights and permissions → unresolved questions → appropriate review.')
}


def compile_editions():
    output = ROOT / 'editions'
    output.mkdir(exist_ok=True)
    sources = sorted(ROOT.glob('*.md'))
    for slug, (name, template) in EDITIONS.items():
        sections = [f'# Ostar Rawful Lair — {name}', '',
                    'AI-assisted collection edition. Definitions remain provisional. No automatic legal, scientific, clinical, or spiritual certification is supplied.', '',
                    '## Edition review template', template, '',
                    'This template frames the retained source sections; it does not change tool behavior or approve their content.', '',
                    '## Source index']
        sections.extend(f'- [{source.name}](../{source.name})' for source in sources)
        sections.extend(['', 'License: [existing repository license](../LICENSE).', ''])
        for source in sources:
            content = source.read_text()
            # Preserve local document links when compiled one directory below sources.
            def relocate(match):
                target = match.group(2)
                if target.startswith(('#', '/', 'http:', 'https:', 'mailto:')):
                    return match.group(0)
                return f'[{match.group(1)}](../{target})'
            content = re.sub(r'\[([^\]]+)\]\(([^\s)]+)\)', relocate, content)
            sections.extend(['---', f'## Source: {source.name}', '', content.rstrip(), ''])
        (output / f'OSTAR-{slug}.md').write_text('\n'.join(sections))
    print(f'Compiled {len(EDITIONS)} editions from {len(sources)} source documents.')


if __name__ == '__main__':
    compile_editions()
