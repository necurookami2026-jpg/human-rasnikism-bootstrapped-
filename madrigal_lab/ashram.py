"""Edition-specific symbolic Ashram grammar and disjoint address algebra."""
import argparse
import json
import re

FORMS = {'0': ('A', 'benevolent'), '1': ('A', 'amalevolent'),
         '2': ('B', 'malevolent'), '3': ('B', 'abenevolent')}
OPERATIONS = ('counteramakkakah', 'counterantonymmakkakah', 'aantonymmakkakah', 'makkakah')
KINDS = ('totem', 'token')
TERMS = (
 ('ashram', 'The edition-specific symbolic practice space containing disjoint A and B namespaces.'),
 ('existencial form', 'A declared base-four symbol, not a classification of people or a measured ontology.'),
 ('A', 'Benevolent-side namespace; admits form 0 or 1.'),
 ('B', 'Malevolent-side namespace; admits form 2 or 3.'),
 ('benevolent', 'Form 0: constructive intention in namespace A.'),
 ('amalevolent', 'Form 1: non-harm restraint in namespace A; a provisional authored label.'),
 ('malevolent', 'Form 2: adverse intention in fictional namespace B.'),
 ('abenevolent', 'Form 3: withheld constructive support in fictional namespace B; a provisional label.'),
 ('primitive', 'A symbolic leaf addressed by eight ordered base-seven positions.'),
 ('amplification', 'Eight independent seven-way choices, yielding 7^8 addresses per form and kind.'),
 ('exponential squared', 'Author-confirmed rule: ordered pairs of eight-position addresses, giving (7^8)^2.'),
 ('punnitsquared', 'Author spelling for the ordered pair grid; an analogy to a Punnett square, not genetics.'),
 ('totem', 'A symbolic narrative emblem in its own type namespace.'),
 ('token', 'A formal reference in its own type namespace; never implicitly a totem.'),
 ('segregation', 'Type and namespace separation of symbolic records; no rule about human populations.'),
 ('counteramakkakah', 'Within this edition, inspect an existing record without changing its side or kind.'),
 ('counterantonymmakkakah', 'Within this edition, review a proposed reversal and retain its origin.'),
 ('aantonymmakkakah', 'Within this edition, propose reframing or retirement within the same namespace.'),
 ('makkakah', 'Within this edition, record maintenance within the same namespace.'),
 ('parable', 'One of seven explanatory mechanics assigned to each side; a story index, not a new primitive.'),
 ('yin', 'A-side totem label in this edition only.'), ('yan', 'B-side counterpart label paired with yin in this edition only.'),
 ('ying', 'Separate A-side totem label; not silently merged with yin.'), ('yang', 'Separate B-side counterpart label paired with ying.'),
 ('dao', 'A-side example label in this edition only.'), ('tao', 'B-side counterpart example label in this edition only; not a historical claim.'),
 ('power', 'A named possibility for constructive action; realised effects require evidence.'),
 ('ability', 'A task-specific skill evidenced by demonstration.'),
 ('capacity', 'A stated available resource or bounded potential.'),
 ('advocacy', 'Support for a declared constructive interest with permission and review.'),
 ('care', 'A-side mechanic: attend to a supplied need and its limits.'),
 ('restraint', 'A-side mechanic: decline an unsupported or harmful transition.'),
 ('repair', 'A-side mechanic: correct a record while retaining its history.'),
 ('truthfulness', 'A-side mechanic: distinguish evidence, inference and unknown facts.'),
 ('stewardship', 'A-side mechanic: account for entrusted resources.'),
 ('learning', 'A-side mechanic: revise a method against stated observations.'),
 ('consensual advocacy', 'A-side mechanic: support a voluntary request without claiming authority over others.'),
)


def specification():
    return {'format':'rasniki-ashram-specification','version':1,'status':'provisional-symbolic-model',
            'terms':[{'number':i,'term':term,'definition':definition} for i,(term,definition) in enumerate(TERMS,1)],
            'forms':[{'digit':int(d),'side':s,'label':label} for d,(s,label) in FORMS.items()],
            'kinds':list(KINDS),'operations':list(OPERATIONS),
            'amplification':{'chosen_interpretation':'(7^8)^2','author_confirmation':'confirmed in this session',
                             'depth':8,'radix':7,'addresses_per_form_and_kind':7**8,
                             'ordered_pairs_per_form_and_kind':7**16,
                             'parable_variants_per_form_and_kind':7**17,
                             'all_four_forms_two_kinds_parable_variants':8*7**17,
                             'alternative_repeated_squaring':'7^(2^7) = 7^128; not the selected address grammar'},
            'separation':'Every pair has one side, one form and one kind. Cross-side and cross-kind composition is refused.',
            'materialized_primitives':0,'scope':'Finite symbolic address algebra, not a scientific claim about reality or people.'}


def address_rank(address):
    if not isinstance(address,(list,tuple)) or len(address)!=8 or any(type(d) is not int or not 0<=d<7 for d in address):
        raise ValueError('An address requires exactly eight integer digits 0..6')
    rank=0
    for digit in address:rank=7*rank+digit
    return rank


def parse(text):
    if not isinstance(text,str) or len(text)>256:raise ValueError('Ashram statements require text of at most 256 characters')
    pattern=r'(A|B):([0-3]) (totem|token) ('+'|'.join(OPERATIONS)+r') ([0-6](?:\.[0-6]){7}) \* ([0-6](?:\.[0-6]){7}) parable ([1-7])'
    match=re.fullmatch(pattern,text)
    if not match:raise ValueError('Use SIDE:FORM KIND OP eight.base7.digits * eight.base7.digits parable 1..7')
    side,form,kind,op,left,right,parable=match.groups()
    if FORMS[form][0]!=side:raise ValueError('Form does not belong to the declared side; no cross-side coercion exists')
    a=[int(x) for x in left.split('.')];b=[int(x) for x in right.split('.')]
    return {'side':side,'form':int(form),'kind':kind,'operation':op,'left':a,'right':b,
            'pair_rank':address_rank(a)*7**8+address_rank(b),'parable':int(parable),
            'status':'symbolic-record-only','executed_real_world_action':False}


def compose(first,second):
    # Validate by rebuilding the canonical grammar, rather than trusting a caller's tags.
    records=[]
    for record in (first,second):
        try:
            canonical=f"{record['side']}:{record['form']} {record['kind']} {record['operation']} "+'.'.join(map(str,record['left']))+' * '+'.'.join(map(str,record['right']))+f" parable {record['parable']}"
        except (KeyError,TypeError):raise ValueError('Provide two complete Ashram records') from None
        records.append(parse(canonical))
    if any(records[0][key]!=records[1][key] for key in ('side','form','kind')):
        raise ValueError('Composition requires the same side, form and kind; symbolic primitives are not mixed')
    return {'side':records[0]['side'],'form':records[0]['form'],'kind':records[0]['kind'],
            'records':records,'status':'symbolic-composition-only'}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--statement');args=parser.parse_args()
    try:print(json.dumps(parse(args.statement) if args.statement is not None else specification(),indent=2))
    except ValueError as error:parser.exit(2,str(error)+'\n')

if __name__=='__main__':main()
