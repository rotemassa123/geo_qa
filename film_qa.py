import requests
import lxml.html
import rdflib
import re # for split by two possible delimiters (oocupation) and regex (bday)
import traceback # for tracing errors
import queue # for crawl
import time # to measure running time
import sys #to receive input from command line arguments


### PART 1: Crawler & Extraction from infobox --> Write into ontology ###
start = time.time()

prefix = "http://en.wikipedia.org"
prefix_for_ontology = "http://example.org/"
urls_source = "https://en.wikipedia.org/wiki/List_of_Academy_Award-winning_films"
visited = set()
urls_queue = queue.Queue() # queue of tuples: (Entity_Type, URL) Entity_Type = Film / Person

data_labels_to_extract_1 = ["Directed by", "Produced by", "Based on", "Starring", "Running time"]
unwanted_data = ["\n" , " " , "by " , '"' , ", ", "(" , ")", ": " , "Executive Producer" , " (p.g.a.)"]
g = rdflib.Graph()
count_based_on = 0

def prepare_name(name):
    # prepare name receives name --> removes extra spaces and lowercase
    # returns prepared name
    return name.strip().lower()

def concat_prefix_to_entity_or_property(name):
    return (f"{prefix_for_ontology}{name}")
    # currently not in use

def push_url_to_queue(uri, entity_type):
    # receives uri and push it into urls_queue if not visited
    # to be visited by crawler
    if (f"{prefix}{uri}" not in visited):
        urls_queue.put((entity_type, f"{prefix}{uri}"))
        visited.add(f"{prefix}{uri}")

def create_initial_urls_list():

    # extract from table in urls_source
    # URIs of Academy Award-winning films wikipedia pages
    # won since 2010 (including) - amount of films (URLs): 164

    r = requests.get(urls_source)
    doc = lxml.html.fromstring(r.content)
    for t in doc.xpath('//table[@class="wikitable sortable"]//tr[td[2]/a[number(text())>=2010]]/td[1]//@href'):
    	push_url_to_queue(t, "film")
    # print(urls_queue,"\n total films urls added: ", len(urls_queue), "\n\n")

def replace_spaces_with_underscores(name):
    name = name.replace(" ", "_")
    return name

def name_from_URL(uri):
    # receives uri and returns name of entity with "_"
    # to use when data form infobox is href and entity is person
    names = uri.split("/")
    name = names[-1]
    return name

def extract_label_from_infobox(url, label):

    # receives URL and label --> returning list of infobox-data of received label
    # taking into consideration if text or href

    data = []
    r = requests.get(url)
    doc = lxml.html.fromstring(r.content)
    data_text = doc.xpath('//table[contains(@class, "infobox")]/tbody/tr[th//text()="{}"]/td//text()'.format(label))
    data_with_href = doc.xpath('//table[contains(@class, "infobox")]/tbody/tr[th//text()="{}"]/td//a/@href'.format(label))
    data_with_href_text = doc.xpath('//table[contains(@class, "infobox")]/tbody/tr[th//text()="{}"]/td//a//text()'.format(label))

    # if label is based on --> object will be yes (no specific data)
    if (label == "Based on" and data_text):
        return ["yes"]

    # if data as text and as urls, if data as text not as url --> add data as text
    if len(data_text) > len(data_with_href):
        for d in data_text:
            if d not in data_with_href_text and d not in unwanted_data:
                data.append(replace_spaces_with_underscores(d.strip()))

    # add all data from href
    for t in data_with_href:
        if "#cite" in t or (label == "Running time"):
            continue
        if label in ["Directed by", "Produced by", "Starring"]:
            push_url_to_queue(t, "person") # push relevant hrefs (directors, producers and actors/actresses to urls_queue) identify entity as person
        data.append(name_from_URL(t).strip("_"))
    return data

def extract_date_from_infobox(url, label):
    bday = []
    years = []
    data = []
    r = requests.get(url)
    doc = lxml.html.fromstring(r.content)
    if label == "Release date":
        bday = doc.xpath('//table[contains(@class, "infobox")]/tbody/tr[th//text()="Release date"]//span[@class="bday dtstart published updated"]//text()')
        text_date = doc.xpath('//table[contains(@class, "infobox")]/tbody/tr[th//text()="Release date"]//td//text()')
    if label == "Born":
        bday = doc.xpath('//table[contains(@class, "infobox")]/tbody/tr[th//text()="Born"]//span[@class="bday"]//text()')
        text_date = doc.xpath('//table[contains(@class, "infobox")]/tbody/tr[th//text()="Born"]//td//text()')
    if not bday:
        if text_date:
            year = 0
            for t in text_date:
                year = re.findall('20\d{2}|19\d{2}', t)
                for y in year:
                    years.append(int(y))
            if not years:
                return []
            data.append(str(min(years)))
            return data
    return bday

def extract_occupation_from_infobox(url):
    data = []
    r = requests.get(url)
    doc = lxml.html.fromstring(r.content)
    data_text = doc.xpath('//table[contains(@class, "infobox")]/tbody/tr[th//text()="Occupation"]/td//text()')
    data_with_href = doc.xpath('//table[contains(@class, "infobox")]/tbody/tr[th//text()="Occupation"]/td//a/@href')
    data_with_href_text = doc.xpath('//table[contains(@class, "infobox")]/tbody/tr[th//text()="Occupation"]/td//a//text()')

    for d in data_with_href:
        data.append(prepare_name(name_from_URL(d)))

    for d in data_text:
        if d not in data_with_href_text:
            for o1 in re.split(",|•", d):
                if o1 not in unwanted_data and "mw-parser-output" not in o1 and o1 != '':
                    data.append(prepare_name(o1))

    for o1 in data:
        if (o1 == "\n" or o1 == ''):
            data.remove(o1)
    # print("final:",data,"\n")
    return data

def add_triples_to_ontology(subject, property, data):
    subject = concat_prefix_to_entity_or_property(subject)
    property = concat_prefix_to_entity_or_property(property)
    for d in data:
        d = concat_prefix_to_entity_or_property(replace_spaces_with_underscores(d.strip()))
        g.add((rdflib.URIRef(subject), rdflib.URIRef(property), rdflib.URIRef(d)))
        # print("(", subject, ",", property, ",", d, ")")

def into_ontology_from_url_tuple(entity_url_tuple):
    subject = name_from_URL(entity_url_tuple[1])

    if (entity_url_tuple[0] == "film"):
        for l in data_labels_to_extract_1:
            try:
                property = replace_spaces_with_underscores(l)
                data = extract_label_from_infobox(entity_url_tuple[1], l)
                add_triples_to_ontology(subject, property, data)
            except Exception:
                print("problem with label:",l,"from url:",entity_url_tuple[1])
                traceback.print_exc()
                pass
        try:
            data = extract_date_from_infobox(entity_url_tuple[1], "Release date")
            add_triples_to_ontology(subject, "Release_date", data)
        except Exception:
            print("problem with label:","Release_date","from url:",entity_url_tuple[1])
            traceback.print_exc()
            pass

    elif (entity_url_tuple[0] == "person"):
        try:
            data = extract_date_from_infobox(entity_url_tuple[1], "Born")
            add_triples_to_ontology(subject, "Born", data)
        except Exception:
            print("problem with label:","Born","from url:",entity_url_tuple[1])
            traceback.print_exc()
            pass
        try:
            data = extract_occupation_from_infobox(entity_url_tuple[1])
            add_triples_to_ontology(subject, "Occupation", data)
        except Exception:
            print("problem with label:","Occupation","from url:",entity_url_tuple[1])
            traceback.print_exc()
            pass
    else:
        print("unknown entity")
    print("Done with url: ", entity_url_tuple[1],"\n\n")

def crawl(urls_queue):
    count_for_serialize = 0
    while not urls_queue.empty():
        current_tuple = urls_queue.get()
        # print(current_tuple)
        start2 = time.time()
        into_ontology_from_url_tuple(current_tuple)
        end = time.time()
        print(end - start2)
        count_for_serialize = count_for_serialize + 1
        if count_for_serialize % 50 == 0:
            g.serialize("ontology.nt", format="nt")

def create():
    create_initial_urls_list()
    crawl(urls_queue)
    g.serialize("ontology.nt", format="nt")

if (sys.argv[1] == "create"):
    create()
    end = time.time()
    print(end - start)


### PART 2: Natural language question --> Convert to SPARQL query ###


def create_sparql_query(input_question):
    length=len(input_question)
    #If the question is not general:
    if input_question.find("How_many")==-1:
        #question 1: Who directed <film>?
        if input_question.find("Who_directed")!=-1:
            entity1 = input_question[13:length-1]
            relation = "Directed_by"

        #question 2: Who produced <film>?
        if input_question.find("Who_produced")!=-1:
            entity1 = input_question[13:length-1]
            relation = "Produced_by"

        #question 3: Is <film> based on a book?
        if input_question.find("based_on_a_book")!=-1:
            entity1 = input_question[3:length-17]
            relation = "Based_on"

        #question 4: When was <film> released?
        if input_question.find("released")!=-1:
            entity1 = input_question[9:length-10]
            relation = "Release_date"

        #question 5: How long is <film>?
        if input_question.find("How_long_is")!=-1:
            entity1 = input_question[12:length-1]
            relation = "Running_time"

        #question 6: who starred in <film>?
        if input_question.find("Who_starred_in")!=-1:
            entity1 = input_question[15:length-1]
            relation = "Starring"

        #question 7: Did <person> star in <film>? and our question: Did <person> produce <film>?
        if input_question.find("Did")!=-1:
            if input_question.find("star_in")!=-1:
                temp_str=input_question[4:length-1]
                enteties=temp_str.split("_star_in_")
                entity1 = enteties[0]
                relation = "Starring"
                entity2 = enteties[1]
            elif input_question.find("produce")!=-1:
                temp_str=input_question[4:length-1]
                enteties=temp_str.split("_produce_")
                entity1 = enteties[0]
                relation = "Produced_by"
                entity2 = enteties[1]

        #question 8: When was <person> born?
        if input_question.find("born?")!=-1:
            entity1 = input_question[9:length-6]
            relation = "Born"

        #question 9: What is the occupation of <person>?
        if input_question.find("What_is_the_occupation_of")!=-1:
            entity1 = input_question[26:length-1]
            relation = "Occupation"
        if input_question.find("Did")==-1:
            return "select * where {<http://example.org/"+entity1+"> <http://example.org/"+relation+"> ?a.}"
        else:
            #<film> <starring> <person>
            return "select * where {<http://example.org/"+entity2+"> <http://example.org/"+relation+"> <http://example.org/"+entity1+">.}"
    #If the question is general:
    if input_question.find("How_many_films_are_based_on_books?")!=-1:
        return "select (COUNT(*) AS ?count) where {?a <http://example.org/Based_on> <http://example.org/yes>.}"

    if input_question.find("How_many_films_starring")!=-1:
        entity1 = input_question[24:length-22]
        return "select (COUNT(*) AS ?count) where {?a <http://example.org/Starring> <http://example.org/"+entity1+">.}"

    if input_question.find("are_also")!=-1:
        input_question=input_question[9:length-1]
        occupations = input_question.split("_are_also_")
#        return "select * where {?a <http://example.org/Occupation> <http://example.org/"+occupations[0]+">. ?a <http://example.org/Occupation> <http://example.org/"+occupations[1]+"> .}"
        return "select (COUNT(?a) AS ?count) where {?a <http://example.org/Occupation> <http://example.org/"+occupations[0]+">. ?a <http://example.org/Occupation> <http://example.org/"+occupations[1]+"> .}"
    #If the input question do not match any of the above:
    return "ERROR: illegal question format."


def question():
    input_question = sys.argv[2]
    input_question = replace_spaces_with_underscores(input_question)
    sparql_query = create_sparql_query(input_question)
    g = rdflib.Graph()
    g.parse("ontology.nt", format="nt")
    query_list_result = g.query(sparql_query)

    #Specific entity, question of type 7 and our question:
    if input_question.find("Did")!=-1 :
        if not query_list_result:
#            print("No")
            return "No"
        else:
#            print("Yes")
            return "Yes"

    #Specific entity questions (type 1-6,8,9):
    elif input_question.find("How_many")==-1:
        if input_question.find("based_on_a_book")!=-1:
            if not query_list_result:
#                print("No")
                return "No"
            else:
#                print("Yes")
                return "Yes"
        else:
            res_string = ""
            for i in range (len(list(query_list_result))):
                row = list(query_list_result)[i] # get row i from query list result.
                entity_with_uri = str(row[0])
                entity_with_uri = entity_with_uri.split("/")
                entity_without_uri = entity_with_uri[-1]
                #the next 3 code lines are to strip excessive spaces in the names.
                entity_without_uri = entity_without_uri.replace("_"," ")
                entity_without_uri = entity_without_uri.strip()
                entity_without_uri = entity_without_uri.replace(" ","_")
                res_string += entity_without_uri+" " #get the entity name without the uri.
            names = res_string.split() #split the string to sort the names lexicographically
            names.sort()
            res_string = ""
            for j in range (len(list(names))): #build string of names separated by ', '
                res_string += names[j]+", "
            res_string = res_string[0:len(res_string)-2] #remove the last ', ' in the string
            res_string = res_string.replace("_", " ")
#            print(res_string)
            return res_string
    #General questions:
    else:
#        for k in range (len(list(query_list_result))):
#            print(list(query_list_result)[k])
#        print(list(query_list_result)[0][0])
        return list(query_list_result)[0][0]
if sys.argv[1] == "question":
	print(question())

