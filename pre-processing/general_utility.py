'''
@author: Reem Alatrash
@version: 1.0
=======================

This module has helper functions that are meant to be used by several scripts

'''

'''
******* ********* *********
*******  imports  *********
******* ********* *********
'''

import os
import codecs

'''
******* ********* *********
******* functions *********
******* ********* *********
'''
def get_file_names(dir_path, file_type="all"):
    '''
        Get list of files names inside directory and filter for specific file type if specified.
        
        Paramters
        ---------
        dir_path = path to directory containing files
        [optional] file_type = file extension to be kept. For example: ".txt"
    '''
    result = []
    dir_file_names = os.listdir(dir_path)
    if file_type=="all":
        result = dir_file_names
    else:   
        result = zip_file_names = list(x for x in dir_file_names if file_type in x)
    return result

def write_speakers_to_file(file_path, speakers, encoding="utf-8"):
    '''
        Get list of files names inside directory and filter for specific file type if specified.
        
        Paramters
        ---------
        file_path = path to output file
        data = list of TokenInfo
        isKD = is data from KiDKo corpus (i.e. kiesdeutsch sentence)
        [optional] encoding = encoding for data in output file      
    '''
    with codecs.open(file_path, 'wb+', encoding) as output_file:
        output_file.write("speaker_ID\tGender\tAbbreviation\n")
        for speaker in speakers:
            # serialize and encode data
            formatted_line = "{}\t{}\t{}\n".format(str(speaker.speaker_id), str(speaker.gender), str(speaker.abbreviation))
            output_file.write(formatted_line)   


def get_n_grams(sentence, n):
    '''returns sequences of length n from given a tokenized sentence.
    
       Paramters
       ---------
       sentence = can be list of tokens, types or pos. Can also be a list of (tokens, pos) tuples
       n = size of n-grams
    '''
    
    ngrams = zip(*[sentence[i:] for i in range(n)])
    return ngrams


'''
******* ********* *********
******* Classes *********
******* ********* *********
'''
class Speaker(object):
    
    def __init__(self, speaker_id=None, gender=None, abbreviation=None):
        
        if speaker_id is None:
            self.speaker_id = ''
        else:
            self.speaker_id = speaker_id

        if gender is None:
            self.gender = ''
        else:
            self.gender = gender
            
        if abbreviation is None:
            self.abbreviation = ''
        else:
            self.abbreviation = abbreviation
    # implement __eq__ and __hash__ methods to teach Python about how to recognise unique Speaker instances.
    # this will allow functions like turning list into set or lookup using keyword "in" to work for this user-defined class
    def __hash__(self):
        return hash((self.speaker_id, self.gender, self.abbreviation))

    def __eq__(self, other):
        if not isinstance(other, type(self)): return NotImplemented
        return self.speaker_id == other.speaker_id and self.gender == other.gender and self.abbreviation == other.abbreviation
            
class TokenInfo(object):
    
    def __init__(self, token=None, pos=None, speaker=None):
        
        if token is None:
            self.token = ''
        else:
            self.token = token

        if pos is None:
            self.pos = ''
        else:
            self.pos = pos
            
        if speaker is None:
            self.speaker = Speaker(None,None,None)
        else:
            self.speaker = speaker     
