"""Educational health workpapers and unit-explicit light calculations."""
from fractions import Fraction

EDITIONS=('rawful','raw','law','lawful')
MODULES={
 'roperist-medical':{'title':'Roperist basic scientific medical','definition':'Author-supplied roperist label; clinical meaning unspecified.','fields':['observation','time and units','measurement method','uncertainty','questions for clinician'], 'limits':'Cannot diagnose, triage or prescribe.'},
 'ostar-nutraceutical':{'title':'Ostar basic scientific nutraceutical','definition':'Supplement evidence and label review.','fields':['ingredient and label quantity','claimed purpose','study population and source','possible interactions to ask pharmacist about','review date'], 'limits':'No inferred efficacy, personalized dose or interaction clearance. Supplements may cause harm.'},
 'therapist-therapy':{'title':'Therapist basic scientific therapy','definition':'Voluntary reflection and professional-session preparation.','fields':['voluntary goal','self-reported experience','context','preferred support and boundaries','questions for qualified therapist'], 'limits':'Not a therapist, diagnostic assessment or crisis service.'},
 'actinology':{'title':'Basic scientific actinology','definition':'Study of radiation and light; this implementation calculates vacuum photon quantities only.','fields':['wavelength in nanometres','medium assumption','measurement uncertainty','instrument/source','questions for radiation specialist'], 'limits':'No UV exposure time, therapeutic irradiation, dosimetry or ionizing-radiation safety decision.'}}
GUIDES={'raw':'Preserve supplied observations without validating them.', 'rawful':'Organize observations, uncertainty and evidence gaps.', 'law':'Record jurisdiction, consent and applicable-rule questions for qualified review.', 'lawful':'Record unresolved compliance questions; never certify legality or clinical approval.'}

def catalogue():
 return {'title':'Huwster Rasnikism — basic health science','modules':MODULES,'editions':GUIDES,'scope':'Educational workpapers, not clinical care or legal certification.', 'privacy':'Processed locally in memory; no server persistence or transmission to care providers. Downloads may contain sensitive information.', 'sources':[{'title':'NIH Office of Dietary Supplements fact sheets','url':'https://ods.od.nih.gov/factsheets/list-all/'},{'title':'NIMH psychotherapies','url':'https://www.nimh.nih.gov/health/topics/psychotherapies'},{'title':'BIPM SI Brochure','url':'https://www.bipm.org/en/publications/si-brochure'}], 'source_status':'Reference links, not fetched clinical evidence.'}

def photon(wavelength_nm):
 if isinstance(wavelength_nm,bool) or not isinstance(wavelength_nm,(str,int,float)):raise ValueError('Supply a numeric wavelength in nm')
 try:
  if len(str(wavelength_nm))>64:raise ValueError()
  nm=Fraction(str(wavelength_nm))
 except (ValueError,ZeroDivisionError):raise ValueError('Invalid wavelength') from None
 if not Fraction(1,1000)<=nm<=10**9:raise ValueError('Educational wavelength range is 0.001..1e9 nm')
 metres=nm/Fraction(10**9);frequency=Fraction(299792458)/metres
 energy=Fraction('6.62607015e-34')*frequency
 return {'wavelength_nm':str(nm),'frequency_hz':str(frequency),'photon_energy_j':str(energy),'frequency_hz_approx':float(frequency),'photon_energy_j_approx':float(energy),'assumption':'Vacuum; exact SI c and h. Rational arithmetic is exact for the supplied value, not measurement certainty.'}

def workpaper(record):
 if not isinstance(record,dict) or set(record)-{'module','edition','notes','evidence','consent','wavelength_nm'}:raise ValueError('Unknown workpaper fields')
 module=record.get('module');edition=record.get('edition','rawful')
 if not isinstance(module,str) or module not in MODULES or not isinstance(edition,str) or edition not in EDITIONS:raise ValueError('Unknown module or edition')
 if record.get('consent') is not True:raise ValueError('Voluntary consent required; no record retained')
 for key in ('notes','evidence'):
  if not isinstance(record.get(key,''),str) or len(record.get(key,''))>8000:raise ValueError('Notes and evidence must be text up to 8000 characters')
 if module!='actinology' and 'wavelength_nm' in record:raise ValueError('Wavelength belongs only to actinology')
 result={'module':module,'edition':edition,'guide':GUIDES[edition],'notes':record.get('notes',''),'evidence':record.get('evidence',''),'fields':MODULES[module]['fields'],'limits':MODULES[module]['limits'],'evidence_status':'User-supplied, not verified','retained_on_server':False,'clinical_approval':False,'legal_certification':False}
 if module=='actinology' and 'wavelength_nm' in record:result['calculation']=photon(record['wavelength_nm'])
 result['response']={
 'ahow / hot':'Record a bounded observation, its method, units and uncertainty.',
 'awho / tho':'The consenting user prepares this record; qualified professionals assess clinical questions.',
 'awhat / that':MODULES[module]['definition'],
 'awhen / then':'Record the observation date and planned review; this software schedules no care.',
 'awhere / there':'Local workbench memory and an explicit optional download.',
 'awhy / thy':'Make evidence gaps visible rather than infer unsupported outcomes.',
 'inability':MODULES[module]['limits']+' These limits follow from absent clinical examination, validated clinical decision tools and professional oversight.'}
 return result
