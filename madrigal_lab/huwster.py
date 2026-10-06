"""Huwster Rasnikism: rawful document architecture and finite ecological game compiler."""
import hashlib
import json
import shlex
from .papers import _text, _integer

TITLE='Huwster Rasnikism'
LABELS=('bot robot droid device pager mobile portable tablet laptop desktop mainframe hive colony suite room floor layer tier condominium condo name stamp bednob seal home house empire special-economic hamlet field ville bathway driveway byway roadway streetway carriageaway motorway interstateway town shop store mall person citizen people demographic individual group collective pal family fam tribe pace species creture nonindividual nongroup noncollective').split()
# Supplied alternate spellings retain their own addresses; no inferred physical identity.
CONTEXTS=('architecture','interactive','roleplay','jobrole','runtime','ecorestoration','franchise')
PURPOSES=('scope-and-parties','permissions-and-consent','resources-and-impact','design-and-obligations','evidence-and-review','change-and-remedy','closure-and-reuse')
FACETS=('identity','authority','ownership','participation','environment','operation','revision')
TYPES={
 'primitive':('mark','read','write','choose','step','signal','reference'),
 'composite':('parcel','household','workgroup','habitat','infrastructure','community','series'),
 'mechanic':('care','restraint','repair','truthfulness','stewardship','learning','advocacy')}
CAREER_CONTEXTS=('career','roleplay','jobrole')
N=7**8


def digits(index,width=8):
    _integer(index,1,7**width,'Document index');value=index-1;out=[0]*width
    for i in range(width-1,-1,-1):out[i]=value%7;value//=7
    return out


def number(ds):
    value=0
    for d in ds:value=value*7+d
    return value+1


def catalogue():
    return {'title':TITLE,'default':'ostar-rawful','publication_mode':'rawful-draft',
            'default_design':'systematic-ecorestoration','next_design':'incremental-environmentalism',
            'subjects':[{'number':i+1,'label':v} for i,v in enumerate(LABELS)],
            'contexts':list(CONTEXTS),'document_purposes':list(PURPOSES),'facets':list(FACETS),
            'document_space':N,'subject_slots':343,'revision_slots':49,'packet_documents':49,
            'rank_types':TYPES,'rank_contexts':list(CAREER_CONTEXTS),
            'ranks_per_type_and_context':49,'rank_records':len(CAREER_CONTEXTS)*sum(map(len,TYPES.values()))*49,
            'scope':'User-supplied and fictional scenarios; drafts are not legal approval, real career credentials or environmental measurements.'}


def decode(index):
    ds=digits(index);slot=ds[0]*49+ds[1]*7+ds[2]
    return {'index':index,'address':'.'.join(str(d+1) for d in ds),'slot':slot,
            'subject_type':LABELS[slot] if slot<len(LABELS) else f'unassigned-subject-{slot+1:03d}',
            'context':CONTEXTS[ds[3]],'purpose':PURPOSES[ds[4]],'facet':FACETS[ds[5]],
            'revision':ds[6]*7+ds[7]+1,'packet_index':ds[4]*7+ds[5]+1}


def document(index,subject='Unspecified subject',project=TITLE):
    _text(subject,160,'Subject',True);_text(project,160,'Project',True);r=decode(index)
    purpose=r['purpose'];facet=r['facet']
    tasks={
     'scope-and-parties':'Identify the proposed parties, defined terms, activity boundary and exclusions. No person is treated as a party solely because a simulation encounters their category.',
     'permissions-and-consent':'Record the required authorisation, voluntary participation, withdrawal route and actual evidence of permission. An unchecked field is unresolved.',
     'resources-and-impact':'Record baseline land, habitat, water, materials and stated social needs. Compare restoration at system scale with incremental consumption changes using supplied evidence.',
     'design-and-obligations':'Describe the proposed architecture, responsibilities, dependencies, resources and acceptance criteria. Distinguish a design proposal from a binding undertaking.',
     'evidence-and-review':'List the evidence relied upon, its origin, uncertainty and the reviewer qualified for the relevant question. A generated file is not independent verification.',
     'change-and-remedy':'Record proposed changes, affected interests, correction procedures, limits and dispute routes. Preserve earlier versions and describe remedies for review.',
     'closure-and-reuse':'Record completion conditions, unresolved obligations, retention, return of resources and proposed reuse or franchise rights. Rights require evidence rather than a title.'}
    focuses={
     'identity':'Identify the record subject and distinguish a display name from authenticated identity.',
     'authority':'State the actor and the evidence supporting each claimed power; unknown authority remains unknown.',
     'ownership':'Record the source, owner assertion and licence or rights evidence for each relevant asset.',
     'participation':'Record who may participate, how agreement is documented and how a participant may leave.',
     'environment':'Define the ecological boundary, baseline, proposed regenerative intervention and measurable indicators.',
     'operation':'State the engineering method, operating bounds, dependencies, signals and the conditions of inability.',
     'revision':'Preserve the version chain, change reason, reviewer and the conditions for adopting a revision.'}
    text=(f"# {project} — Ostar Rawful draft {index:07d}\n\n"
          f"Address {r['address']}; subject category {r['subject_type']}; context {r['context']}; revision {r['revision']}; packet document {r['packet_index']}/49.\n\n"
          f"## Supplied subject\n\n{subject}\n\n## Document purpose: {purpose}\n\n{tasks[purpose]}\n\n"
          f"## Review facet: {facet}\n\n{focuses[facet]}\n\n"
          "## Engineering sequence\n\nStart with a systematic ecorestoration or regenerative-design proposal, including the shared system and its dependencies. Then document incremental environmentalism or green-consumerism choices within that proposal. Compare the scopes rather than assuming either achieves an outcome. Record baseline, target, observed result and remaining uncertainty.\n\n"
          "## Relevant review fields\n\nJurisdiction: not supplied. Parties and authority: not verified. Rights and consent evidence: not supplied. Baseline and calibration: not supplied. Responsibilities and acceptance criteria: to be completed. Qualified reviewer and date: not supplied. Adoption, signature and legal effectiveness: not established. Corrections and outstanding obligations: to be recorded.\n\n"
          "## Inability and status\n\nThis is generated drafting paperwork. It does not grant powers, issue a licence, establish compliance, create employment or confer consent. Missing factual or legal evidence prevents a claim of approval; obtain the relevant evidence and qualified review before adoption. Rawful identifies recorded construction, not lawful certification. An unassigned category is a reserved drafting slot, not an invented encountered person or object.\n")
    return {**r,'subject':subject,'text':text,'sha256':hashlib.sha256(text.encode()).hexdigest(),
            'legal_status':'unreviewed-draft','default':'ostar-rawful'}


def packet(subject_type,context='interactive',subject='Unspecified subject',revision=1):
    if subject_type not in LABELS or context not in CONTEXTS:raise ValueError('Choose a declared subject category and context')
    _integer(revision,1,49,'Revision');slot=LABELS.index(subject_type);r=revision-1
    prefix=[slot//49,(slot//7)%7,slot%7,CONTEXTS.index(context)]
    return [document(number(prefix+[a,b,r//7,r%7]),subject) for a in range(7) for b in range(7)]


def ranks():
    return [{'id':f'{kind}:{typ}:{context}:{a*7+b+1:02d}','kind':kind,'type':typ,'context':context,
             'rank':a*7+b+1,'stage':PURPOSES[a],'facet':FACETS[b],
             'scope':'Simulated role progression; not a credential or employment assignment.'}
            for kind,types in TYPES.items() for typ in types for context in CAREER_CONTEXTS
            for a in range(7) for b in range(7)]


def compile_script(source):
    _text(source,16000,'World script',True)
    instructions=[]
    for line_no,line in enumerate(source.splitlines(),1):
        try:parts=shlex.split(line,comments=True)
        except ValueError as e:raise ValueError(f'Line {line_no}: {e}') from None
        if not parts:continue
        op,args=parts[0],parts[1:]
        counts={'world':1,'place':4,'actor':4,'drive':3,'signal':2,'restore':2,'consume':2,'tick':1,'episode':1,'franchise':1,'refranchise':1}
        if op not in counts or len(args)!=counts[op]:raise ValueError(f'Line {line_no}: unknown operation or wrong argument count')
        if any(len(arg)>160 for arg in args):raise ValueError(f'Line {line_no}: argument exceeds 160 characters')
        numeric={'place':(1,2),'actor':(1,2),'drive':(1,2),'restore':(1,),'consume':(1,),'tick':(0,)}.get(op,())
        for i in numeric:
            try:args[i]=int(args[i])
            except ValueError:raise ValueError(f'Line {line_no}: expected an integer') from None
            bound=100 if op in ('restore','consume','tick') else 23
            _integer(args[i],0 if op!='tick' else 1,bound,f'Line {line_no} argument')
        if op=='actor' and args[3] not in LABELS:raise ValueError(f'Line {line_no}: unknown actor category')
        if op=='place' and args[3] not in ('habitat','home','work','road','shop'):raise ValueError(f'Line {line_no}: unknown place use')
        instructions.append({'op':op,'args':args,'line':line_no})
        if len(instructions)>512:raise ValueError('At most 512 world instructions')
    if not instructions or instructions[0]['op']!='world' or sum(i['op']=='world' for i in instructions)!=1:
        raise ValueError('Start with exactly one world declaration')
    return {'format':'huwster-world-bytecode','version':1,'instructions':instructions,'source_sha256':hashlib.sha256(source.encode()).hexdigest()}


def run(source):
    program=compile_script(source);places={};actors={};frames=[];signals=[];episodes=[];franchises=[];clock=0;encounters=[];restored=set()
    def encounter(name,category):
        packets={context:[d["index"] for d in packet(category,context,subject=name)] for context in ("interactive","roleplay","jobrole")}
        encounters.append({"name":name,"category":category,"document_indexes":packets["interactive"],"packets":packets,"count":49,"total_references":147})
    def frame():
        if len(frames)>=257:raise ValueError('Simulation exceeds 256 ticks plus its initial frame')
        frames.append({'tick':clock,'actors':[dict(a) for a in actors.values()],
                       'places':[dict(p) for p in places.values()]})
    for instruction in program['instructions']:
        op,args=instruction['op'],instruction['args']
        if op=='world':title=args[0]
        elif op=='place':
            name,x,y,use=args
            if name in places or len(places)>=64:raise ValueError('Duplicate place or more than 64 places')
            places[name]={'name':name,'x':x,'y':y,'use':use,'habitat':20,'water':20,'consumption':50}
            encounter(name,{'habitat':'field','home':'home','work':'room','road':'roadway','shop':'shop'}[use])
        elif op=='actor':
            name,x,y,category=args
            if name in actors or len(actors)>=32:raise ValueError('Duplicate actor or more than 32 actors')
            actors[name]={'name':name,'x':x,'y':y,'category':category,'target':[x,y]}
            # Every simulated encounter receives all 49 numbered drafting references by default.
            encounter(name,category)
        elif op=='drive':
            if args[0] not in actors:raise ValueError('Drive references an unknown actor')
            actors[args[0]]['target']=args[1:]
        elif op=='signal':
            if args[0] not in actors and args[0] not in places:raise ValueError('Signal references an unknown actor or place')
            signals.append({'subject':args[0],'text':args[1],'tick':clock})
        elif op in ('restore','consume'):
            if args[0] not in places:raise ValueError('Ecological operation references an unknown place')
            p=places[args[0]];amount=args[1]
            if op=='restore':
                restored.add(args[0]);p['habitat']=min(100,p['habitat']+amount);p['water']=min(100,p['water']+amount)
            else:
                if args[0] not in restored:raise ValueError('First record a systematic restoration intervention for this place, then model incremental consumption')
                p['consumption']=max(0,p['consumption']-amount)
        elif op=='tick':
            if not frames:frame()
            for _ in range(args[0]):
                clock+=1
                for a in actors.values():
                    for i,key in enumerate(('x','y')):a[key]+=(a['target'][i]>a[key])-(a['target'][i]<a[key])
                frame()
        elif op=='episode':episodes.append({'title':args[0],'tick':clock,'number':len(episodes)+1})
        elif op in ('franchise','refranchise'):
            franchises.append({'kind':op,'title':args[0],'parent':len(franchises) if op=='refranchise' else None,'rights':'unreviewed-proposal'})
    if not frames or frames[-1]['actors']!=list(actors.values()) or frames[-1]['places']!=list(places.values()):frame()
    result={'title':title,'default':'ostar-rawful','design_sequence':['systematic-ecorestoration','incremental-environmentalism'],
            'program':program,'frames':frames,'signals':signals,'episodes':episodes,'franchises':franchises,'encounters':encounters,
            'scope':'Toy life-simulation game. Scores are rule-based indicators, not physical measurements or social predictions.',
            'native_device_control':False,'legal_status':'drafts-only','finalised':'bounded-run-completed'}
    result['quilt_sha256']=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return result
