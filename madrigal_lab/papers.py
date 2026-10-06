"""Finite prose workpapers, original seed writing and manually supplied map plots."""
import hashlib
import html
import math

FORMATS = {
    'rawful': ('Construction record', 'Record the inputs, derivation and observed result.'),
    'raw': ('Working record', 'Preserve the supplied account for a later review.'),
    'magazine': ('Editorial feature', 'Identify the audience and the evidence supporting this account.'),
    'ring': ('Return and review', 'Revisit this version when its assumptions change.'),
    'seek': ('Inquiry paper', 'Keep the question distinct from the proposed answer.'),
    'hobbit': ('Fictional reading paper', 'Treat this supplied label as fictional; no franchise rights are granted.'),
    'brochure': ('Information paper', 'Explain the declared service and its available alternatives.'),
    'search': ('Search record', 'Record a query, its scope and the limits of the returned material.'),
    'wise': ('Reflective paper', 'Distinguish an interpretation from the observation that prompted it.'),
    'lecture': ('Learning paper', 'Describe an exercise and how its finite result can be checked.'),
}


def _text(value, maximum, label, required=False):
    if not isinstance(value, str):
        raise ValueError(label + ' must be text')
    try:
        size = len(value.encode('utf-8'))
    except UnicodeError as error:
        raise ValueError(label + ' must be valid UTF-8') from error
    if size > maximum or (required and not value.strip()):
        raise ValueError(label + ' is empty or exceeds its UTF-8 byte limit')
    return value


def _integer(value, lower, upper, label):
    if type(value) is not int or not lower <= value <= upper:
        raise ValueError(f'{label} must be an integer in {lower}..{upper}')
    return value


def catalogue():
    return {'formats': [{'id': key, 'name': value[0], 'scope': value[1]} for key, value in FORMATS.items()],
            'scope': 'User-supplied prose and original fictional seeds; no source verification or rights grant.'}


def render(record):
    if not isinstance(record, dict) or set(record) - {'format', 'title', 'purpose', 'body', 'revision', 'sources', 'rights'}:
        raise ValueError('Supply the declared workpaper fields')
    kind = record.get('format', 'rawful')
    if not isinstance(kind, str) or kind not in FORMATS:
        raise ValueError('Choose a declared workpaper format')
    title = _text(record.get('title'), 160, 'Title', True)
    purpose = _text(record.get('purpose'), 1000, 'Purpose', True)
    body = _text(record.get('body'), 16000, 'Body', True)
    rights = _text(record.get('rights', 'Rights and reuse need separate review.'), 1000, 'Rights')
    revision = _integer(record.get('revision', 1), 1, 10000, 'Revision')
    sources = record.get('sources', [])
    if not isinstance(sources, list) or len(sources) > 16:
        raise ValueError('At most sixteen supplied source references')
    sources = [_text(item, 500, 'Source reference', True) for item in sources]
    prose = f'# {title}\n\n{FORMATS[kind][0]} · Revision {revision}\n\n'
    prose += f'The stated purpose of this workpaper is: {purpose}\n\n{body}\n\n'
    prose += FORMATS[kind][1] + '\n\n'
    prose += ('Supplied references: ' + '; '.join(sources) + '.' if sources else 'No supporting references were supplied.')
    prose += '\n\n' + rights + '\n\nThis finite draft is not automatically published or authenticated.\n'
    return {'format': kind, 'revision': revision, 'text': prose, 'bytes': len(prose.encode()),
            'sha256': hashlib.sha256(prose.encode()).hexdigest(), 'references_verified': False,
            'server_retention': False}


def fandom(seed, count=4):
    seed = _text(seed, 512, 'Seed', True)
    count = _integer(count, 1, 32, 'Count')
    places = ('garden', 'library', 'harbour', 'workshop', 'observatory', 'orchard', 'reading room', 'courtyard')
    tasks = ('mend a shared map', 'revise a song', 'study a returned letter', 'prepare an open exhibition',
             'document a lost recipe', 'review an old promise', 'teach a quiet lesson', 'share a useful discovery')
    records = []
    for index in range(count):
        digest = hashlib.sha256((seed + '\0' + str(index)).encode()).digest()
        text = f'In the {places[digest[0] % len(places)]}, a voluntary circle gathers to {tasks[digest[1] % len(tasks)]}. '
        text += 'Each participant can question the plan, choose an accessible role or leave the story.'
        records.append({'numer': digest.hex()[:16], 'index': index, 'text': text})
    return {'seed': seed, 'records': records, 'count': count, 'scope': 'Original fictional seed prompts; numer is a proposed local identifier label.',
            'franchise_rights_granted': False, 'communication_sent': False}


def map_svg(points):
    if not isinstance(points, list) or not 1 <= len(points) <= 64:
        raise ValueError('Supply 1..64 manually entered map points')
    plotted = []
    for point in points:
        if not isinstance(point, dict) or set(point) != {'label', 'latitude', 'longitude'}:
            raise ValueError('Each point needs label, latitude and longitude')
        label = _text(point['label'], 80, 'Point label', True)
        if any((ord(char) < 32 and char not in '\t\r\n') or ord(char) in (0xfffe, 0xffff) for char in label):
            raise ValueError('Point label contains an XML-forbidden character')
        lat, lon = point['latitude'], point['longitude']
        if any(type(value) not in (int, float) or (type(value) is float and not math.isfinite(value)) for value in (lat, lon)):
            raise ValueError('Coordinates must be finite numbers')
        if not -90 <= lat <= 90 or not -180 <= lon <= 180:
            raise ValueError('Coordinates outside latitude/longitude bounds')
        plotted.append({'label': label, 'latitude': lat, 'longitude': lon, 'x': (lon + 180) * 2, 'y': (90 - lat) * 2})
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 410" role="img">',
           '<title>Manually supplied coordinate plot</title><desc>Illustrative equirectangular grid; no live tracking or basemap.</desc>',
           '<rect width="720" height="410" fill="#0f1722"/>']
    for x in range(0, 721, 120):
        svg.append(f'<path d="M{x} 0V360" stroke="#334459"/>')
    for y in range(0, 361, 60):
        svg.append(f'<path d="M0 {y}H720" stroke="#334459"/>')
    for point in plotted:
        x, y = point['x'], point['y']
        anchor = 'end' if x > 540 else 'start'
        tx = max(4, min(716, x - 8 if anchor == 'end' else x + 8))
        svg.append(f'<circle cx="{x}" cy="{y}" r="4" fill="#98dfbd"/>')
        svg.append(f'<text x="{tx}" y="{max(14,min(350,y))}" text-anchor="{anchor}" fill="#edf1f1" font-size="12">{html.escape(point["label"])}</text>')
    svg.append('<text x="12" y="390" fill="#b1bfce" font-size="14">Supplied coordinates · illustrative grid · no live tracking</text></svg>')
    return {'svg': ''.join(svg), 'points': plotted, 'live_tracking': False, 'projection': 'equirectangular'}
