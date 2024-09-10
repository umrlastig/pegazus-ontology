import re
import unidecode
from rdflib import Graph, RDFS, Literal, URIRef
from difflib import SequenceMatcher

def remove_spaces(str_value):
    return str_value.replace(" ", "")

def split_cell_content(cell_content:str, sep=",", remove_spaces=True):
    if cell_content == "" or cell_content is None:
        return []
    
    elems = cell_content.split(sep)
    if remove_spaces:
        return [re.sub("(^ {1,}| {1,}$)", "", x) for x in elems]
    return elems

def remove_abbreviations_from_dict(name:str, abbreviations_dict:dict, entire_match:bool=False):
    normalized_name = name
    for abbre, val in abbreviations_dict.items():
        if entire_match:
            abbre = f"^{abbre}$"
        normalized_name = re.sub(abbre, val, normalized_name)

    return normalized_name

def match_apostrophe(matchobj:re.Match):
    to_replace = re.sub("'{1,}", " ", matchobj.group(0))
    return to_replace

def get_words_list_from_label(label:str, case_option:str=None):
    split_setting = " "
    separated_words = re.sub("[’'ʼ]", "'", label) # Replace apostrophies by only one version
    separated_words = re.sub("[- ]{1,}", " ", label) # Replace dash and spaces by `split_setting`
    separated_words = re.sub("(^| )[a-z]('{1,})", match_apostrophe, separated_words, flags=re.IGNORECASE)

    if case_option == "lower":
        separated_words = separated_words.lower()
    elif case_option == "upper":
        separated_words = separated_words.upper()
    elif case_option == "title":
        separated_words = separated_words.title()
    elif case_option == "capitalize":
        separated_words = separated_words.capitalize()

    words_list = separated_words.split(split_setting)
    return words_list

def normalize_french_commune_name(commune_name:str):
    abbreviations_dict = {"st(\.|)":"saint", "ste(\.|)":"sainte", "sts(\.|)":"saints", "stes(\.|)":"saintes",
                         "chap(\.|)":"chapelle",
                         "gd":"grand", "pt":"petit", "vx":"vieux", 
                        }
    lower_case_words = ["à","au","aux","chez","d","de","derrière","des","dessous","dessus","deux","devant","du","en","entre","ès","et","l","la","le","les","lès","près","sous","sur"]
    words_before_apostrophe = ["d","l"]

    commune_name_words = get_words_list_from_label(commune_name, case_option="lower")
    for i, raw_word in enumerate(commune_name_words):
        if raw_word in lower_case_words:
            is_lower_case_word = True
        else:
            is_lower_case_word = False

        if not is_lower_case_word or i == 0 or next_chr == " ":
            word = remove_abbreviations_from_dict(raw_word, abbreviations_dict, True)
            word = word.capitalize()
        else:
            word = raw_word

        next_chr = "-"
        if i == len(commune_name_words) - 1:
            next_chr = ""
        elif raw_word in words_before_apostrophe:
            next_chr = "'"
        elif i == 0 and is_lower_case_word :
            next_chr = " "
        
        commune_name_words[i] = word + next_chr
   
    return "".join(commune_name_words)

def normalize_french_thoroughfare_name(thoroughfare_name:str):
    abbreviations_dict = {
        "pl(a|)(\.|)":"place",
        "av(\.|)":"avenue",
        "(bd|blvd|boul)(\.|)":"boulevard",
        "bre(\.|)":"barrière",
        "barriere":"barrière",
        "crs(\.|)":"cours",
        "r(\.|)":"rue",
        "rl{1,2}e(\.|)":"ruelle",
        "rte(\.|)":"route",
        "pas(s|)(\.|)": "passage",
        "all(ee|)(\.|)": "allée",
        "imp(\.|)": "impasse",
        "mte(\.|)": "montée",
        "montee ": "montée",
        "r(e|é)s(idence)(\.|)": "résidence",
        "s(\.|)":"saint", "st(\.|)":"saint", "ste(\.|)":"sainte", "sts(\.|)":"saints", "stes(\.|)":"saintes",
        "mlle(\.|)":"mademoiselle",
        "mme(\.|)":"madame",
        "fg(\.|)":"faubourg",
        "rpt(\.|)":"rond-point",
        "gd(\.|)":"grand",
        "gds(\.|)":"grands",
        "gde(\.|)":"grande",
        "gdes(\.|)":"grandes",
        "pt(\.|)":"petit",
        "pte(\.|)":"petite",
        "pts(\.|)":"petits",
        "vx(\.|)":"vieux",
        "0":"zéro", "1":"un", "2":"deux", "3":"trois", "4":"quatre", "5":"cinq", "6":"six", "7":"sept", "8":"huit", "9":"neuf",
        "10":"dix", "11":"onze", "12":"douze", "13":"treize", "14":"quatorze", "15":"quinze", "16":"seize", "17":"dix-sept", "18":"dix-huit", "19":"dix-neuf",
        "20":"vingt", "30":"trente", "40":"quarante", "50":"cinquante", "60":"soixante", "70":"soixante-dix", "80":"quatre-vingts", "90":"quatre-vingt-dix",
        "100":"cent", "1000":"mille",
    }

    lower_case_words = ["&","a","à","au","aux","d","de","des","du","en","ès","es","et","l","la","le","les","lès","ou","sous","sur"]
    words_before_apostrophe = ["d","l"]
        
    thoroughfare_name_words = get_words_list_from_label(thoroughfare_name, case_option="lower")

    for i, word in enumerate(thoroughfare_name_words):
        word = remove_abbreviations_from_dict(word, abbreviations_dict, True)
        if word not in lower_case_words:
            word = word.capitalize()
        if word in words_before_apostrophe:
            word += "'"
        thoroughfare_name_words[i] = word
    
    normalized_name = " ".join(thoroughfare_name_words)
    normalized_name = normalized_name.replace("' ", "'")
    return normalized_name


def simplify_french_landmark_name(landmark_name:str, keep_spaces=True, keep_diacritics=True, sort_characters=False):
    words_to_remove = ["&","a","à","au","aux","d","de","des","du","en","ès","es","et","l","la","le","les","lès","ou"]
    commune_name_words = get_words_list_from_label(landmark_name, case_option="lower")
    new_commune_name_words = []

    for word in commune_name_words:
        word = word.replace("'", "")
        if word not in words_to_remove:
            if not keep_diacritics:
                word = unidecode.unidecode(word)
            new_commune_name_words.append(word)

    word_sep = ""
    if keep_spaces:
        word_sep = " "

    simplified_name = word_sep.join(new_commune_name_words)

    if sort_characters:
        simplified_name = "".join(sorted(simplified_name))

    return simplified_name


def get_lower_simplified_french_street_name_function(variable:str):
    replacements = [["([- ]de[- ]la[- ]|[- ]de[- ]|[- ]des[- ]|[- ]du[- ]|[- ]le[- ]|[- ]la[- ]|[- ]les[- ]|[- ]aux[- ]|[- ]au[- ]|[- ]à[- ]|[- ]en[- ]|/|-|\\.)", " "],
                ["(l'|d')", ""],
                ["[àâ]", "a"], 
                ["[éèêë]", "e"], 
                ["[îíìï]", "i"], 
                ["[ôö]", "o"], 
                ["[ûüù]", "u"], 
                ["[ÿŷ]", "y"],
                ["[ç]", "c"], 
                ]
    
    lc_variable = f"LCASE({variable})"
    return get_remplacement_sparql_function(lc_variable, replacements)

def get_remplacement_sparql_function(string, replacements):
    # arg, pattern, replacement = string, first_repl[0], first_repl[1]
    # function_str = f"REPLACE({arg}, {pattern}, {replacement})"
    function_str = string
    for repl in replacements:
        arg, pattern, replacement = function_str, repl[0], repl[1]
        pattern = pattern.replace('\\', '\\\\')
        function_str = f"REPLACE({arg}, \"{pattern}\", \"{replacement}\")"

    return function_str

def normalize_street_rdfs_labels_in_graph_file(graph_file:str):
    # Normalisation de noms de voies
    g = Graph()
    g.parse(graph_file)
    triples_to_remove = []
    triples_to_add = []
    for s, p, o in g:
        if p == RDFS.label and isinstance(o, Literal) and o.language == "fr":
            new_o_value = normalize_french_thoroughfare_name(o.value)
            new_o = Literal(new_o_value, lang="fr")
            triples_to_remove.append((s,p,o))
            triples_to_add.append((s, p, new_o))

    for triple in triples_to_remove:
        g.remove(triple)
    for triple in triples_to_add:
        g.add(triple)

    g.serialize(graph_file)

def define_time_filter_for_sparql_query(val_tRef:str, cal_tRef:str, val_t1:str, cal_t1:str, val_t2:str, cal_t2:str, time_precision:URIRef="day"):
    """
    Création d'un filtre temporel pour les requêtes afin de sélectionner des données valables à l'instant `tRef` telles que t2 <= tRef <= t1
    val_tX sont des variables de la requête liées aux timestamps (`?t1Value`, `?t2Value`...)
    cal_tX sont des variables de la requête liées aux calendriers (`?t1Calendar`, `?t2Calendar`...)

    `time_precision` peut prendre les valeurs suivantes : 
    * `URIRef("http://www.w3.org/2006/time#unitYear")` ;
    * `URIRef("http://www.w3.org/2006/time#unitMonth")` ;
    * `URIRef("http://www.w3.org/2006/time#unitDay")`.
    """
    
    t1_get_t2 = "{t1} >= {t2}"
    t1_let_t2 = "{t1} <= {t2}"
    # t1_gt_t2 = "{t1} > {t2}"
    # t1_lt_t2 = "{t1} < {t2}"
    # t1_eq_t2 = "{t1} = {t2}"
    t_not_exists = "!BOUND({t})"
    or_op = "||"
    and_op = "&&"

    t1_get_t2_year = t1_get_t2.format(t1="YEAR({t1})", t2="YEAR({t2})")
    t1_get_t2_month = t1_get_t2.format(t1="MONTH({t1})",t2="MONTH({t2})")
    t1_get_t2_year_month = f"{t1_get_t2_year} {and_op} {t1_get_t2_month}"

    t1_let_t2_year = t1_let_t2.format(t1="YEAR({t1})", t2="YEAR({t2})")
    t1_let_t2_month = t1_let_t2.format(t1="MONTH({t1})", t2="MONTH({t2})")
    t1_let_t2_year_month = f"{t1_let_t2_year} {and_op} {t1_let_t2_month}"

    if time_precision == URIRef("http://www.w3.org/2006/time#unitYear"):
        t1_get_tRef_comp = t1_get_t2_year
        t2_let_tRef_comp = t1_let_t2_year
    elif time_precision == URIRef("http://www.w3.org/2006/time#unitMonth"):
        t1_get_tRef_comp = t1_get_t2_year_month
        t2_let_tRef_comp = t1_let_t2_year_month
    else:
        t1_get_tRef_comp = t1_get_t2
        t2_let_tRef_comp = t1_let_t2

    t1_get_tRef_val = t1_get_tRef_comp.format(t1=val_t1, t2=val_tRef)
    t2_let_tRef_val = t2_let_tRef_comp.format(t1=val_t2, t2=val_tRef)
    t1_not_exists_val = t_not_exists.format(t=val_t1)
    t2_not_exists_val = t_not_exists.format(t=val_t2)
    cal_t1_not_exists_val = t_not_exists.format(t=cal_t1)
    cal_t2_not_exists_val = t_not_exists.format(t=cal_t2)

    calendar_time_filter = f"""(
        (({cal_t1} = {cal_tRef}) {and_op} ({cal_t2} = {cal_tRef})) {or_op}
        (({cal_t1} = {cal_tRef}) {and_op} ({cal_t2_not_exists_val})) {or_op}
        (({cal_t2} = {cal_tRef}) {and_op} ({cal_t1_not_exists_val})) {or_op}
        ({cal_t1_not_exists_val} {and_op} {cal_t2_not_exists_val})
        )"""

    value_time_filter = f"""(
        ({t1_get_tRef_val} {and_op} {t2_let_tRef_val}) {or_op}
        ({t1_get_tRef_val} {and_op} {t2_not_exists_val}) {or_op}
        ({t2_let_tRef_val} {and_op} {t1_not_exists_val}) {or_op}
        ({t1_not_exists_val} {and_op} {t2_not_exists_val})
        )
    """

    time_filter = f"""FILTER({value_time_filter} {and_op} {calendar_time_filter})"""
    return time_filter

def are_similar_names(name_1, name_2, min_score=0.9):
    similarity_score = SequenceMatcher(None, name_1, name_2).ratio()
    if similarity_score >= min_score:
        return True
    return False

def normalize_french_name_version(name_version, name_type):
    if name_type == "housenumber":
        return name_version.lower()
    elif name_type == "thoroughfare":
        return normalize_french_thoroughfare_name(name_version)
    elif name_type == "area":
        return normalize_french_commune_name(name_version)
    else:
        return None
    
def normalize_nolang_name_version(name_version, name_type):
    if name_type == "housenumber":
        return name_version.lower()
    else:
        return None
    
def normalize_name_version(name_version, name_type, name_lang):
    if name_version is None:
        return None
    elif name_lang is None:
        return normalize_nolang_name_version(name_version, name_type)
    elif name_lang == "fr":
        return normalize_french_name_version(name_version, name_type)
    
    return None

def simplify_french_name_version(name_version, name_type):
    if name_type == "housenumber":
        return remove_spaces(name_version)
    elif name_type in ["thoroughfare", "area"]:
        return simplify_french_landmark_name(name_version, keep_spaces=False, keep_diacritics=False, sort_characters=True)
    else:
        return None

def simplify_nolang_name_version(name_version, name_type):
    if name_type == "housenumber":
        return remove_spaces(name_version)
    return None

def simplify_name_version(name_version, name_type, name_lang):
    if name_version is None:
        return None
    if name_lang is None:
        return simplify_nolang_name_version(name_version, name_type)
    elif name_lang == "fr":
        return simplify_french_name_version(name_version, name_type)
    
    return None

def normalize_and_simplify_name_version(name_version:str, name_type:str, name_lang:str):
    normalized_name = normalize_name_version(name_version, name_type, name_lang)
    simplified_name = simplify_name_version(normalized_name, name_type, name_lang)

    return normalized_name, simplified_name