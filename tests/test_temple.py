import unittest
import hashlib
import json
import tempfile
from madrigal_lab import temple
from madrigal_lab.server import Lab

class TempleTests(unittest.TestCase):
    def test_default_order_independent_preferences_and_blueprint(self):
        a=temple.defaults();a['visible_panels'].clear();self.assertEqual(len(temple.defaults()['visible_panels']),7)
        plan=temple.blueprint();self.assertEqual([z['id'] for z in plan['zones']],['botanical','rural','urban','artificial','aggrestral','modder','ley-line'])
        self.assertFalse(plan['structural_approval']);self.assertFalse(plan['budget']['purchasing_enabled'])
        self.assertIsNone(plan['budget']['amount']);self.assertEqual(plan['settings']['profile_state'],'anonymous')

    def test_custom_profile_and_invalid_settings(self):
        plan=temple.blueprint({'primary_temple':'modder','palette':'urban','profile_state':'local-profile','profile_name':'My local plan','brand_preferences':['Supplied style'],'text_scale':120})
        self.assertEqual(plan['zones'][0]['id'],'modder');self.assertEqual(plan['interior']['brand_preferences'],['Supplied style'])
        for record in ({'text_scale':500},{'palette':'<script>'},{'visible_panels':['world']},{'brand_preferences':['']},{'mode':'lawful'},{'unknown':1}):
            with self.assertRaises(ValueError):temple.settings(record)

    def test_runtime_snapshot_hash_includes_custom_blueprint(self):
        with tempfile.TemporaryDirectory() as tmp:
            lab=Lab(tmp);result=lab.action('huwster-run',{'source':'world Demo\ntick 1','settings':{'primary_temple':'rural'}})
            digest=result.pop('quilt_sha256');self.assertEqual(digest,hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest())
            self.assertEqual(result['temple_blueprint']['zones'][0]['id'],'rural')
