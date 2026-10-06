import json
import unittest
from madrigal_lab import huwster
from madrigal_lab.server import Lab
import tempfile

SCRIPT='''world "Commons"
place wetland 4 6 habitat
actor steward 0 0 person
restore wetland 30
consume wetland 10
drive steward 2 3
signal steward "Review the baseline"
episode "Habitat return"
tick 3
franchise "Commons"
refranchise "Second season"
'''

class HuwsterTests(unittest.TestCase):
    def test_complete_base7_address_roundtrip_and_drafts(self):
        for index in (1,7,49,343,5764801):
            self.assertEqual(huwster.number(huwster.digits(index)),index)
            d=huwster.document(index);self.assertEqual(d['legal_status'],'unreviewed-draft')
            self.assertIn('Jurisdiction: not supplied',d['text']);self.assertIn(str(index).zfill(7),d['text'])
        self.assertEqual(huwster.decode(huwster.N)['revision'],49)
        for bad in (0,huwster.N+1,True):
            with self.assertRaises(ValueError):huwster.document(bad)

    def test_every_encounter_category_has_49_unique_documents_in_requested_contexts(self):
        for category in huwster.LABELS:
            for context in ('interactive','roleplay','jobrole'):
                docs=huwster.packet(category,context,subject='Fictional participant')
                self.assertEqual(len(docs),49);self.assertEqual(len({d['index'] for d in docs}),49)
                self.assertEqual({d['packet_index'] for d in docs},set(range(1,50)))
                self.assertTrue(all(d['subject_type']==category and d['context']==context for d in docs))

    def test_full_rank_grid(self):
        ranks=huwster.ranks();self.assertEqual(len(ranks),3087);self.assertEqual(len({r['id'] for r in ranks}),3087)
        for kind,types in huwster.TYPES.items():
            for typ in types:
                for context in huwster.CAREER_CONTEXTS:
                    subset=[r for r in ranks if (r['kind'],r['type'],r['context'])==(kind,typ,context)]
                    self.assertEqual({r['rank'] for r in subset},set(range(1,50)))

    def test_game_engine_motion_metrics_lore_and_default_documents(self):
        result=huwster.run(SCRIPT);self.assertEqual(result,huwster.run(SCRIPT))
        last=result['frames'][-1];self.assertEqual((last['actors'][0]['x'],last['actors'][0]['y']),(2,3))
        self.assertEqual(last['places'][0]['habitat'],50);self.assertEqual(last['places'][0]['consumption'],40)
        self.assertEqual(result['encounters'][0]['count'],49);self.assertEqual(len(result['signals']),1)
        self.assertEqual(result['episodes'][0]['number'],1);self.assertEqual(result['franchises'][1]['parent'],1)
        self.assertFalse(result['native_device_control']);self.assertEqual(result['default'],'ostar-rawful')

    def test_rejection_of_invalid_world_and_green_first_order(self):
        for source in ('world Test\nexec rm', 'world Test\nplace x 0 0 habitat\nconsume x 2',
                       'world Test\ndrive absent 0 0','world Test\nactor A 24 0 person',
                       'world Test\ntick 100\ntick 100\ntick 100','world Test\nactor A 0 0 person\nactor A 1 1 person'):
            with self.assertRaises(ValueError):huwster.run(source)

    def test_server_action_routes(self):
        with tempfile.TemporaryDirectory() as tmp:
            lab=Lab(tmp);self.assertEqual(lab.status()['name'],'Huwster Rasnikism')
            self.assertEqual(lab.action('huwster-run',{'source':SCRIPT})['default'],'ostar-rawful')
            self.assertEqual(len(lab.action('huwster-packet',{'category':'bot'})['documents']),49)
            self.assertEqual(lab.action('huwster-document',{'index':1})['index'],1)
