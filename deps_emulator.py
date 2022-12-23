import conllu
import os
import re
import matplotlib.pyplot as plt
import pandas as pd



"""
Input: a folder containing all the conllu annotated files by the UDPipe (REST API: https://lindat.mff.cuni.cz/services/udpipe/).
Output:
    - Creates a TOKEN_PER_ROW folder containing all the reannotated files in the TreeTagger specific input format (please read the documentation of TreeTagger).
    - A dictionnary containing two lists, the first one containing the id of the sentences in which there is a "that" re-annotated with WPR and the second one
    containing the id of the sentences in which there is a "that" re-annotated with CST.
"""


# some counting:
nb_acl = 0
nb_aclrelcl = 0
nb_that = 0
nb_that_reannoted = 0
nb_that_WPR = 0
nb_that_CST = 0
nb_vb_relcl_without_that = 0
nb_aclrelcl = 0
nb_tokens = 0
nb_aclrelcl_vb = 0
nb_acl_vb = 0


sentences_reannotated_WPR = [] # the id of the sentences in which there is a "that" re-annotated with WPR
sentences_reannotated_CST = [] # the id of the sentences in which there is a "that" re-annotated with CST

for filename in os.listdir("brown_annotated/"):
    if os.path.isfile("brown_annotated/"+filename):
        # read the conllu file
        data = open("brown_annotated/"+filename, "r", encoding="utf-8")
        annotations = data.read()
        data.close()
        # Transformation of the conllu file into the accepted format of TreeTagger (c.f. the documentation)
        with open("brown_annotated/TOKEN_PER_ROW/token_per_row_"+filename.replace(".conllu", "")+".txt", "w+") as fo:
            sentences = conllu.parse(annotations)
            for i in range(len(sentences)):
                for j in range(len(sentences[i])):
                    nb_tokens += 1
                    if sentences[i][j]['deprel'] == "acl":
                        nb_acl += 1
                    if sentences[i][j]['deprel'] == "acl:relcl":
                        nb_aclrelcl += 1
                        
                        
                    if sentences[i][j]["deps"] != None:
                        deps = "|".join(list(map(lambda x: ":".join(list(reversed(list(map(str, x))))), sentences[i][j]["deps"])))
                    """
                    for each sentence ∈ corpus do
                        for each token ∈ sentence do
                            • If the token is a verb (i.e. XPOS = VB) and is a clausal modifier of noun (i.e. DEPREL
                              = acl) then go steps before that token to see if there is any "that", if so, label it as CST.
                            • If the token is a verb (i.e. XPOS = VB) and is part of a relative clause (i.e. DEPREL =
                              acl:relcl) then go steps before that token to see if there is any "that", if so, label it as WPR.
                        end for
                    end for
                    """                    
                    if(sentences[i][j]['form'].lower() == 'that'):
                        nb_that += 1                    
                    if sentences[i][j]['xpos'] == 'VB' and sentences[i][j]['deprel'] == 'acl': # précédent that à CST
                        nb_acl_vb += 1
                        k = j
                        added = False
                        that_present = False
                        while(k >= 0):
                            if(sentences[i][k]['form'].lower() == 'that'):
                                nb_that_reannoted += 1
                                nb_that_CST += 1
                                sentences[i][k]['xpos'] = "CST"
                                if(not added):
                                    sentences_reannotated_CST.append(sentences[i])
                                    added = True
                                break
                            k -= 1
                    elif sentences[i][j]['xpos'] == 'VB' and sentences[i][j]['deprel'] == 'acl:relcl': # précédent that à WPR
                        nb_aclrelcl_vb += 1
                        k = j
                        that_present = False
                        added = False
                        while(k >= 0):
                            if sentences[i][k]['feats'] != None and 'PronType' in sentences[i][k]['feats']:
                                if sentences[i][k]['feats']['PronType'] == "Rel" and sentences[i][k]['form'].lower() == 'that':
                                    that_present = True
                            if(sentences[i][k]['form'].lower() == 'that'):
                                nb_that_reannoted += 1
                                nb_that_WPR += 1
                                sentences[i][k]['xpos'] = "WPR"
                                if(not added):
                                    sentences_reannotated_WPR.append(sentences[i])
                                    added = True
                                break
                            k -= 1
                        if not that_present:
                            nb_vb_relcl_without_that += 1
                    
            for i in range(len(sentences)):
                for j in range(len(sentences[i])):
                    to_write = sentences[i][j]['form'] + "\t" + sentences[i][j]['xpos'] + "\n"
                    fo.write(to_write)
                    
# Some intersting numbers
print("There are ", nb_that, "'that' in all the 30 files")
print("There are ", nb_that_reannoted, "'that' re-annotated.")
print("There are ", nb_that_CST, "'that' re-annotated with CST.")
print("There are ", nb_that_WPR, "'that' re-annotated with WPR")
print("The number of VB acl:relcl without that before is", nb_vb_relcl_without_that)
print("There are", nb_acl/nb_tokens, "% acl\n", nb_aclrelcl/nb_tokens, "% acl:relcl")
print("There are", nb_aclrelcl_vb, "acl:relcl verbs")
print("There are", nb_acl_vb, "acl verbs")


return {"WPR ID": sentences_reannotated_WPR, "CST ID": sentences_reannotated_CST}