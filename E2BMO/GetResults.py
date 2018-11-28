#!/Users/banafsheh/anaconda3/bin/env python
import sys
import rdflib
import rdfextras
import re
import threading, time, random
import json

questionVariable = (sys.argv[1])
questionType = (sys.argv[2])
conceptSchemeFlag = False;

#BMO_MASTER for BMO relations
#BMOSKOS_V3 for BMO + SKOS words
filename = "file:///Library/WebServer/Documents/E2BMO/CGI-Executables/BMOSKOS_V3" #replace with something interesting
# with open('/Library/WebServer/Documents/BioOntologyCourse/BMOSKOS_V3') as f:
#     content = f.readlines()
#     print(content)

f1=open('/Library/WebServer/Documents/E2BMO/CGI-Executables/'+questionVariable+'_trade_offs.txt', 'w')
f2=open('/Library/WebServer/Documents/E2BMO/CGI-Executables/'+questionVariable+'_BiologicalText.txt', 'w')
fgraph=open('/Library/WebServer/Documents/E2BMO/CGI-Executables/'+questionVariable+'_graph.csv', 'w')
print("in python")
rdfextras.registerplugins() # so we can Graph.query()

g=rdflib.Graph()
g.parse(filename)
query_with_placeholder = None;
results=[];
Final_results =[];
graphresults=[];
graphresults.append("'id', 'childLabel', 'parent', 'size', { role: 'style' }\n0,"+questionVariable+", -1, 1,  black\n");
parent="";
parent2="";
flag=False;
i = 1 ;

#creates duplicates = to remove later !!!!! now manually removing
FoundBiologyText =[]
text =[]

#reading from trade_offs files already created
def getNoun2(questionVariable):
    global Final_results
    with open('/Library/WebServer/Documents/E2BMO/CGI-Executables/'+questionVariable+'.txt') as f:
        lines = f.read().split("\n")
        for line in lines:
            if(line not in Final_results):
                r = line.split("::")
                g = r[-1].split(",")
                Final_results.append(r[0:len(r)-1]+g)
                print(Final_results[-1])
    
    

#Creating trade-off files : use BMO_MASTER
def getNoun(questionVariable):
#     global Final_results
    count =0
    query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
    SELECT  ?labelogg ?anot ?antithesisVal ?thesisVal ?ReferenceURLVAL ?s
    where{
    ?s rdfs:label '$ENTITY_CODE$' .
    ?s a owl:Class .
    ?t rdfs:subClassOf ?s .
    ?t a owl:Class .
    ?t rdfs:label ?labelogg .
    ?t obo:IAO_0000305 ?anot .
    ?t obo:Antithesis  ?antithesisVal .
    ?t obo:Thesis   ?thesisVal .
    ?t obo:IAO_0000301  ?ReferenceURLVAL .
    }
    """
    if query_with_placeholder != None:
        new_query=query_with_placeholder.replace("$ENTITY_CODE$",questionVariable)
        predicate_query = g.query(new_query)
        print (new_query);
        
        for row in predicate_query:
            results.append(row['labelogg'].toPython() +"::"+ row['antithesisVal'].toPython() +"::"+ row['thesisVal'].toPython() +"::"+ row['anot'].toPython()+ "::"+ row['ReferenceURLVAL'].toPython()+ "::")
            #parentNoun = questionVariable.replace(' ', '_')+"."+row['labelogg'].toPython().replace(' ', '_')
#             print(row['s'])
            newSearch = row['labelogg']
            query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
            SELECT  ?thesisAnthithesis ?someValuesFrom ?s
            where{
            ?s rdfs:label '$ENTITY_CODE$' .
            ?s a owl:Class .
            {?s owl:equivalentClass/owl:intersectionOf _:b. _:b rdf:first ?restriction}
            UNION { ?s owl:equivalentClass/owl:intersectionOf/(rdf:rest+/rdf:first+)*  ?restriction.}
            ?restriction  rdf:type owl:Restriction.
            ?restriction  owl:onProperty ?onProp.
            ?restriction  owl:someValuesFrom ?someValuesFrom.
            ?someValuesFrom rdfs:label ?thesisAnthithesis .
            }
            """
            if query_with_placeholder != None:
                new_query=query_with_placeholder.replace("$ENTITY_CODE$",newSearch)
                print(new_query)
                predicate_query = g.query(new_query)
                for row in predicate_query:
                    results.append(row['thesisAnthithesis'].toPython()+"::")
                    print(row['s'] + "\n")
                    SuperClassSearch = row['someValuesFrom']
                    print(SuperClassSearch + "\n")
                    classCode = re.findall(r'\d+',SuperClassSearch)
                    print( classCode[0][5] +" "+ classCode[0][6]+"\n");
                    TRIZCode = "http://purl.obolibrary.org/obo/BMO_00000"+classCode[0][5]+ classCode[0][6];
                    print(TRIZCode)

                    query_with_placeholder="""
                    PREFIX obo_term: <http://purl.obolibrary.org/obo/>
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX base: <http://www.semanticweb.org/banafsheh/ontologies/2018/3/rdf_xml#>

                    SELECT  ?superTRIZLabels
                    where{
                    <$ENTITY_CODE$> rdfs:label ?superTRIZLabels .

                    }
                    """
                    if query_with_placeholder != None:
                        new_query=query_with_placeholder.replace("$ENTITY_CODE$",TRIZCode)
                        print(new_query)
                        predicate_query = g.query(new_query)

                        for row in predicate_query:
                            results.append(row['superTRIZLabels'].toPython()+" ::" )
                            print(row['superTRIZLabels'].toPython())
                        if len(predicate_query) <1:
                            results.append(" TRIZ label "+"::" )
                            print(" - "+"::" )


            query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
            SELECT  ?subclassPrinciples ?someValuesFrom
            where{
            ?s rdfs:label '$ENTITY_CODE$' .
            ?s a owl:Class .
            {?s rdfs:subClassOf _:b. _:b rdf:first ?restriction}

            UNION { ?s rdfs:subClassOf/(rdf:rest+/rdf:first+)*  ?restriction.}

            ?restriction  rdf:type owl:Restriction.

            ?restriction  owl:onProperty ?onProp.

            FILTER(regex(str(?onProp), "use_the_principle", "i"))


            ?restriction  owl:someValuesFrom ?someValuesFrom.

            ?someValuesFrom rdfs:label ?subclassPrinciples .

            }
            """
            if query_with_placeholder != None:
                new_query=query_with_placeholder.replace("$ENTITY_CODE$",newSearch)
                print(new_query)
                predicate_query = g.query(new_query)

                for row in predicate_query:
                    results.append(row['subclassPrinciples'].toPython()+"|" )
                    SuperClassSearch = row['someValuesFrom']
                    print(SuperClassSearch + "\n")
                    classCode = re.findall(r'\d+',SuperClassSearch)
                    print( classCode[0][2] +" "+ classCode[0][3]+"\n");
                    TRIZCode = "http://purl.obolibrary.org/obo/BMO_01"+classCode[0][2]+ classCode[0][3]+"0";
                    print(TRIZCode)

                    query_with_placeholder="""
                    PREFIX obo_term: <http://purl.obolibrary.org/obo/>
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX base: <http://www.semanticweb.org/banafsheh/ontologies/2018/3/rdf_xml#>

                    SELECT  ?superTRIZLabels ?IPVALUE
                    where{
                    <$ENTITY_CODE$> rdfs:label ?superTRIZLabels .
                    <$ENTITY_CODE$> BMO:TRIZ_reference ?IPVALUE

                    }
                    """
                    if query_with_placeholder != None:
                        new_query=query_with_placeholder.replace("$ENTITY_CODE$",TRIZCode)
                        print(new_query)
                        predicate_query = g.query(new_query)

                        for row in predicate_query:
                            results.append(row['IPVALUE'].toPython()+":"+row['superTRIZLabels'].toPython()+"," )
                            print(row['superTRIZLabels'].toPython())
                        if len(predicate_query) <1:
                            results.append(" TRIZ label "+"::" )
                            print(" - "+"::" )
                results.append("\n")

                # if(results[count:len(results)] not in Final_results):
#                     Final_results.append(results[count:len(results)])
#                 count = len(results);
               #  print(Final_results[-1])
#                 print("\n")
                    


    
    
    
def func(parent,query):
    print(parent)
    global i
#     global content
    query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
    PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
    SELECT  ?ipNames ?ipnumbers ?ipvalues
    where{
    <$ENTITY_CODE$> rdf:type ?ipvalues .
    ?ipvalues rdfs:label ?ipNames .
    ?ipvalues BMOKernel:TRIZ_reference ?ipnumbers .
    }
    """
    if query_with_placeholder != None:
        new_query=query_with_placeholder.replace("$ENTITY_CODE$",query)
        print(new_query)
        predicate_query = g.query(new_query)

        for row in predicate_query:

            print("ipname: "+ row['ipNames'].toPython()+"\n" + "ipnumber: "+row['ipnumbers'].toPython()+"\n")
            name = row['ipNames'].toPython() + " ("+row['ipnumbers'].toPython().replace(' ', '')+")"
            graphresults.append(""+str(i)+", '"+name+"', "+str(parent)+", 1, red\n")
            parentIP = i
            i = i +1;
            ipname = row['ipNames'].toPython()
            ipnumber = row['ipnumbers'].toPython()
            # if( row['ipvalues'] not in SubIPClassSearch):
#                 SubIPClassSearch.append(row['ipvalues'])
            
                        
            
#             first level Sub IP
            query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
            PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
            SELECT  ?labelogg 
            where{
                ?s rdfs:label '$ENTITY_CODE$' .
                ?s a owl:Class .
                ?uriCode rdfs:subClassOf ?s .
                ?uriCode a owl:Class .
                ?uriCode rdfs:label ?labelogg .
                }
            """
            if query_with_placeholder != None:
                new_query=query_with_placeholder.replace("$ENTITY_CODE$",row['ipNames'].toPython())
                print(new_query)
                predicate_query = g.query(new_query)
                for row in predicate_query:
                    regexTemp = row['labelogg'].toPython()
                    print("Sub IPs1: "+regexTemp+"\n");
                    graphresults.append(""+str(i)+", '"+regexTemp+"', "+str(parentIP)+", 1,  purple\n")
                    subIP_parent = i
                    i = i +1;
                    
                    for results_row in Final_results:
                        if((regexTemp+'|'+ipnumber+':'+ipname) in results_row):
                            print(regexTemp)
                            graphresults.append(""+str(i)+", '"+results_row[0]+"', "+str(subIP_parent)+", 1,  blue\n")
                            i = i +1;
                            a= (results_row[0]+"::"+results_row[1]+"::"+results_row[2]+"::"+results_row[3]+"::"+results_row[4]+"::"+results_row[5]+"::"+results_row[6]+"::"+results_row[7]+"::"+results_row[8]+"::")
                            for jcount in range(9,len(results_row)-1): 
                                a+=(results_row[jcount]+",")
                            a+=("\n");
                            text = a

                            if( text not in FoundBiologyText):
                                FoundBiologyText.append(text);

                            # graphresults.append(""+str(i)+", '"+results_row[1]+"', "+str(subIP_parent)+", 1,  blue\n")
#                             i = i +1;
#                             graphresults.append(""+str(i)+", '"+results_row[2]+"', "+str(subIP_parent)+", 1,  blue\n")
#                             i = i +1;
#                             graphresults.append(""+str(i)+", '"+results_row[3]+"', "+str(subIP_parent)+", 1,  blue\n")
#                             i = i +1;
#                             graphresults.append(""+str(i)+", '"+results_row[4]+"', "+str(subIP_parent)+", 1,  blue\n")
#                             i = i +1;
#                             graphresults.append(""+str(i)+", '"+results_row[5]+"', "+str(subIP_parent)+", 1,  blue\n")
#                             i = i +1;
#                             graphresults.append(""+str(i)+", '"+results_row[6]+"', "+str(subIP_parent)+", 1,  blue\n")
#                             i = i +1;
#                             graphresults.append(""+str(i)+", '"+results_row[7]+"', "+str(subIP_parent)+", 1,  blue\n")
#                             i = i +1;
                            


#                     second level of Sub IPs
                    query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
                    PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
                    SELECT  ?labelogg
                    where{
                        ?s rdfs:label '$ENTITY_CODE$' .
                        ?s a owl:Class .
                        ?t rdfs:subClassOf ?s .
                        ?t a owl:Class .
                        ?t rdfs:label ?labelogg .
                        }
                    """
                    if query_with_placeholder != None:
                        new_query=query_with_placeholder.replace("$ENTITY_CODE$",row['labelogg'].toPython())
                        print(new_query)
                        predicate_query = g.query(new_query)
                        for row in predicate_query:
                            regexTemp = row['labelogg'].toPython()
                            print("Sub IPs2: "+regexTemp+"\n");
                            graphresults.append(""+str(i)+", '"+regexTemp+"', "+str(subIP_parent)+", 1,  purple\n")
                            subIP_parent2 = i
                            i = i +1;
                            for results_row in Final_results:
                                if((regexTemp+'|'+ipnumber+':'+ipname)  in results_row):
                                    print(results_row[0])
                                    graphresults.append(""+str(i)+", '"+results_row[0]+"', "+str(subIP_parent2)+", 1,  blue\n")
                                    i = i +1;
                                    a= (results_row[0]+"::"+results_row[1]+"::"+results_row[2]+"::"+results_row[3]+"::"+results_row[4]+"::"+results_row[5]+"::"+results_row[6]+"::"+results_row[7]+"::"+results_row[8]+"::")
                                    for jcount in range(9,len(results_row)-1): 
                                        a+=(results_row[jcount]+",")
                                    a+=("\n");
                                    text = a

                                    if( text not in FoundBiologyText):
                                        FoundBiologyText.append(text);

                                    # graphresults.append(""+str(i)+", '"+results_row[1]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                     i = i +1;
#                                     graphresults.append(""+str(i)+", '"+results_row[2]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                     i = i +1;
#                                     graphresults.append(""+str(i)+", '"+results_row[3]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                     i = i +1;
#                                     graphresults.append(""+str(i)+", '"+results_row[4]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                     i = i +1;
#                                     graphresults.append(""+str(i)+", '"+results_row[5]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                     i = i +1;
#                                     graphresults.append(""+str(i)+", '"+results_row[6]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                     i = i +1;
#                                     graphresults.append(""+str(i)+", '"+results_row[7]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                     i = i +1;
                            
#                             thirds level of Sub IPs
                            query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
                            PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
                            SELECT  ?labelogg
                            where{
                                ?s rdfs:label '$ENTITY_CODE$' .
                                ?s a owl:Class .
                                ?t rdfs:subClassOf ?s .
                                ?t a owl:Class .
                                ?t rdfs:label ?labelogg .
                                }
                            """
                            if query_with_placeholder != None:
                                new_query=query_with_placeholder.replace("$ENTITY_CODE$",row['labelogg'].toPython())
                                print(new_query)
                                predicate_query = g.query(new_query)
                                for row in predicate_query:
                                    regexTemp = row['labelogg'].toPython()
                                    print("Sub IPs3: "+regexTemp+"\n");
                                    graphresults.append(""+str(i)+", '"+regexTemp+"', "+str(subIP_parent2)+", 1,  purple\n")
                                    subIP_parent3 = i;
                                    i = i +1;
                                    for results_row in Final_results:
                                        if((regexTemp+'|'+ipnumber+':'+ipname)  in results_row):
                                            print(results_row[0])
                                            graphresults.append(""+str(i)+", '"+results_row[0]+"', "+str(subIP_parent3)+", 1,  blue\n")
                                            i = i +1;
                                            a= (results_row[0]+"::"+results_row[1]+"::"+results_row[2]+"::"+results_row[3]+"::"+results_row[4]+"::"+results_row[5]+"::"+results_row[6]+"::"+results_row[7]+"::"+results_row[8]+"::")
                                            for jcount in range(9,len(results_row)-1): 
                                                a+=(results_row[jcount]+",")
                                            a+=("\n");
                                            text = a

                                            if( text not in FoundBiologyText):
                                                FoundBiologyText.append(text);
                                              #  graphresults.append(""+str(i)+", '"+results_row[1]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                             i = i +1;
#                                             graphresults.append(""+str(i)+", '"+results_row[2]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                             i = i +1;
#                                             graphresults.append(""+str(i)+", '"+results_row[3]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                             i = i +1;
#                                             graphresults.append(""+str(i)+", '"+results_row[4]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                             i = i +1;
#                                             graphresults.append(""+str(i)+", '"+results_row[5]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                             i = i +1;
#                                             graphresults.append(""+str(i)+", '"+results_row[6]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                             i = i +1;
#                                             graphresults.append(""+str(i)+", '"+results_row[7]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                             i = i +1;




    # Start of Narrow variable rabbit hole
    query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
    PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
    SELECT  ?narowervariable
    where{
    <$ENTITY_CODE$> skos:narrower ?narowervariable .

    }
    """
    if query_with_placeholder != None:
        new_query=query_with_placeholder.replace("$ENTITY_CODE$",query)
        print(new_query)
        predicate_query = g.query(new_query)

        for row in predicate_query:
            regexTemp = re.sub(r'.*#', "", row['narowervariable'].toPython())

            print("narowervariable0: "+regexTemp+"\n");
            NarowerVariable = row['narowervariable'].toPython()
            name = regexTemp
            graphresults.append(""+str(i)+", '"+name+"', "+str(parent)+", 1, green\n")
            parent2 = i
            i = i +1;

            # IP variables for the level 0 of narrow variables
            query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
            PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
            SELECT   ?ipNames ?ipnumbers ?ipvalues
            where{
            <$ENTITY_CODE$> rdf:type ?ipvalues .
            ?ipvalues rdfs:label ?ipNames .
            ?ipvalues BMOKernel:TRIZ_reference ?ipnumbers

            }
            """
            if query_with_placeholder != None:
                new_query=query_with_placeholder.replace("$ENTITY_CODE$",NarowerVariable)
                print(new_query)
                predicate_query = g.query(new_query)

                for row in predicate_query:
                    print("NarowerVariable0 : ipname: "+ row['ipNames'].toPython()+"\n" + "ipnumber: "+row['ipnumbers'].toPython()+"\n")
                    name = row['ipNames'].toPython() + " ("+row['ipnumbers'].toPython().replace(' ', '')+")"
                    graphresults.append(""+str(i)+", '"+name+"', "+str(parent2)+", 1, red\n")
                    parentIP = i
                    i = i +1;
                    ipname = row['ipNames'].toPython()
                    ipnumber = row['ipnumbers'].toPython()
#                     first level of Sub IP
                    query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
                    PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
                    SELECT  ?labelogg
                    where{
                        ?s rdfs:label '$ENTITY_CODE$' .
                        ?s a owl:Class .
                        ?t rdfs:subClassOf ?s .
                        ?t a owl:Class .
                        ?t rdfs:label ?labelogg .
                        }
                    """
                    if query_with_placeholder != None:
                        new_query=query_with_placeholder.replace("$ENTITY_CODE$",row['ipNames'].toPython())
                        print(new_query)
                        predicate_query = g.query(new_query)
                        for row in predicate_query:
                            regexTemp = row['labelogg'].toPython()
                            print("Sub IPs1: "+regexTemp+"\n");
                            graphresults.append(""+str(i)+", '"+regexTemp+"', "+str(parentIP)+", 1,  purple\n")
                            subIP_parent = i
                            i = i +1;
                            
                            for results_row in Final_results:
#                                 print (results_row)
                                if((regexTemp+'|'+ipnumber+':'+ipname)  in results_row):
                                    print(results_row[0])
                                    graphresults.append(""+str(i)+", '"+results_row[0]+"', "+str(subIP_parent)+", 1,  blue\n")
                                    i = i +1;
                                    a= (results_row[0]+"::"+results_row[1]+"::"+results_row[2]+"::"+results_row[3]+"::"+results_row[4]+"::"+results_row[5]+"::"+results_row[6]+"::"+results_row[7]+"::"+results_row[8]+"::")
                                    for jcount in range(9,len(results_row)-1): 
                                        a+=(results_row[jcount]+",")
                                    a+=("\n");
                                    text = a

                                    if( text not in FoundBiologyText):
                                        FoundBiologyText.append(text);
                                  
                                    # graphresults.append(""+str(i)+", '"+results_row[1]+"', "+str(subIP_parent)+", 1,  blue\n")
#                                     i = i +1;
#                                     graphresults.append(""+str(i)+", '"+results_row[2]+"', "+str(subIP_parent)+", 1,  blue\n")
#                                     i = i +1;
#                                     graphresults.append(""+str(i)+", '"+results_row[3]+"', "+str(subIP_parent)+", 1,  blue\n")
#                                     i = i +1;
#                                     graphresults.append(""+str(i)+", '"+results_row[4]+"', "+str(subIP_parent)+", 1,  blue\n")
#                                     i = i +1;
#                                     graphresults.append(""+str(i)+", '"+results_row[5]+"', "+str(subIP_parent)+", 1,  blue\n")
#                                     i = i +1;
#                                     graphresults.append(""+str(i)+", '"+results_row[6]+"', "+str(subIP_parent)+", 1,  blue\n")
#                                     i = i +1;
#                                     graphresults.append(""+str(i)+", '"+results_row[7]+"', "+str(subIP_parent)+", 1,  blue\n")
#                                     i = i +1;
                            
#                             second level of Sub IPs
                            query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
                            PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
                            SELECT  ?labelogg
                            where{
                                ?s rdfs:label '$ENTITY_CODE$' .
                                ?s a owl:Class .
                                ?t rdfs:subClassOf ?s .
                                ?t a owl:Class .
                                ?t rdfs:label ?labelogg .
                                }
                            """
                            if query_with_placeholder != None:
                                new_query=query_with_placeholder.replace("$ENTITY_CODE$",row['labelogg'].toPython())
                                print(new_query)
                                predicate_query = g.query(new_query)
                                for row in predicate_query:
                                    regexTemp = row['labelogg'].toPython()
                                    print("Sub IPs2: "+regexTemp+"\n");
                                    graphresults.append(""+str(i)+", '"+regexTemp+"', "+str(subIP_parent)+", 1,  purple\n")
                                    subIP_parent2 = i
                                    i = i +1;
                                    for results_row in Final_results:
                                        if((regexTemp+'|'+ipnumber+':'+ipname)  in results_row):
                                            print(results_row[0])
                                            graphresults.append(""+str(i)+", '"+results_row[0]+"', "+str(subIP_parent2)+", 1,  blue\n")
                                            i = i +1;
                                            a= (results_row[0]+"::"+results_row[1]+"::"+results_row[2]+"::"+results_row[3]+"::"+results_row[4]+"::"+results_row[5]+"::"+results_row[6]+"::"+results_row[7]+"::"+results_row[8]+"::")
                                            for jcount in range(9,len(results_row)-1): 
                                                a+=(results_row[jcount]+",")
                                            a+=("\n");
                                            text = a

                                            if( text not in FoundBiologyText):
                                                FoundBiologyText.append(text);
                                           
                                            # graphresults.append(""+str(i)+", '"+results_row[1]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                             i = i +1;
#                                             graphresults.append(""+str(i)+", '"+results_row[2]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                             i = i +1;
#                                             graphresults.append(""+str(i)+", '"+results_row[3]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                             i = i +1;
#                                             graphresults.append(""+str(i)+", '"+results_row[4]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                             i = i +1;
#                                             graphresults.append(""+str(i)+", '"+results_row[5]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                             i = i +1;
#                                             graphresults.append(""+str(i)+", '"+results_row[6]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                             i = i +1;
#                                             graphresults.append(""+str(i)+", '"+results_row[7]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                             i = i +1;
                                    
#                                     thirds level of Sub IPs
                                    query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
                                    PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
                                    SELECT  ?labelogg
                                    where{
                                        ?s rdfs:label '$ENTITY_CODE$' .
                                        ?s a owl:Class .
                                        ?t rdfs:subClassOf ?s .
                                        ?t a owl:Class .
                                        ?t rdfs:label ?labelogg .
                                        }
                                    """
                                    if query_with_placeholder != None:
                                        new_query=query_with_placeholder.replace("$ENTITY_CODE$",row['labelogg'].toPython())
                                        print(new_query)
                                        predicate_query = g.query(new_query)
                                        for row in predicate_query:
                                            regexTemp = row['labelogg'].toPython()
                                            print("Sub IPs3: "+regexTemp+"\n");
                                            graphresults.append(""+str(i)+", '"+regexTemp+"', "+str(subIP_parent2)+", 1,  purple\n")
                                            subIP_parent3 = i;
                                            i = i +1;
                                            for results_row in Final_results:
                                               if((regexTemp+'|'+ipnumber+':'+ipname)  in results_row):
                                                    print(results_row[0])
                                                    graphresults.append(""+str(i)+", '"+results_row[0]+"', "+str(subIP_parent3)+", 1,  blue\n")
                                                    i = i +1;
                                                    a= (results_row[0]+"::"+results_row[1]+"::"+results_row[2]+"::"+results_row[3]+"::"+results_row[4]+"::"+results_row[5]+"::"+results_row[6]+"::"+results_row[7]+"::"+results_row[8]+"::")
                                                    for jcount in range(9,len(results_row)-1): 
                                                        a+=(results_row[jcount]+",")
                                                    a+=("\n");
                                                    text = a

                                                    if( text not in FoundBiologyText):
                                                        FoundBiologyText.append(text);
                                                    
                                                    
                                                    # graphresults.append(""+str(i)+", '"+results_row[1]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                                     i = i +1;
#                                                     graphresults.append(""+str(i)+", '"+results_row[2]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                                     i = i +1;
#                                                     graphresults.append(""+str(i)+", '"+results_row[3]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                                     i = i +1;
#                                                     graphresults.append(""+str(i)+", '"+results_row[4]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                                     i = i +1;
#                                                     graphresults.append(""+str(i)+", '"+results_row[5]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                                     i = i +1;
#                                                     graphresults.append(""+str(i)+", '"+results_row[6]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                                     i = i +1;
#                                                     graphresults.append(""+str(i)+", '"+results_row[7]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                                     i = i +1;


            # Narrow Section goes 3 level deep and finds concepts and possible invertive principles
            query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
            PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
            SELECT  ?narowervariable
            where{
            <$ENTITY_CODE$> skos:narrower ?narowervariable .

            }
            """
            if query_with_placeholder != None:
                new_query=query_with_placeholder.replace("$ENTITY_CODE$",NarowerVariable)
                print(new_query)
                predicate_query = g.query(new_query)

                for row in predicate_query:
                    regexTemp = re.sub(r'.*#', "", row['narowervariable'].toPython())
                    print("narowervariable1: "+regexTemp+"\n")
                    NarowerVariable2 = row['narowervariable'].toPython()

                    name = regexTemp
                    graphresults.append(""+str(i)+", '"+name+"', "+str(parent2)+", 1, orange\n")
                    parent3 = i
                    i = i +1;
                    

                    print(parent2)
                    # IP variables for the level 1 of narrow variables
                    query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
                    PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
                    SELECT  ?broadervariable ?ipNames ?ipnumbers ?narowervariable ?topScheme ?ipvalues
                    where{
                    <$ENTITY_CODE$> rdf:type ?ipvalues .
                    ?ipvalues rdfs:label ?ipNames .
                    ?ipvalues BMOKernel:TRIZ_reference ?ipnumbers

                    }
                    """
                    if query_with_placeholder != None:
                        new_query=query_with_placeholder.replace("$ENTITY_CODE$",NarowerVariable2)
                        # print(new_query)
                        predicate_query = g.query(new_query)

                        for row in predicate_query:

                            print("NarowerVariable1 : ipname: "+ row['ipNames'].toPython()+"\n" + "ipnumber: "+row['ipnumbers'].toPython()+"\n")
                            name = row['ipNames'].toPython() + " ("+row['ipnumbers'].toPython().replace(' ', '')+")"
                            graphresults.append(""+str(i)+", '"+name+"', "+str(parent3)+", 1, red\n")
                            parentIP = i
                            i = i +1;
                            ipname = row['ipNames'].toPython()
                            ipnumber = row['ipnumbers'].toPython()

                                #first level of Sub IP
                            query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
                            PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
                            SELECT  ?labelogg
                            where{
                                ?s rdfs:label '$ENTITY_CODE$' .
                                ?s a owl:Class .
                                ?t rdfs:subClassOf ?s .
                                ?t a owl:Class .
                                ?t rdfs:label ?labelogg .
                                }
                            """
                            if query_with_placeholder != None:
                                new_query=query_with_placeholder.replace("$ENTITY_CODE$",row['ipNames'].toPython())
                                print(new_query)
                                predicate_query = g.query(new_query)
                                for row in predicate_query:
                                    regexTemp = row['labelogg'].toPython()
                                    print("Sub IPs1: "+regexTemp+"\n");
                                    graphresults.append(""+str(i)+", '"+regexTemp+"', "+str(parentIP)+", 1,  purple\n")
                                    subIP_parent = i
                                    i = i +1;
                                    for results_row in Final_results:
                                        if((regexTemp+'|'+ipnumber+':'+ipname)  in results_row):
                                            print(results_row[0])
                                            graphresults.append(""+str(i)+", '"+results_row[0]+"', "+str(subIP_parent)+", 1,  blue\n")
                                            i = i +1;
                                            a= (results_row[0]+"::"+results_row[1]+"::"+results_row[2]+"::"+results_row[3]+"::"+results_row[4]+"::"+results_row[5]+"::"+results_row[6]+"::"+results_row[7]+"::"+results_row[8]+"::")
                                            for jcount in range(9,len(results_row)-1): 
                                                a+=(results_row[jcount]+",")
                                            a+=("\n");
                                            text = a

                                            if( text not in FoundBiologyText):
                                                FoundBiologyText.append(text);
                                             #  graphresults.append(""+str(i)+", '"+results_row[1]+"', "+str(subIP_parent)+", 1,  blue\n")
#                                             i = i +1;
#                                             graphresults.append(""+str(i)+", '"+results_row[2]+"', "+str(subIP_parent)+", 1,  blue\n")
#                                             i = i +1;
#                                             graphresults.append(""+str(i)+", '"+results_row[3]+"', "+str(subIP_parent)+", 1,  blue\n")
#                                             i = i +1;
#                                             graphresults.append(""+str(i)+", '"+results_row[4]+"', "+str(subIP_parent)+", 1,  blue\n")
#                                             i = i +1;
#                                             graphresults.append(""+str(i)+", '"+results_row[5]+"', "+str(subIP_parent)+", 1,  blue\n")
#                                             i = i +1;
#                                             graphresults.append(""+str(i)+", '"+results_row[6]+"', "+str(subIP_parent)+", 1,  blue\n")
#                                             i = i +1;
#                                             graphresults.append(""+str(i)+", '"+results_row[7]+"', "+str(subIP_parent)+", 1,  blue\n")
#                                             i = i +1;
                                    
#                                     second level of Sub IPs
                                    query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
                                    PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
                                    SELECT  ?labelogg
                                    where{
                                        ?s rdfs:label '$ENTITY_CODE$' .
                                        ?s a owl:Class .
                                        ?t rdfs:subClassOf ?s .
                                        ?t a owl:Class .
                                        ?t rdfs:label ?labelogg .
                                        }
                                    """
                                    if query_with_placeholder != None:
                                        new_query=query_with_placeholder.replace("$ENTITY_CODE$",row['labelogg'].toPython())
                                        print(new_query)
                                        predicate_query = g.query(new_query)
                                        for row in predicate_query:
                                            regexTemp = row['labelogg'].toPython()
                                            print("Sub IPs2: "+regexTemp+"\n");
                                            graphresults.append(""+str(i)+", '"+regexTemp+"', "+str(subIP_parent)+", 1,  purple\n")
                                            subIP_parent2 = i
                                            i = i +1;
                                            for results_row in Final_results:
                                                if((regexTemp+'|'+ipnumber+':'+ipname)  in results_row):
                                                    print(results_row[0])
                                                    graphresults.append(""+str(i)+", '"+results_row[0]+"', "+str(subIP_parent2)+", 1,  blue\n")
                                                    i = i +1;
                                                    a= (results_row[0]+"::"+results_row[1]+"::"+results_row[2]+"::"+results_row[3]+"::"+results_row[4]+"::"+results_row[5]+"::"+results_row[6]+"::"+results_row[7]+"::"+results_row[8]+"::")
                                                    for jcount in range(9,len(results_row)-1): 
                                                        a+=(results_row[jcount]+",")
                                                    a+=("\n");
                                                    text = a

                                                    if( text not in FoundBiologyText):
                                                        FoundBiologyText.append(text);
                                                     #  graphresults.append(""+str(i)+", '"+results_row[1]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                                     i = i +1;
#                                                     graphresults.append(""+str(i)+", '"+results_row[2]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                                     i = i +1;
#                                                     graphresults.append(""+str(i)+", '"+results_row[3]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                                     i = i +1;
#                                                     graphresults.append(""+str(i)+", '"+results_row[4]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                                     i = i +1;
#                                                     graphresults.append(""+str(i)+", '"+results_row[5]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                                     i = i +1;
#                                                     graphresults.append(""+str(i)+", '"+results_row[6]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                                     i = i +1;
#                                                     graphresults.append(""+str(i)+", '"+results_row[7]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                                     i = i +1;
                                            
#                                             thirds level of Sub IPs
                                            query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
                                            PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
                                            SELECT  ?labelogg
                                            where{
                                                ?s rdfs:label '$ENTITY_CODE$' .
                                                ?s a owl:Class .
                                                ?t rdfs:subClassOf ?s .
                                                ?t a owl:Class .
                                                ?t rdfs:label ?labelogg .
                                                }
                                            """
                                            if query_with_placeholder != None:
                                                new_query=query_with_placeholder.replace("$ENTITY_CODE$",row['labelogg'].toPython())
                                                print(new_query)
                                                predicate_query = g.query(new_query)
                                                for row in predicate_query:
                                                    regexTemp = row['labelogg'].toPython()
                                                    print("Sub IPs3: "+regexTemp+"\n");
                                                    graphresults.append(""+str(i)+", '"+regexTemp+"', "+str(subIP_parent2)+", 1,  purple\n")
                                                    subIP_parent3 = i
                                                    i = i +1;
                                                    for results_row in Final_results:
                                                        if((regexTemp+'|'+ipnumber+':'+ipname)  in results_row):
                                                            print(results_row[0])
                                                            graphresults.append(""+str(i)+", '"+results_row[0]+"', "+str(subIP_parent3)+", 1,  blue\n")
                                                            i = i +1;
                                                            a= (results_row[0]+"::"+results_row[1]+"::"+results_row[2]+"::"+results_row[3]+"::"+results_row[4]+"::"+results_row[5]+"::"+results_row[6]+"::"+results_row[7]+"::"+results_row[8]+"::")
                                                            for jcount in range(9,len(results_row)-1): 
                                                                a+=(results_row[jcount]+",")
                                                            a+=("\n");
                                                            text = a

                                                            if( text not in FoundBiologyText):
                                                                FoundBiologyText.append(text);
                                                             # graphresults.append(""+str(i)+", '"+results_row[1]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                                             i = i +1;
#                                                             graphresults.append(""+str(i)+", '"+results_row[2]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                                             i = i +1;
#                                                             graphresults.append(""+str(i)+", '"+results_row[3]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                                             i = i +1;
#                                                             graphresults.append(""+str(i)+", '"+results_row[4]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                                             i = i +1;
#                                                             graphresults.append(""+str(i)+", '"+results_row[5]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                                             i = i +1;
#                                                             graphresults.append(""+str(i)+", '"+results_row[6]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                                             i = i +1;
#                                                             graphresults.append(""+str(i)+", '"+results_row[7]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                                             i = i +1;

                    # Level 2 of Narrower varibles
                    query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
                    PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
                    SELECT  ?narowervariable
                    where{
                    <$ENTITY_CODE$> skos:narrower ?narowervariable .

                    }
                    """
                    if query_with_placeholder != None:
                        new_query=query_with_placeholder.replace("$ENTITY_CODE$",NarowerVariable2)
                        print(new_query)
                        predicate_query = g.query(new_query)

                        for row in predicate_query:
                            regexTemp = re.sub(r'.*#', "", row['narowervariable'].toPython())

                            print("narowervariable2  variable: "+regexTemp+"\n")
                            NarowerVariable3 = row['narowervariable'].toPython()
                            name = regexTemp
                            graphresults.append(""+str(i)+", '"+name+"', "+str(parent2)+", 1, 'orange'\n")
                            parent4 = i
                            i = i +1;


                            # IP variables for the level 2 of narrow variables
                            query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
                            PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
                            SELECT   ?ipNames ?ipnumbers ?ipvalues
                            where{
                            <$ENTITY_CODE$> rdf:type ?ipvalues .
                            ?ipvalues rdfs:label ?ipNames .
                            ?ipvalues BMOKernel:TRIZ_reference ?ipnumbers

                            }
                            """
                            if query_with_placeholder != None:
                                new_query=query_with_placeholder.replace("$ENTITY_CODE$",NarowerVariable3)
                                print(new_query)
                                predicate_query = g.query(new_query)

                                for row in predicate_query:

                                    print("NarowerVariable2 : ipname: "+ row['ipNames'].toPython()+"\n" + "ipnumber: "+row['ipnumbers'].toPython()+"\n")
                                    name = row['ipNames'].toPython() + " ("+row['ipnumbers'].toPython().replace(' ', '')+")"
                                    graphresults.append(""+str(i)+", '"+name+"', "+str(parent4)+", 1, red\n")
                                    parentIP = i
                                    i = i +1;
                                    ipname = row['ipNames'].toPython()
                                    ipnumber = row['ipnumbers'].toPython()
                                   #  if( row['ipvalues'] not in SubIPClassSearch):
#                                         SubIPClassSearch.append(row['ipvalues'])
                                    
                                    #first level of Sub IP
                                    query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
                                    PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
                                    SELECT  ?labelogg
                                    where{
                                        ?s rdfs:label '$ENTITY_CODE$' .
                                        ?s a owl:Class .
                                        ?t rdfs:subClassOf ?s .
                                        ?t a owl:Class .
                                        ?t rdfs:label ?labelogg .
                                        }
                                    """
                                    if query_with_placeholder != None:
                                        new_query=query_with_placeholder.replace("$ENTITY_CODE$",row['ipNames'].toPython())
                                        print(new_query)
                                        predicate_query = g.query(new_query)
                                        for row in predicate_query:
                                            regexTemp = row['labelogg'].toPython()
                                            print("Sub IPs1: "+regexTemp+"\n");
                                            graphresults.append(""+str(i)+", '"+regexTemp+"', "+str(parentIP)+", 1, purple\n")
                                            subIP_parent = i
                                            i = i +1;
                                            for results_row in Final_results:
                                                if((regexTemp+'|'+ipnumber+':'+ipname)  in results_row):
                                                    print(results_row[0])
                                                    graphresults.append(""+str(i)+", '"+results_row[0]+"', "+str(subIP_parent)+", 1,  blue\n")
                                                    i = i +1;
                                                    a= (results_row[0]+"::"+results_row[1]+"::"+results_row[2]+"::"+results_row[3]+"::"+results_row[4]+"::"+results_row[5]+"::"+results_row[6]+"::"+results_row[7]+"::"+results_row[8]+"::")
                                                    for jcount in range(9,len(results_row)-1): 
                                                        a+=(results_row[jcount]+",")
                                                    a+=("\n");
                                                    text = a

                                                    if( text not in FoundBiologyText):
                                                        FoundBiologyText.append(text);
                                                     # graphresults.append(""+str(i)+", '"+results_row[1]+"', "+str(subIP_parent)+", 1,  blue\n")
#                                                     i = i +1;
#                                                     graphresults.append(""+str(i)+", '"+results_row[2]+"', "+str(subIP_parent)+", 1,  blue\n")
#                                                     i = i +1;
#                                                     graphresults.append(""+str(i)+", '"+results_row[3]+"', "+str(subIP_parent)+", 1,  blue\n")
#                                                     i = i +1;
#                                                     graphresults.append(""+str(i)+", '"+results_row[4]+"', "+str(subIP_parent)+", 1,  blue\n")
#                                                     i = i +1;
#                                                     graphresults.append(""+str(i)+", '"+results_row[5]+"', "+str(subIP_parent)+", 1,  blue\n")
#                                                     i = i +1;
#                                                     graphresults.append(""+str(i)+", '"+results_row[6]+"', "+str(subIP_parent)+", 1,  blue\n")
#                                                     i = i +1;
#                                                     graphresults.append(""+str(i)+", '"+results_row[7]+"', "+str(subIP_parent)+", 1,  blue\n")
#                                                     i = i +1;
                                            
#                                             second level of Sub IPs
                                            query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
                                            PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
                                            SELECT  ?labelogg
                                            where{
                                                ?s rdfs:label '$ENTITY_CODE$' .
                                                ?s a owl:Class .
                                                ?t rdfs:subClassOf ?s .
                                                ?t a owl:Class .
                                                ?t rdfs:label ?labelogg .
                                                }
                                            """
                                            if query_with_placeholder != None:
                                                new_query=query_with_placeholder.replace("$ENTITY_CODE$",row['labelogg'].toPython())
                                                print(new_query)
                                                predicate_query = g.query(new_query)
                                                for row in predicate_query:
                                                    regexTemp = row['labelogg'].toPython()
                                                    print("Sub IPs2: "+regexTemp+"\n");
                                                    graphresults.append(""+str(i)+", '"+regexTemp+"', "+str(subIP_parent)+", 1,  purple\n")
                                                    subIP_parent2 = i
                                                    i = i +1;
                                                    for results_row in Final_results:
                                                        if((regexTemp+'|'+ipnumber+':'+ipname)  in results_row):
                                                            print(results_row[0])
                                                            graphresults.append(""+str(i)+", '"+results_row[0]+"', "+str(subIP_parent2)+", 1,  blue\n")
                                                            i = i +1;
                                                            a= (results_row[0]+"::"+results_row[1]+"::"+results_row[2]+"::"+results_row[3]+"::"+results_row[4]+"::"+results_row[5]+"::"+results_row[6]+"::"+results_row[7]+"::"+results_row[8]+"::")
                                                            for jcount in range(9,len(results_row)-1): 
                                                                a+=(results_row[jcount]+",")
                                                            a+=("\n");
                                                            text = a

                                                            if( text not in FoundBiologyText):
                                                                FoundBiologyText.append(text);
                                                             # graphresults.append(""+str(i)+", '"+results_row[1]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                                             i = i +1;
#                                                             graphresults.append(""+str(i)+", '"+results_row[2]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                                             i = i +1;
#                                                             graphresults.append(""+str(i)+", '"+results_row[3]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                                             i = i +1;
#                                                             graphresults.append(""+str(i)+", '"+results_row[4]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                                             i = i +1;
#                                                             graphresults.append(""+str(i)+", '"+results_row[5]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                                             i = i +1;
#                                                             graphresults.append(""+str(i)+", '"+results_row[6]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                                             i = i +1;
#                                                             graphresults.append(""+str(i)+", '"+results_row[7]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                                             i = i +1;
                                                    
#                                                     thirds level of Sub IPs
                                                    query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
                                                    PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
                                                    SELECT  ?labelogg
                                                    where{
                                                        ?s rdfs:label '$ENTITY_CODE$' .
                                                        ?s a owl:Class .
                                                        ?t rdfs:subClassOf ?s .
                                                        ?t a owl:Class .
                                                        ?t rdfs:label ?labelogg .
                                                        }
                                                    """
                                                    if query_with_placeholder != None:
                                                        new_query=query_with_placeholder.replace("$ENTITY_CODE$",row['labelogg'].toPython())
                                                        print(new_query)
                                                        predicate_query = g.query(new_query)
                                                        for row in predicate_query:
                                                            regexTemp = row['labelogg'].toPython()
                                                            print("Sub IPs3: "+regexTemp+"\n");
                                                            graphresults.append(""+str(i)+", '"+regexTemp+"', "+str(subIP_parent2)+", 1,  purple\n")
                                                            i = i +1;
                                                            for results_row in Final_results:
                                                                if((regexTemp+'|'+ipnumber+':'+ipname)  in results_row):
                                                                    print(results_row[0])
                                                                    graphresults.append(""+str(i)+", '"+results_row[0]+"', "+str(subIP_parent3)+", 1,  blue\n")
                                                                    i = i +1;
                                                                    a= (results_row[0]+"::"+results_row[1]+"::"+results_row[2]+"::"+results_row[3]+"::"+results_row[4]+"::"+results_row[5]+"::"+results_row[6]+"::"+results_row[7]+"::"+results_row[8]+"::")
                                                                    for jcount in range(9,len(results_row)-1): 
                                                                        a+=(results_row[jcount]+",")
                                                                    a+=("\n");
                                                                    text = a

                                                                    if( text not in FoundBiologyText):
                                                                        FoundBiologyText.append(text);
                                                                     # graphresults.append(""+str(i)+", '"+results_row[1]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                                                     i = i +1;
#                                                                     graphresults.append(""+str(i)+", '"+results_row[2]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                                                     i = i +1;
#                                                                     graphresults.append(""+str(i)+", '"+results_row[3]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                                                     i = i +1;
#                                                                     graphresults.append(""+str(i)+", '"+results_row[4]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                                                     i = i +1;
#                                                                     graphresults.append(""+str(i)+", '"+results_row[5]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                                                     i = i +1;
#                                                                     graphresults.append(""+str(i)+", '"+results_row[6]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                                                     i = i +1;
#                                                                     graphresults.append(""+str(i)+", '"+results_row[7]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                                                     i = i +1;



                            query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
                            PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
                            SELECT  ?narowervariable
                            where{
                            <$ENTITY_CODE$> skos:narrower ?narowervariable .

                            }
                            """
                            if query_with_placeholder != None:
                                new_query=query_with_placeholder.replace("$ENTITY_CODE$",NarowerVariable3)
                                print(new_query)
                                predicate_query = g.query(new_query)

                                for row in predicate_query:
                                    regexTemp = re.sub(r'.*#', "", row['narowervariable'].toPython())

                                    print("narowervariable3  variable"+regexTemp+"\n")
                                    NarowerVariable4 = row['narowervariable'].toPython()
                                    name = regexTemp
                                    graphresults.append(""+str(i)+", '"+name+"', "+str(parent2)+", 1, grey\n")
                                    parent5 = i
                                    i = i +1;

                                    # IP variables for the level 2 of narrow variables
                                    query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
                                    PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
                                    SELECT ?ipNames ?ipnumbers ?ipvalues
                                    where{
                                    <$ENTITY_CODE$> rdf:type ?ipvalues .
                                    ?ipvalues rdfs:label ?ipNames .
                                    ?ipvalues BMOKernel:TRIZ_reference ?ipnumbers

                                    }
                                    """
                                    if query_with_placeholder != None:
                                        new_query=query_with_placeholder.replace("$ENTITY_CODE$",NarowerVariable4)
                                        print(new_query)
                                        predicate_query = g.query(new_query)

                                        for row in predicate_query:

                                            print("NarowerVariable3 : ipname: "+ row['ipNames'].toPython()+"\n" + "ipnumber: "+row['ipnumbers'].toPython()+"\n")
                                            name = row['ipNames'].toPython() + " ("+row['ipnumbers'].toPython().replace(' ', '')+")"
                                            graphresults.append(""+str(i)+", '"+name+"', "+str(parent5)+", 1, red\n")
                                            parentIP = i
                                            i = i +1;
                                            ipname = row['ipNames'].toPython()
                                            ipnumber = row['ipnumbers'].toPython()
#                                             if( row['ipvalues'] not in SubIPClassSearch):
#                                                 SubIPClassSearch.append(row['ipvalues'])
                                            
                                            #first level of SubIP
                                            query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
                                            PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
                                            SELECT  ?labelogg
                                            where{
                                                ?s rdfs:label '$ENTITY_CODE$' .
                                                ?s a owl:Class .
                                                ?t rdfs:subClassOf ?s .
                                                ?t a owl:Class .
                                                ?t rdfs:label ?labelogg .
                                                }
                                            """
                                            if query_with_placeholder != None:
                                                new_query=query_with_placeholder.replace("$ENTITY_CODE$",row['ipNames'].toPython())
                                                print(new_query)
                                                predicate_query = g.query(new_query)
                                                for row in predicate_query:
                                                    regexTemp = row['labelogg'].toPython()
                                                    print("Sub IPs1: "+regexTemp+"\n");
                                                    graphresults.append(""+str(i)+", '"+regexTemp+"', "+str(parentIP)+", 1, purple\n")
                                                    subIP_parent = i
                                                    i = i +1;
                                                    for results_row in Final_results:
                                                        if((regexTemp+'|'+ipnumber+':'+ipname)  in results_row):
                                                            print(results_row[0])
                                                            graphresults.append(""+str(i)+", '"+results_row[0]+"', "+str(subIP_parent)+", 1,  blue\n")
                                                            i = i +1;
                                                            a= (results_row[0]+"::"+results_row[1]+"::"+results_row[2]+"::"+results_row[3]+"::"+results_row[4]+"::"+results_row[5]+"::"+results_row[6]+"::"+results_row[7]+"::"+results_row[8]+"::")
                                                            for jcount in range(9,len(results_row)-1): 
                                                                a+=(results_row[jcount]+",")
                                                            a+=("\n");
                                                            text = a

                                                            if( text not in FoundBiologyText):
                                                                FoundBiologyText.append(text);
                                                             # graphresults.append(""+str(i)+", '"+results_row[1]+"', "+str(subIP_parent)+", 1,  blue\n")
#                                                             i = i +1;
#                                                             graphresults.append(""+str(i)+", '"+results_row[2]+"', "+str(subIP_parent)+", 1,  blue\n")
#                                                             i = i +1;
#                                                             graphresults.append(""+str(i)+", '"+results_row[3]+"', "+str(subIP_parent)+", 1,  blue\n")
#                                                             i = i +1;
#                                                             graphresults.append(""+str(i)+", '"+results_row[4]+"', "+str(subIP_parent)+", 1,  blue\n")
#                                                             i = i +1;
#                                                             graphresults.append(""+str(i)+", '"+results_row[5]+"', "+str(subIP_parent)+", 1,  blue\n")
#                                                             i = i +1;
#                                                             graphresults.append(""+str(i)+", '"+results_row[6]+"', "+str(subIP_parent)+", 1,  blue\n")
#                                                             i = i +1;
#                                                             graphresults.append(""+str(i)+", '"+results_row[7]+"', "+str(subIP_parent)+", 1,  blue\n")
#                                                             i = i +1;
                                                    
#                                                     second level of Sub IPs
                                                    query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
                                                    PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
                                                    SELECT  ?labelogg
                                                    where{
                                                        ?s rdfs:label '$ENTITY_CODE$' .
                                                        ?s a owl:Class .
                                                        ?t rdfs:subClassOf ?s .
                                                        ?t a owl:Class .
                                                        ?t rdfs:label ?labelogg .
                                                        }
                                                    """
                                                    if query_with_placeholder != None:
                                                        new_query=query_with_placeholder.replace("$ENTITY_CODE$",row['labelogg'].toPython())
                                                        print(new_query)
                                                        predicate_query = g.query(new_query)
                                                        for row in predicate_query:
                                                            regexTemp = row['labelogg'].toPython()
                                                            print("Sub IPs2: "+regexTemp+"\n");
                                                            graphresults.append(""+str(i)+", '"+regexTemp+"', "+str(subIP_parent)+", 1,  purple\n")
                                                            subIP_parent2 = i
                                                            i = i +1;
                                                            for results_row in Final_results:
                                                                if((regexTemp+'|'+ipnumber+':'+ipname)  in results_row):
                                                                    print(results_row[0])
                                                                    graphresults.append(""+str(i)+", '"+results_row[0]+"', "+str(subIP_parent2)+", 1,  blue\n")
                                                                    i = i +1;
                                                                    a= (results_row[0]+"::"+results_row[1]+"::"+results_row[2]+"::"+results_row[3]+"::"+results_row[4]+"::"+results_row[5]+"::"+results_row[6]+"::"+results_row[7]+"::"+results_row[8]+"::")
                                                                    for jcount in range(9,len(results_row)-1): 
                                                                        a+=(results_row[jcount]+",")
                                                                    a+=("\n");
                                                                    text = a

                                                                    if( text not in FoundBiologyText):
                                                                        FoundBiologyText.append(text);
                                                                     # graphresults.append(""+str(i)+", '"+results_row[1]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                                                     i = i +1;
#                                                                     graphresults.append(""+str(i)+", '"+results_row[2]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                                                     i = i +1;
#                                                                     graphresults.append(""+str(i)+", '"+results_row[3]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                                                     i = i +1;
#                                                                     graphresults.append(""+str(i)+", '"+results_row[4]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                                                     i = i +1;
#                                                                     graphresults.append(""+str(i)+", '"+results_row[5]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                                                     i = i +1;
#                                                                     graphresults.append(""+str(i)+", '"+results_row[6]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                                                     i = i +1;
#                                                                     graphresults.append(""+str(i)+", '"+results_row[7]+"', "+str(subIP_parent2)+", 1,  blue\n")
#                                                                     i = i +1;
                                                            
#                                                             thirds level of Sub IPs
                                                            query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
                                                            PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
                                                            SELECT  ?labelogg
                                                            where{
                                                                ?s rdfs:label '$ENTITY_CODE$' .
                                                                ?s a owl:Class .
                                                                ?t rdfs:subClassOf ?s .
                                                                ?t a owl:Class .
                                                                ?t rdfs:label ?labelogg .
                                                                }
                                                            """
                                                            if query_with_placeholder != None:
                                                                new_query=query_with_placeholder.replace("$ENTITY_CODE$",row['labelogg'].toPython())
                                                                print(new_query)
                                                                predicate_query = g.query(new_query)
                                                                for row in predicate_query:
                                                                    regexTemp = row['labelogg'].toPython()
                                                                    print("Sub IPs3: "+regexTemp+"\n");
                                                                    graphresults.append(""+str(i)+", '"+regexTemp+"', "+str(subIP_parent2)+", 1,  purple\n")
                                                                    subIP_parent3 = i;
                                                                    i = i +1;
                                                                    for results_row in Final_results:
                                                                        if((regexTemp+'|'+ipnumber+':'+ipname)  in results_row):
                                                                            print(results_row[0])
                                                                            graphresults.append(""+str(i)+", '"+results_row[0]+"', "+str(subIP_parent3)+", 1,  blue\n")
                                                                            i = i +1;
                                                                            a= (results_row[0]+"::"+results_row[1]+"::"+results_row[2]+"::"+results_row[3]+"::"+results_row[4]+"::"+results_row[5]+"::"+results_row[6]+"::"+results_row[7]+"::"+results_row[8]+"::")
                                                                            for jcount in range(9,len(results_row)-1): 
                                                                                a+=(results_row[jcount]+",")
                                                                            a+=("\n");
                                                                            text = a
                        
                                                                            if( text not in FoundBiologyText):
                                                                                FoundBiologyText.append(text);
                                                                           
                                                                             #  graphresults.append(""+str(i)+", '"+results_row[1]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                                                             i = i +1;
#                                                                             graphresults.append(""+str(i)+", '"+results_row[2]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                                                             i = i +1;
#                                                                             graphresults.append(""+str(i)+", '"+results_row[3]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                                                             i = i +1;
#                                                                             graphresults.append(""+str(i)+", '"+results_row[4]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                                                             i = i +1;
#                                                                             graphresults.append(""+str(i)+", '"+results_row[5]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                                                             i = i +1;
#                                                                             graphresults.append(""+str(i)+", '"+results_row[6]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                                                             i = i +1;
#                                                                             graphresults.append(""+str(i)+", '"+results_row[7]+"', "+str(subIP_parent3)+", 1,  blue\n")
#                                                                             i = i +1;



if questionType=='Noun':
    getNoun(questionVariable)

elif questionType=='Function':
    getNoun2('speed-accuracy_trade_offs')
    getNoun2('cost-benefit_trade_offs')
    getNoun2('load-strength_trade_offs')
    getNoun2('reproduction-immunity_trade_offs')
    getNoun2('resolution-sensitivity_trade_offs')
    getNoun2('safety-efficiency_trade_offs')
    getNoun2('speed-energy_trade_offs')
    getNoun2('survival-reproduction_trade_offs')
    getNoun2('tolerance-defence_trade_offs')
    
    print('getNouns')
    query = "http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#"+questionVariable;
    query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
    PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
    SELECT  ?topScheme
    where{
    <$ENTITY_CODE$> skos:inScheme ?topScheme.
    }
    """
    if query_with_placeholder != None:
        new_query=query_with_placeholder.replace("$ENTITY_CODE$",query)
        print(new_query)
        predicate_query = g.query(new_query)
        for row in predicate_query:
            regexTemp = re.sub(r'.*#', "", row['topScheme'].toPython())
            print("top scheme: " + regexTemp+"\n")
            graphresults.append(""+str(i)+", '"+regexTemp +"', 0, 1, black\n")
            parent =i
            i = i +1;


    query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
    PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
    SELECT  ?topConcepts
    where{
    <$ENTITY_CODE$> skos:hasTopConcept ?topConcepts .
    }
    """
    if query_with_placeholder != None:
        new_query=query_with_placeholder.replace("$ENTITY_CODE$",query)
        print(new_query)
        predicate_query = g.query(new_query)
        for row in predicate_query:
            regexTemp = re.sub(r'.*#', "", row['topConcepts'].toPython())

            print("hasTopConcept: "+ regexTemp+"\n")
            graphresults.append(""+str(i)+", '"+regexTemp +"', 0, 1, black\n")
            parent =i
            i = i +1;
            conceptSchemeFlag = True;

            flag=True;
            query = "http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#"+regexTemp;
            func(parent,query);



    query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
    PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
    SELECT  ?broadervariable
    where{
    <$ENTITY_CODE$> skos:broader ?broadervariable .
    }
    """
    if query_with_placeholder != None:
        new_query=query_with_placeholder.replace("$ENTITY_CODE$",query)
        print(new_query)
        predicate_query = g.query(new_query)

        for row in predicate_query:
            regexTempb = re.sub(r'.*#', "", row['broadervariable'].toPython())

            print("broadervariable: "+regexTempb+"\n")
            broaderVariable= row['broadervariable'].toPython();


            query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
            PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
            SELECT  ?topScheme
            where{
            <$ENTITY_CODE$> skos:inScheme ?topScheme.
            }
            """
            if query_with_placeholder != None:
                new_query=query_with_placeholder.replace("$ENTITY_CODE$",broaderVariable)
                print(new_query)
                predicate_query = g.query(new_query)
                for row in predicate_query:
                    regexTemp = re.sub(r'.*#', "", row['topScheme'].toPython())

                    print("broadervariable top scheme: " + regexTemp+"\n")
                    graphresults.append(""+str(i)+", '"+regexTemp +"', 0, 1, black\n")
                    parent =i
                    i = i +1;

                    graphresults.append(""+str(i)+", '"+regexTempb +"', "+str(parent)+", 1, black\n")
                    parent =i
                    i = i +1;

                    graphresults.append(""+str(i)+", '"+questionVariable +"', "+str(parent)+", 1, orange\n")
                    parent =i
                    i = i +1;

                    flag=True;
                    query = "http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#"+questionVariable;
                    func(parent,query);

            query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
            PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
            SELECT  ?broadervariable
            where{
            <$ENTITY_CODE$> skos:broader ?broadervariable .
            }
            """
            if query_with_placeholder != None:
                new_query=query_with_placeholder.replace("$ENTITY_CODE$",broaderVariable)
                # print(new_query)
                predicate_query = g.query(new_query)

                for row in predicate_query:
                    regexTempb2 = re.sub(r'.*#', "", row['broadervariable'].toPython())

                    print("broadervariable: "+regexTempb2+"\n")
                    broaderVariable2= row['broadervariable'].toPython();


                    query_with_placeholder=""" PREFIX obo_term: <http://purl.obolibrary.org/obo/>
                    PREFIX rdf_about: <http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#>
                    SELECT  ?topScheme
                    where{
                    <$ENTITY_CODE$> skos:inScheme ?topScheme.
                    }
                    """
                    if query_with_placeholder != None:
                        new_query=query_with_placeholder.replace("$ENTITY_CODE$",broaderVariable2)
                        print(new_query)
                        predicate_query = g.query(new_query)
                        for row in predicate_query:
                            regexTemp = re.sub(r'.*#', "", row['topScheme'].toPython())
                            regexTemp2 = re.sub(r'.*#', "", broaderVariable2)
                            regexTempbbb = re.sub(r'.*#', "", broaderVariable)

                            print("broadervariable top scheme: " + regexTemp+"\n")

                            graphresults.append(""+str(i)+", '"+regexTemp +"', 0, 1, black\n")
                            parent =i
                            i = i +1;

                            graphresults.append(""+str(i)+", '"+regexTemp2 +"', "+str(parent)+", 1, black\n")
                            parent =i
                            i = i +1;

                            graphresults.append(""+str(i)+", '"+regexTempbbb +"', "+str(parent)+", 1, green\n")
                            parent =i
                            i = i +1;

                            graphresults.append(""+str(i)+", '"+questionVariable +"', "+str(parent)+", 1, orange\n")
                            parent =i
                            i = i +1;

                            flag=True;
                            query = "http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#"+questionVariable;
                            func(parent,query);
    if(flag==False):
        if(conceptSchemeFlag == False):
            graphresults.append(""+str(i)+", '"+questionVariable +"',"+str(parent)+", 1, orange\n")
            parent = i
            i = i+1
        print("false flag")
        query = "http://www.semanticweb.org/garne/ontologies/2018/4/E2B-SKOS-BMO-kernel#"+questionVariable;
        func(parent,query);



    


f2.writelines("%s"% item for item in FoundBiologyText )
f1.writelines( "%s" % item for item in results )
fgraph.writelines( "%s" % item for item in graphresults )




del FoundBiologyText[:]
del results[:]
del graphresults[:]
del Final_results[:]
f1.close()
f2.close()
fgraph.close()
