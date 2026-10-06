import unittest
from madrigal_lab.ashram import specification,parse,compose,address_rank

class AshramTests(unittest.TestCase):
    def sentence(self,side='A',form=0,kind='token',digits='0.0.0.0.0.0.0.0'):
        return f'{side}:{form} {kind} makkakah {digits} * {digits} parable 1'

    def test_all_forms_and_kinds_and_extreme_ranks(self):
        for side,forms in [('A',(0,1)),('B',(2,3))]:
            for form in forms:
                for kind in ('totem','token'):
                    r=parse(self.sentence(side,form,kind));self.assertFalse(r['executed_real_world_action']);self.assertEqual(r['pair_rank'],0)
        r=parse(self.sentence(digits='6.6.6.6.6.6.6.6'));self.assertEqual(r['pair_rank'],7**16-1)
        self.assertEqual(address_rank([1,0,0,0,0,0,0,0]),7**7)

    def test_separation_refuses_cross_side_form_kind_and_forged_records(self):
        a=parse(self.sentence());self.assertEqual(len(compose(a,a)['records']),2)
        for b in [parse(self.sentence('B',2)),parse(self.sentence(form=1)),parse(self.sentence(kind='totem'))]:
            with self.assertRaises(ValueError):compose(a,b)
        b=dict(a,side='B')
        with self.assertRaises(ValueError):compose(a,b)
        for statement in [self.sentence('A',2),self.sentence(digits='7.0.0.0.0.0.0.0'),self.sentence().replace('parable 1','parable 8'),self.sentence().replace('makkakah','invented')]:
            with self.assertRaises(ValueError):parse(statement)
        with self.assertRaises(ValueError):address_rank([True]*8)

    def test_counts_and_sequential_unique_lexicon(self):
        s=specification();rows=s['terms'];self.assertEqual([r['number'] for r in rows],list(range(1,len(rows)+1)))
        self.assertEqual(len(set(r['term'] for r in rows)),len(rows));self.assertEqual(s['materialized_primitives'],0)
        self.assertEqual(s['amplification']['ordered_pairs_per_form_and_kind'],33232930569601)
        self.assertEqual(s['amplification']['all_four_forms_two_kinds_parable_variants'],8*7**17)
