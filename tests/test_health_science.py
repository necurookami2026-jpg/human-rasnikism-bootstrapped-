import unittest
from fractions import Fraction
from madrigal_lab import health_science as h

class HealthScienceTests(unittest.TestCase):
 def test_photon_units_and_exact_constants(self):
  r=h.photon('500');self.assertEqual(Fraction(r['frequency_hz']),599584916000000)
  self.assertEqual(Fraction(r['photon_energy_j']),Fraction('6.62607015e-34')*599584916000000)
  for value in [True,0,-1,'nan','inf',[],1e10]:
   with self.assertRaises(ValueError):h.photon(value)
 def test_all_modules_and_editions_no_certification(self):
  for module in h.MODULES:
   for edition in h.EDITIONS:
    r=h.workpaper({'module':module,'edition':edition,'consent':True,'notes':'<script>inert</script>'})
    self.assertFalse(r['clinical_approval']);self.assertFalse(r['legal_certification']);self.assertFalse(r['retained_on_server']);self.assertIn('inability',r['response'])
 def test_rejections_and_calculation(self):
  for record in [{},{'module':[]},{'module':'actinology','consent':1},{'module':'actinology','consent':True,'notes':'x'*8001},{'module':'roperist-medical','consent':True,'wavelength_nm':500}]:
   with self.assertRaises(ValueError):h.workpaper(record)
  self.assertIn('calculation',h.workpaper({'module':'actinology','consent':True,'wavelength_nm':'500'}))
