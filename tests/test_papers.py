import unittest
import xml.etree.ElementTree as ET
from madrigal_lab import papers


class PapersTests(unittest.TestCase):
    def test_all_prose_formats_and_retained_inputs(self):
        record={'title':'Review','purpose':'Preserve a local account.','body':'First account.\n\nA later interpretation.','sources':['An unverified reference.']}
        for kind in papers.FORMATS:
            result=papers.render(dict(record,format=kind))
            self.assertIn(record['body'],result['text'])
            self.assertIn(record['purpose'],result['text'])
            self.assertFalse(result['references_verified'])
            self.assertFalse(result['server_retention'])
        with self.assertRaises(ValueError):papers.render(dict(record,revision=True))
        with self.assertRaises(ValueError):papers.render(dict(record,body='x'*16001))
        with self.assertRaises(ValueError):papers.render(dict(record,format='unknown'))

    def test_seed_prompts_are_repeatable_and_finite(self):
        result=papers.fandom('circle',32)
        self.assertEqual(result,papers.fandom('circle',32))
        self.assertEqual(len({r['numer'] for r in result['records']}),32)
        self.assertNotEqual(result,papers.fandom('another',32))
        self.assertFalse(result['communication_sent'])
        for count in (True,0,33):
            with self.assertRaises(ValueError):papers.fandom('circle',count)

    def test_map_coordinates_escaping_and_bounds(self):
        result=papers.map_svg([{'label':'<script> & map','latitude':0,'longitude':0}])
        ET.fromstring(result['svg'])
        self.assertNotIn('<script>',result['svg'])
        self.assertEqual((result['points'][0]['x'],result['points'][0]['y']),(360,180))
        self.assertFalse(result['live_tracking'])
        for coordinate in (True,float('nan'),float('inf'),91,10**400):
            with self.assertRaises(ValueError):papers.map_svg([{'label':'Point','latitude':coordinate,'longitude':0}])
        for label in ('Point\x00','Point\ufffe'):
            with self.assertRaises(ValueError):papers.map_svg([{'label':label,'latitude':0,'longitude':0}])
