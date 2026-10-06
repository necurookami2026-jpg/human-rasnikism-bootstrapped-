"""Validated launch preferences and schematic temple blueprints; no account service."""
import copy
import html
import json
import re

TEMPLES=(
 ('botanical','Botanical temple','primary','Planting court, quiet study, water stewardship and accessible circulation.'),
 ('rural','Rural temple','secondary','Low-density practice rooms, repair workshop and shared landscape.'),
 ('urban','Urban temple','tertiary','Compact shared rooms, transit-facing entry and acoustic buffers.'),
 ('artificial','Artificial temple','quaternary','Explicitly simulated modular structure and instrumented service rooms.'),
 ('aggrestral','Aggrestral temple','quinary','Proposed cultivation and landscape template; supplied term remains provisional.'),
 ('modder','Modder temple','sexenary','Adaptable maker rooms and reversible workshop layouts.'),
 ('ley-line','Ley line temple','septenary','Symbolic connecting paths; no verified energy-line or spiritual effects are asserted.'))
PANELS=('blueprint','settings','world','paperwork','ranks','lore','evidence')
TERMS=('counteramakkakah','counterantonymmakkakah','aantonymmakkakah','makkah','ainsuitable','suitable','hen','apen','nomic','henapenall')
PALETTES={'botanical':('#102820','#98dfbd','#e1c788'),'rural':('#282015','#dfc59b','#a9cb9b'),'urban':('#142431','#a3cbdc','#dfce98')}
DEFAULTS={'version':1,'mode':'ostar-rawful','persona':'Rasniki Hoppit Huwster Demihuman',
          'profile_name':'','profile_state':'anonymous','primary_temple':'botanical','palette':'botanical',
          'density':'comfortable','text_scale':100,'hud_layout':'standard','visible_panels':list(PANELS),
          'planning_budget':'unset','budget_amount':None,'brand_preferences':[],
          'interior_style':'ancient-jungle','botanical_material':'artificial-botanicals','interior_detail':'rich',
          'service_orientation':'client-first','great_expenditure':'layered-multientity-artistry',
          'interior_review':'maximum-documented-counter-review','settings_terms':list(TERMS)}


def defaults():return copy.deepcopy(DEFAULTS)


def settings(record=None):
    if record is None:return defaults()
    if not isinstance(record,dict) or set(record)-set(DEFAULTS):raise ValueError('Unknown launch-settings field')
    out=defaults();out.update(copy.deepcopy(record))
    enums={'primary_temple':tuple(x[0] for x in TEMPLES),'palette':tuple(PALETTES),
           'density':('comfortable','compact'),'hud_layout':('standard','focus'),
           'planning_budget':('unset','balanced','minimal'),
           'interior_style':('ancient-jungle','coastal-forest','valley-forest','alpine'),
           'interior_detail':('rich','standard','minimal'),
           'service_orientation':('client-first','owner-directed'),
           'profile_state':('anonymous','local-profile')}
    for key,values in enums.items():
        if not isinstance(out[key],str) or out[key] not in values:raise ValueError('Invalid '+key)
    if out['botanical_material']!='artificial-botanicals' or out['great_expenditure']!='layered-multientity-artistry':raise ValueError('Unsupported material or great-expenditure setting')
    if type(out['version']) is not int or out['version']!=1 or out['mode']!='ostar-rawful' or out['persona']!=DEFAULTS['persona'] or out['interior_review']!=DEFAULTS['interior_review'] or out['settings_terms']!=list(TERMS):raise ValueError('Unsupported settings version or changed canonical defaults')
    if type(out['text_scale']) is not int or not 85<=out['text_scale']<=140:raise ValueError('Text scale must be an integer 85..140')
    if not isinstance(out['profile_name'],str) or len(out['profile_name'])>80:raise ValueError('Profile name requires at most 80 characters')
    panels=out['visible_panels']
    if not isinstance(panels,list) or any(type(p) is not str or p not in PANELS for p in panels) or len(panels)!=len(set(panels)) or 'settings' not in panels:raise ValueError('Panels must be unique declared names and include settings')
    brands=out['brand_preferences']
    if not isinstance(brands,list) or len(brands)>16 or any(not isinstance(b,str) or not b.strip() or len(b)>80 for b in brands):raise ValueError('At most 16 supplied brand/style names, each 1..80 characters')
    amount=out['budget_amount']
    if amount is not None and (type(amount) is not int or not 0<=amount<=1000000000):raise ValueError('Optional planning amount requires an integer 0..1000000000')
    if out['profile_state']=='anonymous':out['profile_name']=''
    return out


def catalogue():
    return {'title':'Huwster Rasnikism — temple HUD','defaults':defaults(),
            'temples':[{'id':i,'name':n,'priority':j+1,'ordinal':o,'scope':s} for j,(i,n,o,s) in enumerate(TEMPLES)],
            'panels':list(PANELS),'palettes':list(PALETTES),
            'interior_styles':['ancient-jungle','coastal-forest','valley-forest','alpine'],
            'terms':[{'term':t,'status':'implemented-setting-label' if t in TERMS[:6] else 'provisional-label-not-an-executable-guarantee'} for t in TERMS],
            'spelling_aliases':{'counteramakakah':'counteramakkakah','counterantonymmakkah':'counterantonymmakkakah'},
            'personalisation':'Explicitly saved local browser profile; no authenticated account login or Amazon purchase-history access.',
            'scope':'Conceptual layout and fictional persona, not a structural engineering approval.'}


def blueprint(record=None):
    prefs=settings(record);primary=prefs['primary_temple'];ordered=sorted(TEMPLES,key=lambda t:t[0]!=primary)
    boxes=[(2,2,8,6),(12,2,10,5),(12,9,10,5),(2,10,8,5),(2,17,6,5),(10,17,6,5),(18,17,4,5)]
    zones=[{'id':t[0],'name':t[1],'rank':index+1,'x':box[0],'y':box[1],'width':box[2],'height':box[3],'scope':t[3]} for index,(t,box) in enumerate(zip(ordered,boxes))]
    bg,accent,gold=PALETTES[prefs['palette']]
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 760" role="img" aria-label="Conceptual temple blueprint"><rect width="720" height="760" fill="{bg}"/><text x="30" y="35" fill="{accent}" font-size="22">Huwster temple blueprint</text><text x="30" y="60" fill="{gold}" font-size="13">Schematic grid units; not construction dimensions or approval</text>']
    for z in zones:
        x,y,w,h=z['x']*28,z['y']*28+70,z['width']*28,z['height']*28
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{accent}" stroke-width="2"/><text x="{x+8}" y="{y+22}" fill="{gold}" font-size="13">{z["rank"]}. {html.escape(z["name"])}</text>')
    parts.append(f'<path d="M 308 90 V 715 M 38 518 H 660" stroke="{gold}" stroke-dasharray="7 5" fill="none"/><text x="30" y="744" fill="{accent}" font-size="12">Access and service paths require site-specific design review.</text></svg>')
    return {'settings':prefs,'zones':zones,'svg':''.join(parts),'units':'conceptual-grid','structural_approval':False,
            'interior':{'likeness':'maximum documented counteramakkakah and counterantonymmakkakah review',
                        'materials':['artificial botanicals','repairable furnishings','simulated daylight','reusable scenery'],
                        'style':prefs['interior_style'],'detail':prefs['interior_detail'],
                        'service_orientation':prefs['service_orientation'],
                        'great_expenditure':{'meaning':'layered-multientity-artistry','layers':['primitive','composite','mechanic','chronological','structural','architectural'], 'fashion':['paisley chic','Victorian Gothic','steampunk'], 'ashram_contrast':{'A':'benevolent symbolic motif','B':'malevolent symbolic motif','mix_primitives':False}, 'colour_compatibility':'coordinated palette with distinct motifs; client-customizable', 'nomichenpenall':'author-supplied client compatibility label; no scientific definition supplied'},
                        'design_brief':'Products serve the supplied client brief; if absent, use the supplied owner brief. No purchase or environmental benefit is inferred.',
                        'brand_preferences':prefs['brand_preferences'],'brands_verified':False},
            'budget':{'preset':prefs['planning_budget'],'amount':prefs['budget_amount'],'currency':'not supplied','purchasing_enabled':False}}
