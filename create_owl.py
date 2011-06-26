#!/usr/bin/env python

# first fix the concepts file

rdf_file='ontology/concepts.rdf'

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

print rdf_preamble

rdf_entities=['dc "http://purl.org/dc/elements/1.1/"','ro "http://www.obofoundry.org/ro/ro.owl#"','cogat "http://www.cognitiveatlas.org/ontology/cogat.owl#"','rdf "http://www.w3.org/1999/02/22-rdf-syntax-ns#"','skos "http://www.w3.org/2004/02/skos/core#"','rdfs "http://www.w3.org/2000/01/rdf-schema#"','span "http://www.ifomis.org/bfo/1.1/span#"','cogpo "http://www.cogpo.org/ontologies/working/CogPOver2011.owl#"']

entities='<!DOCTYPE rdf:RDF [\n'
for a in rdf_entities:
    entities=entities+'<!ENTITY %s >\n'%a
entities=entities+']>\n\n'


# 4. add descriptions of properties 
properties='<!--\n//Annotation Properties\n-->\n\n'

concept_fields=['dc:Title','dc:Contributor','dc:Date','skos:definition','skos:prefLabel','skos:altLabel']
task_fields=['dc:Title','dc:Contributor','dc:Date','skos:definition','skos:prefLabel','skos:altLabel']

annotation_properties=['&'+a.replace(':',';') for a in set(concept_fields + task_fields)]


for a in annotation_properties:
    properties=properties+'<owl:AnnotationProperty rdf:about="%s"/>\n'%a

# add object properties#
properties=properties+'\n\n<!--\n//Object Properties\n-->\n\n'

object_properties=['<owl:ObjectProperty rdf:about="&ro;has_part"/>','<owl:ObjectProperty rdf:about="&cogat;measured_by"><rdfs:label>measured_by</rdfs:label><rdfs:domain rdf:resource="&cogat;MentalConcept"/><rdfs:range rdf:resource="&cogpo;COGPO_00049"/></owl:ObjectProperty>','<owl:ObjectProperty rdf:about="&cogat;descended_from"><rdfs:label>descended_from</rdfs:label><rdfs:domain rdf:resource="&cogpo;COGPO_00049"/><rdfs:range rdf:resource="&cogpo;COGPO_00049"/></owl:ObjectProperty>']

# NOTE: need to change the measured_by relation to have contrasts rather than tasks as its domain

for a in object_properties:
    properties=properties+'%s\n'%a

properties=properties+'\n\n'

properties=properties+'<owl:Class rdf:about="&cogat;MentalConcept">\n\t<rdfs:subClassOf rdf:resource="&skos;Concept"/>\n</owl:Class>\n\n'


# 5. fix each class
owl_classes_fixed=[]
owl_id=[]
owl_dict={}
ctr=0
getcontent=lambda x: x.split('<')[0].split('>')[1]

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
                owl_dict[id][f]=getcontent(e)
    
    owl_dict[id]['dc:Title']=owl_dict[id]['dc:Title'].replace('Cognitive Atlas : Lexicon : ','')
    owl_dict[id]['relations']=[]
    owl_dict[id]['superClass']='&cogat;MentalConcept'
    ctr+=1

# read in tasks
rdf_file='ontology/tasks.rdf'
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
                owl_task_dict[id][f]=getcontent(e)
    owl_task_dict[id]['dc:Title']=owl_task_dict[id]['dc:Title'].replace('Cognitive Atlas : Lexicon : ','')
    owl_task_dict[id]['relations']=[]
    #owl_task_dict[id]['superClass']='&span;Process'
    owl_task_dict[id]['superClass']='&cogpo;COGPO_00049'
    ctr+=1

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
        owl_dict[r[2]]['relations'].append([r[3],r[4]])
    elif owl_task_dict.has_key(r[2]):
        owl_task_dict[r[2]]['relations'].append([r[3],r[4]])
    #else:
    #    print 'problem with %s'%r

# save everything to file
owl_file='ontology/cogat.owl'
f=open(owl_file,'w')
f.write('<?xml version="1.0"?>\n\n')
f.write(entities)

f.write(rdf_preamble+'\n\n\n')
f.write(properties)

attrs_to_loop=['dc:Title','dc:Contributor','dc:Date','skos:definition','skos:prefLabel','skos:altLabel']
for a in owl_dict.iterkeys():
    d=owl_dict[a]
    f.write('<owl:Class rdf:about="&cogat;%s">\n'%a)
    f.write('\t<rdfs:label>%s</rdfs:label>\n'%d['dc:Title'])
    f.write('\t<dc:identifier>%s</dc:identifier>\n'%a)
    for l in attrs_to_loop:
        f.write('\t<%s>%s</%s>\n'%(l,d[l],l))
    superClassSet=0
    measured_by_relations=[]
    if len(d['relations'])>0:
        for r in d['relations']:
            if r[0]=='T1' and owl_dict.has_key(r[1]):
                superClassSet=1
                f.write('\t<rdfs:subClassOf rdf:resource="&cogat;%s"/>\n'%r[1])
            elif r[0]=='T2' and owl_dict.has_key(r[1]):
                f.write('\t<rdfs:subClassOf>\n\t\t<owl:Restriction>\n\t\t\t<owl:onProperty rdf:resource="&ro;part_of"/>\n\t\t\t<owl:someValuesFrom rdf:resource="&cogat;%s"/>\n\t\t</owl:Restriction>\n\t</rdfs:subClassOf>\n'%r[1])
            elif r[0]=='T16' and owl_task_dict.has_key(r[1]):
                measured_by_relations.append(r[1])
                

    if not superClassSet:
        f.write('\t<rdfs:subClassOf rdf:resource="%s"/>\n'%d['superClass'])
#    if 0:
    if len(measured_by_relations)>1:
        for m in set(measured_by_relations):
            f.write('\t<rdfs:subClassOf>\n\t\t<owl:Restriction>\n\t\t\t<owl:onProperty rdf:resource="&cogat;measured_by"/>\n\t\t\t<owl:someValuesFrom rdf:resource="&cogat;%s"/>\n\t\t</owl:Restriction>\n\t</rdfs:subClassOf>\n'%m)
        f.write('\t<rdfs:subClassOf>\n\t\t<owl:Restriction>\n\t\t\t<owl:onProperty rdf:resource="&cogat;measured_by"/>\n\t\t\t\t<owl:allValuesFrom>\n\t\t\t\t\t<owl:Class>\n\t\t\t\t\t\t<owl:unionOf rdf:parseType="Collection">\n')
        #print measured_by_relations
        for m in set(measured_by_relations):
            f.write('\t\t\t\t\t\t<rdf:Description rdf:about="&cogat;%s"/>\n'%m)
        f.write('\t\t\t\t\t\t</owl:unionOf>\n\t\t\t\t\t</owl:Class>\n\t\t\t\t</owl:allValuesFrom>\n\t\t</owl:Restriction>\n\t</rdfs:subClassOf>\n\n')

    f.write('</owl:Class>\n\n\n')
               
                
attrs_to_loop=['dc:Title','dc:Contributor','dc:Date','skos:definition','skos:prefLabel','skos:altLabel']
for a in owl_task_dict.iterkeys():
    d=owl_task_dict[a]
    f.write('<owl:Class rdf:about="&cogat;%s">\n'%a)
    f.write('\t<dc:identifier>%s</dc:identifier>\n'%a)
    f.write('\t<rdfs:label>%s</rdfs:label>\n'%d['dc:Title'])
    for l in attrs_to_loop:
        f.write('\t<%s>%s</%s>\n'%(l,d[l],l))
    if len(d['relations'])>0:
        for r in d['relations']:
            if r[0]=='T15' and owl_task_dict.has_key(r[1]):
                print r
                f.write('\t<rdfs:subClassOf>\n\t\t<owl:Restriction>\n\t\t\t<owl:onProperty rdf:resource="&cogat;descended_from"/>\n\t\t\t<owl:someValuesFrom rdf:resource="&cogat;%s"/>\n\t\t</owl:Restriction>\n\t</rdfs:subClassOf>\n'%r[1])
    f.write('\t<rdfs:subClassOf rdf:resource="%s"/>\n'%d['superClass'])
    f.write('</owl:Class>\n\n\n')
                


# add basic classes

f.write('<!-- http://www.ifomis.org/bfo/1.1/span#Process -->\n\n<owl:Class rdf:about="&span;Process"/>\n\n<!-- http://www.w3.org/2004/02/skos/core#Concept -->\n\n<owl:Class rdf:about="&skos;Concept"/>\n\n')

f.write('</rdf:RDF>\n')

f.close()
