(function(root){
'use strict';
const templates=[
{id:'greeting',name:'Greeting',source:'mark r0 65\nsignal r0 0 1\nsignal r0 2 1\n',input:[],drivers:[],description:'Outputs A; change 65 to another byte.'},
{id:'echo',name:'Input echo',source:'signal r0 1 0\nsignal r0 0 1\nsignal r0 2 1\n',input:[65],drivers:[],description:'Reads and outputs one byte.'},
{id:'choice',name:'Conditional choice',source:'signal r0 1 0\nchoose r0 zero nonzero\nzero: mark r1 48\nstep output\nnonzero: mark r1 49\noutput: signal r1 0 1\nsignal r0 2 1\n',input:[1],drivers:[],description:'Outputs 0 for zero input, otherwise 1.'},
{id:'latch',name:'Attached latch',source:'mark r0 65\nsignal r0 17 1\nsignal r1 17 0\nsignal r1 0 1\nsignal r0 2 1\n',input:[],drivers:['latch'],description:'Stores and retrieves a value using port 17.'}
];
function instantiate(id){const template=templates.find(t=>t.id===id);if(!template)throw Error('Unknown template');return {...template,input:[...template.input],drivers:[...template.drivers]};}
root.JerryPopTemplates={templates,instantiate};
})(globalThis);
