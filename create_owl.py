#!/usr/bin/env python
""" create_owl.py

Code to translate the Cognitive Atlas database dump into OWL format.


Concepts and tasks can be exported as csv on the admin page: 
http://www.cognitiveatlas.org/admin/
I will expand that code to include relations, conditions and contrasts, 
but for now I just export those tables from phpMyAdmin.

Generate Task Records
http://www.cognitiveatlas.org/rdf/testgenall.php?type=task

Generate Concept Records
http://www.cognitiveatlas.org/rdf/testgenall.php?type=concept



"""

## Copyright 2011, Russell Poldrack. All rights reserved.

## Redistribution and use in source and binary forms, with or without modification, are
## permitted provided that the following conditions are met:

##    1. Redistributions of source code must retain the above copyright notice, this list of
##       conditions and the following disclaimer.

##    2. Redistributions in binary form must reproduce the above copyright notice, this list
##       of conditions and the following disclaimer in the documentation and/or other materials
##       provided with the distribution.

## THIS SOFTWARE IS PROVIDED BY RUSSELL POLDRACK ``AS IS'' AND ANY EXPRESS OR IMPLIED
## WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
## FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL RUSSELL POLDRACK OR
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
## CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
## SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
## ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
## NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import pickle
versionString='0.3'

def make_sentence_case(s):
    """ make sentence case, excluding acronyms in parens and keeping proper nouns"""
    ss=s.split('(')    
    ss[0]=ss[0][0].upper()+ss[0][1:].lower()
    ssc='('.join(ss)
    return ssc

# load in the ID dictionary if it exists

id_dictionary_file='ontology/id_dictionary.pkl'
try:
    pklfile=open(id_dictionary_file,'rb')
    id_dictionary=pickle.load(pklfile)
    pklfile.close()
    dict_ctr=len(id_dictionary)
    existing_pickle_count=dict_ctr
except:
    existing_pickle_count=0
    id_dictionary={}
    # save the first 100 entries for reserved words
    dict_ctr=101
    
# first fix the concepts file

rdf_file='ontology/all_concepts.rdf'

f=open(rdf_file,'r')
# 1.  change from skos:Concept to owl:Class
r=[a.replace('skos:Concept','owl:Class').strip() for a in f.readlines()]
f.close()

# 2. separate each ontological element into a separate array entry

r_joined = ' '.join(r).split('<owl:Class')
rdf_preamble=r_joined[0].replace('" ','"\n').replace('RDF','RDF\n')
rdf_preamble=rdf_preamble.split('?>')[1]
owl_classes = ['<owl:Class'+a for a in r_joined[1:]]
owl_classes[-1]=owl_classes[-1].replace('</rdf:RDF>','')

# 3. add additional namespaces

additional_namespaces=['xmlns:OBO_REL="http://purl.org/obo/owl/OBO_REL#"','xmlns:snap="http://www.ifomis.org/bfo/1.1/snap#"','xmlns:obo="http://purl.obolibrary.org/obo/"','xmlns:ro="http://www.obofoundry.org/ro/ro.owl#"','xmlns:owl="http://www.w3.org/2002/07/owl#"','xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"','xmlns:span="http://www.ifomis.org/bfo/1.1/span#"','xmlns:cogpo="http://www.cogpo.org/ontologies/working/CogPOver2011.owl#"']

for a in additional_namespaces:
    rdf_preamble=rdf_preamble.replace('> ','\n\t%s> '%a)

rdf_preamble=rdf_preamble+'\n\n<owl:Ontology rdf:about="http://www.cognitiveatlas.org/ontology/cogat.owl">\n\t<owl:versionInfo>%s</owl:versionInfo>\n</owl:Ontology>\n\n'%versionString

rdf_entities=['dc "http://purl.org/dc/elements/1.1/"','ro "http://www.obofoundry.org/ro/ro.owl#"','cogat "http://www.cognitiveatlas.org/ontology/cogat.owl#"','rdf "http://www.w3.org/1999/02/22-rdf-syntax-ns#"','skos "http://www.w3.org/2004/02/skos/core#"','rdfs "http://www.w3.org/2000/01/rdf-schema#"','span "http://www.ifomis.org/bfo/1.1/span#"','cogpo "http://www.cogpo.org/ontologies/working/CogPOver2011.owl#"']

entities='<!DOCTYPE rdf:RDF [\n'
for a in rdf_entities:
    entities=entities+'<!ENTITY %s >\n'%a
entities=entities+']>\n\n'


# 4. add descriptions of properties 
properties='<!--\n//Annotation Properties\n-->\n\n'

concept_fields=['dc:Title','dc:Contributor','dc:Date','skos:definition','skos:prefLabel','skos:altLabel','skos:hasTopConcept']
task_fields=['dc:Title','dc:Contributor','dc:Date','skos:definition','skos:prefLabel','skos:altLabel']

annotation_properties=['&'+a.replace(':',';') for a in set(concept_fields + task_fields)]


for a in annotation_properties:
    properties=properties+'<owl:AnnotationProperty rdf:about="%s"/>\n'%a

# add object properties#
properties=properties+'\n\n<!--\n//Object Properties\n-->\n\n'

object_properties=['<owl:ObjectProperty rdf:about="&ro;has_part"/>','<owl:ObjectProperty rdf:about="&cogat;measured_by"><rdfs:label>measured_by</rdfs:label><obo:IAO_0000115>The relationship between a mental concept and a measurement that is thought to reflect the activity of that mental concept.</obo:IAO_0000115><rdfs:domain rdf:resource="&cogat;MentalConcept"/><rdfs:range rdf:resource="&cogpo;COGPO_00049"/></owl:ObjectProperty>','<owl:ObjectProperty rdf:about="&cogat;descended_from"><rdfs:label>descended_from</rdfs:label><obo:IAO_0000115>The relationship between a task and another task of which the former is an adaptation.</obo:IAO_0000115><rdfs:domain rdf:resource="&cogpo;COGPO_00049"/><rdfs:range rdf:resource="&cogpo;COGPO_00049"/></owl:ObjectProperty>']

# NOTE: need to change the measured_by relation to have contrasts rather than tasks as its domain

for a in object_properties:
    properties=properties+'%s\n'%a

properties=properties+'\n\n'

properties=properties+'<owl:Class rdf:about="&cogat;CAO_00001">\n\t<rdfs:subClassOf rdf:resource="&skos;Concept"/>\n</owl:Class>\n\n'


# 5. fix each class
owl_classes_fixed=[]
owl_id=[]
owl_dict={}
ctr=0
getcontent=lambda x: x.split('<')[0].split('>')[1]

# note:  following the lead of GO, we want:
# rdf:about = CAO_XXXXX
# rdfs:label = plain text name
# dc:identifier = database identifier

for c in owl_classes:
    cl=c.split('> <')
    # get the identifier and create a dictionary
    id=cl[0].split('/')[-1].strip('"')
    owl_id.append(id)
    # remove the brackets left over by the split
    cl[0]=cl[0].replace('<','')
    cl[-1]=cl[-1].replace('>','')
    owl_classes_fixed.append('\n'.join(['<'+a+'>' for a in cl]))
    owl_dict[id]={}
    for f in concept_fields:
        owl_dict[id][f]=''
        
    for e in cl:
        for f in concept_fields:
            if e.find(f)>-1:
                owl_dict[id][f]=getcontent(e).replace('&','and').replace('/','-').replace('_','-')
    owl_dict[id]['dc:Title']=make_sentence_case(owl_dict[id]['dc:Title'].replace('Cognitive Atlas : Lexicon : ',''))
    if not id_dictionary.has_key(id):
        id_dictionary[id]='CAO_%05d'%dict_ctr
        dict_ctr+=1
        
    owl_dict[id]['dc:identifier']=id
#    owl_dict[id]['dc:Title'].replace('Cognitive Atlas : Lexicon : ','').lower()
    owl_dict[id]['rdf:about']=id_dictionary[id]
    owl_dict[id]['skos:prefLabel']=make_sentence_case(owl_dict[id]['skos:prefLabel'])
    owl_dict[id]['relations']=[]
    owl_dict[id]['superClass']='&cogat;CAO_00001'
    ctr+=1

# read in tasks
rdf_file='ontology/all_tasks.rdf'
f=open(rdf_file,'r')
# 1.  change from skos:Concept to owl:Class
r=[a.replace('skos:Concept','owl:Class').strip() for a in f.readlines()]
f.close()

# 2. separate each ontological element into a separate array entry

r_joined = ' '.join(r).split('<owl:Class')
#rdf_preamble=r_joined[0].replace('" ','"\n').replace('RDF','RDF\n')
owl_classes = ['<owl:Class'+a for a in r_joined[1:]]
owl_classes[-1]=owl_classes[-1].replace('</rdf:RDF>','')

owl_task_classes_fixed=[]
owl_task_id=[]
owl_task_dict={}
ctr=0
for c in owl_classes:
    cl=c.split('> <')
    # get the identifier and create a dictionary
    id=cl[0].split('/')[-1].strip('"')
    owl_task_id.append(id)
    # remove the brackets left over by the split
    cl[0]=cl[0].replace('<','')
    cl[-1]=cl[-1].replace('>','')
    owl_task_classes_fixed.append('\n'.join(['<'+a+'>' for a in cl]))
    owl_task_dict[id]={}
    for f in task_fields:
        owl_task_dict[id][f]=''
        
    for e in cl:
        for f in task_fields:
            if e.find(f)>-1:
                owl_task_dict[id][f]=getcontent(e).replace('&','and').replace('/','-').replace('_','-')
    owl_task_dict[id]['dc:Title']=make_sentence_case(owl_task_dict[id]['dc:Title'].replace('Cognitive Atlas : Lexicon : ',''))
    if not id_dictionary.has_key(id):
        id_dictionary[id]='CAO_%05d'%dict_ctr
        dict_ctr+=1
        
    owl_task_dict[id]['dc:identifier']=id
#    owl_task_dict[id]['dc:Title'].replace('Cognitive Atlas : Lexicon : ','').lower()
    owl_task_dict[id]['rdf:about']=id_dictionary[id]
    owl_task_dict[id]['skos:prefLabel']=make_sentence_case(owl_task_dict[id]['skos:prefLabel'])
    owl_task_dict[id]['relations']=[]
    owl_task_dict[id]['conditions']=[]
    owl_task_dict[id]['contrasts']=[]
    owl_task_dict[id]['superClass']='&cogpo;COGPO_00049'
    ctr+=1


# read in conditions

conditions_file='ontology/type_condition.csv'
conditions=[]
conditions_dict={}
f=open(conditions_file,'r')
for l in f.readlines():
    conditions.append(l.strip().replace('"','').split(';'))

for c in conditions:
    owl_task_dict[c[2]]['conditions'].append(c)
    conditions_dict[c[0]]=c[2]
    if not id_dictionary.has_key(c[0]):
       id_dictionary[c[0]]='CAO_%05d'%dict_ctr
       dict_ctr+=1
         
# read in contrasts

contrasts_file='ontology/type_contrast.csv'
contrasts=[]
contrasts_dict={}
f=open(contrasts_file,'r')
for l in f.readlines():
    contrasts.append(l.strip().replace('"','').split(';'))

for c in contrasts:
    try:
        owl_task_dict[c[2]]['contrasts'].append(c)
        contrasts_dict[c[0]]=c[2]
        if not id_dictionary.has_key(c[0]):
           id_dictionary[c[0]]='CAO_%05d'%dict_ctr
           dict_ctr+=1
    except:
        print 'problem adding %s'%c

# read in relations

## "T1";"is a kind of";"is-a-kind-of";"Foundational";"The subject is a subtype of the object.";"The 3-Back test is-a-kind-of N-Back test.";"100";"is not a kind of"
## "T10";"is a synonym of";"has-synonym";"Terminological";"The two terms are transitively synonomous. ";"Declarative memory is a synonym of explicit memory..";"200";"is not a synonym of"
## "T15";"is descended from";"descended-from";"Cognitive";"The subject task is derivative of the predicate task.";"Masked lexical decision task derives from lexical decision task.";"410";"is not descended from"
## "T16";"is measured by";"is-measured-by";"Cognitive";"The concept can be measured by the task:contrast.";"Conflict detection is measured by the contrast of incongruent - congruent trials in the color-word stroop task";"501";"is not measured by"
## "T17";"has literature association";"has-literature-association";"Citational";"Object found in cited literature.";"for example...";"100000";"has no literature association"
## "T2";"is a part of";"is-a-part-of";"Foundational";"The predicate is a constituent element of the subject (either integral or proper). ";"Cue specification is a part of memory retrieval.";"101";"is not a part of"
## "T5";"is preceded by";"preceded-by";"Temporal";"The subject is preceded temporally by the predicate.";"Example of this relation here.";"302";"is not preceded by"

relation_file='ontology/table_assertion.csv'
relations=[]
f=open(relation_file,'r')
for l in f.readlines():
    relations.append(l.strip().replace('"','').split(';'))    

f.close()

relations_legend=relations[0]

relations.remove(relations[0])  # get rid of legend

for r in relations:
    if owl_dict.has_key(r[2]):
        owl_dict[r[2]]['relations'].append(r)
    elif owl_task_dict.has_key(r[2]):
        owl_task_dict[r[2]]['relations'].append(r)
    #else:
    #    print 'problem with %s'%r

# save everything to file
owl_file='ontology/cogat.owl'
f=open(owl_file,'w')
f.write('<?xml version="1.0"?>\n\n')
f.write(entities)

f.write(rdf_preamble+'\n\n\n')
f.write(properties)

attrs_to_loop=['dc:Title','dc:Contributor','dc:Date','skos:definition','skos:prefLabel','skos:altLabel','skos:hasTopConcept']
for a in owl_dict.iterkeys():
    d=owl_dict[a]
    f.write('<owl:Class rdf:about="&cogat;%s">\n'%id_dictionary[a])
    f.write('\t<rdfs:label>%s</rdfs:label>\n'%d['dc:Title'])
    f.write('\t<dc:identifier>%s</dc:identifier>\n'%a)
    for l in attrs_to_loop:
        f.write('\t<%s>%s</%s>\n'%(l,d[l],l))
    superClassSet=0
    measured_by_relations=[]
    if len(d['relations'])>0:
        for r in d['relations']:
            if r[3]=='T1' and owl_dict.has_key(r[4]):
                d['superClass']='&cogat;'+id_dictionary[r[4]]
            elif r[3]=='T2' and owl_dict.has_key(r[4]):
                f.write('\t<rdfs:subClassOf>\n\t\t<owl:Restriction>\n\t\t\t<owl:onProperty rdf:resource="&ro;part_of"/>\n\t\t\t<owl:someValuesFrom rdf:resource="&cogat;%s"/>\n\t\t</owl:Restriction>\n\t</rdfs:subClassOf>\n'%id_dictionary[r[4]])
            elif r[3]=='T16' and contrasts_dict.has_key(r[11]):
                 measured_by_relations.append(r)

    f.write('\t<rdfs:subClassOf rdf:resource="%s"/>\n'%d['superClass'])
#    if 0:
    if len(measured_by_relations)>1:
        # first need to clean out duplicate entries:
        cnt_names=set([c[11] for c in measured_by_relations])
        good_measured_by_relations=[]
        for m in measured_by_relations:
            if m[11] in cnt_names:
                good_measured_by_relations.append(m)
#        print good_measured_by_relations
        
        for m in good_measured_by_relations:
            f.write('\t<rdfs:subClassOf>\n\t\t<owl:Restriction>\n\t\t\t<owl:onProperty rdf:resource="&cogat;measured_by"/>\n\t\t\t<owl:someValuesFrom rdf:resource="&cogat;%s"/>\n\t\t</owl:Restriction>\n\t</rdfs:subClassOf>\n'%id_dictionary[m[11]])
        f.write('\t<rdfs:subClassOf>\n\t\t<owl:Restriction>\n\t\t\t<owl:onProperty rdf:resource="&cogat;measured_by"/>\n\t\t\t\t<owl:allValuesFrom>\n\t\t\t\t\t<owl:Class>\n\t\t\t\t\t\t<owl:unionOf rdf:parseType="Collection">\n')
        #print measured_by_relations
        for m in good_measured_by_relations:
            f.write('\t\t\t\t\t\t<rdf:Description rdf:about="&cogat;%s"/>\n'%id_dictionary[m[11]])
        f.write('\t\t\t\t\t\t</owl:unionOf>\n\t\t\t\t\t</owl:Class>\n\t\t\t\t</owl:allValuesFrom>\n\t\t</owl:Restriction>\n\t</rdfs:subClassOf>\n\n')

    f.write('</owl:Class>\n\n\n')
               
                
attrs_to_loop=['dc:Title','dc:Contributor','dc:Date','skos:definition','skos:prefLabel','skos:altLabel']
for a in owl_task_dict.iterkeys():
    d=owl_task_dict[a]
    f.write('<owl:Class rdf:about="&cogat;%s">\n'%id_dictionary[a])
    f.write('\t<dc:identifier>%s</dc:identifier>\n'%a)
    f.write('\t<rdfs:label>%s</rdfs:label>\n'%d['dc:Title'])
    for l in attrs_to_loop:
        f.write('\t<%s>%s</%s>\n'%(l,d[l],l))
    # write out conditions
    if len(d['conditions'])>0:
        for c in d['conditions']:
                f.write('\t<rdfs:subClassOf>\n\t\t<owl:Restriction>\n\t\t\t<owl:onProperty rdf:resource="&ro;has_part"/>\n\t\t\t<owl:someValuesFrom rdf:resource="&cogat;%s"/>\n\t\t</owl:Restriction>\n\t</rdfs:subClassOf>\n'%id_dictionary[c[0]])
    if len(d['contrasts'])>0:
        for c in d['contrasts']:
                f.write('\t<rdfs:subClassOf>\n\t\t<owl:Restriction>\n\t\t\t<owl:onProperty rdf:resource="&cogpo;has_contrast"/>\n\t\t\t<owl:someValuesFrom rdf:resource="&cogat;%s"/>\n\t\t</owl:Restriction>\n\t</rdfs:subClassOf>\n'%id_dictionary[c[0]])
   
    if len(d['relations'])>0:
        for r in d['relations']:
            if r[3]=='T15' and owl_task_dict.has_key(r[4]):
                 print r
                 f.write('\t<rdfs:subClassOf>\n\t\t<owl:Restriction>\n\t\t\t<owl:onProperty rdf:resource="&cogat;descended_from"/>\n\t\t\t<owl:someValuesFrom rdf:resource="&cogat;%s"/>\n\t\t</owl:Restriction>\n\t</rdfs:subClassOf>\n'%id_dictionary[r[4]])
    f.write('\t<rdfs:subClassOf rdf:resource="%s"/>\n'%d['superClass'])
    f.write('</owl:Class>\n\n\n')

# write out conditions as classes
for a in owl_task_dict.iterkeys():
    if len(owl_task_dict[a]['conditions'])>0:
        for c in owl_task_dict[a]['conditions']:
            c = [x.replace('&#34;','') for x in c]
            c = [x.replace('&#34','') for x in c]
            c = [x.replace('&','and') for x in c]
            condname=owl_task_dict[a]['dc:Title'].replace(' ','_')+'-'+c[3].replace(' ','_')
            f.write('<owl:Class rdf:about="&cogat;%s">\n'%id_dictionary[c[0]])
            f.write('\t<dc:identifier>%s</dc:identifier>\n'%c[0])
            f.write('\t<skos:definition>%s</skos:definition>\n'%c[4])
            #print c[4]
            f.write('\t<rdfs:label>%s</rdfs:label>\n'%condname)
            f.write('\t<rdfs:subClassOf>\n\t\t<owl:Restriction>\n\t\t\t<owl:onProperty rdf:resource="&ro;part_of"/>\n\t\t\t<owl:someValuesFrom rdf:resource="&cogat;%s"/>\n\t\t</owl:Restriction>\n\t</rdfs:subClassOf>\n'%id_dictionary[c[2]])
            f.write('\t<rdfs:subClassOf rdf:resource="&cogpo;COGPO_00300"/>\n')
            f.write('</owl:Class>\n\n\n')
          
# write out contrasts as classes
for a in owl_task_dict.iterkeys():
    if len(owl_task_dict[a]['contrasts'])>0:
        for c in owl_task_dict[a]['contrasts']:
            c = [x.replace('&#34;','') for x in c]
            c = [x.replace('&#34','') for x in c]
            c = [x.replace('&','and') for x in c]
            contname=owl_task_dict[a]['dc:Title'].replace(' ','_')+'-'+c[3].replace(' ','_')
            f.write('<owl:Class rdf:about="&cogat;%s">\n'%id_dictionary[c[0]])
            f.write('\t<dc:identifier>%s</dc:identifier>\n'%c[0])
            f.write('\t<rdfs:label>%s</rdfs:label>\n'%contname)
            f.write('\t<rdfs:subClassOf>\n\t\t<owl:Restriction>\n\t\t\t<owl:onProperty rdf:resource="&cogpo;is_related_to"/>\n\t\t\t<owl:someValuesFrom rdf:resource="&cogat;%s"/>\n\t\t</owl:Restriction>\n\t</rdfs:subClassOf>\n'%id_dictionary[c[2]])
            f.write('\t<rdfs:subClassOf rdf:resource="&cogpo;COGPO_00109"/>\n')
            f.write('</owl:Class>\n\n\n')
          


# add basic classes

f.write('<!-- http://www.ifomis.org/bfo/1.1/span#Process -->\n\n<owl:Class rdf:about="&span;Process"/>\n\n<!-- http://www.w3.org/2004/02/skos/core#Concept -->\n\n<owl:Class rdf:about="&skos;Concept"/>\n\n')

f.write('</rdf:RDF>\n')

f.close()

if not dict_ctr==existing_pickle_count:
    print 'added new terms, saving dictionary...'
    pklfile=open(id_dictionary_file,'wb')
    pickle.dump(id_dictionary,pklfile)
    pklfile.close()
