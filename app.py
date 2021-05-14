from flask import Flask,request,render_template
import numpy as np
import pickle
from publicsuffixlist import PublicSuffixList
import re
import collections
import math


app=Flask(__name__)

@app.route('/',methods=['GET'])
def home():
    return render_template('index1.html')

@app.route('/predict', methods=['POST'])
def predict():
    domain=str(request.form['url'])

    #creating an obj for PublicSuffixList
    psl = PublicSuffixList() 

    # Generate Domain Name Length (DNL)
    def domain_length(domain):
        return len(domain)

    # Generate Number of Subdomains (NoS)
    def subdomains_number(domain):
        subdomain = ignoreVPS(domain)
        return (subdomain.count('.') + 1)

    def subdomain_length_mean(domain):
        # enerate Subdomain Length Mean (SLM) 
        subdomain = ignoreVPS(domain)
        result = (len(subdomain) - subdomain.count('.')) / (subdomain.count('.') + 1)
        return result

    def ignoreVPS(domain):
        # Return the rest of domain after ignoring the Valid Public Suffixes:
        validPublicSuffix = '.' + psl.publicsuffix(domain)
        if len(validPublicSuffix) < len(domain):
             # If it has VPS
            subString = domain[0: domain.index(validPublicSuffix)]  
        elif len(validPublicSuffix) == len(domain):
            return 0
        else:
            # If not
            subString = domain
        return subString

    def typeTo_Binary(type):
        # Convert Type to Binary variable DGA = 1, Normal = 0
        if type == 'DGA':
            return 1
        else:
            return 0

    def has_www_prefix(domain):
        # Generate Has www Prefix (HwP)
        if domain.split('.')[0] == 'www':
            return 1
        else:
            return 0

    def has_hvltd(domain):
        # Generate Has a Valid Top Level Domain (HVTLD)
        if domain.split('.')[len(domain.split('.')) - 1].upper() in topLevelDomain:
            return 1
        else:
            return 0

    def contains_single_character_subdomain(domain):
        # Generate Contains Single-Character Subdomain (CSCS) 
        domain = ignoreVPS(domain)
        str_split = domain.split('.')
        minLength = len(str_split[0])
        for i in range(0, len(str_split) - 1):
            minLength = len(str_split[i]) if len(str_split[i]) < minLength else minLength
        if minLength == 1:
            return 1
        else:
            return 0

    def contains_TLD_subdomain(domain):
        # Generate Contains TLD as Subdomain (CTS)
        subdomain = ignoreVPS(domain)
        str_split = subdomain.split('.')
        for i in range(0, len(str_split) - 1):
            if str_split[i].upper() in topLevelDomain:
                return 1
        return 0

    def underscore_ratio(domain):
        # Generate Underscore Ratio (UR) on dataset
        subString = ignoreVPS(domain)
        result = subString.count('_') / (len(subString) - subString.count('.'))
        return result

    def contains_IP_address(domain):
        # Generate Contains IP Address (CIPA) on datasetx
        splitSet = domain.split('.')
        for element in splitSet:
            if(re.match("\d+", element)) == None:
                return 0
        return 1  

    def contains_digit(domain):
        """
        Contains Digits 
        """
        subdomain = ignoreVPS(domain)
        for item in subdomain:
            if item.isdigit():
                return 1
        return 0

    def vowel_ratio(domain):
        """
        calculate Vowel Ratio 
        """
        VOWELS = set('aeiou')
        v_counter = 0
        a_counter = 0
        ratio = 0
        subdomain = ignoreVPS(domain)
        for item in subdomain:
            if item.isalpha():
                a_counter+=1
                if item in VOWELS:
                    v_counter+=1
        if a_counter>1:
            ratio = v_counter/a_counter
        return ratio

    def digit_ratio(domain):
        """
        calculate digit ratio
        """
        d_counter = 0
        counter = 0
        ratio = 0
        subdomain = ignoreVPS(domain)
        for item in subdomain:
            if item.isalpha() or item.isdigit():
                counter+=1
                if item.isdigit():
                    d_counter+=1
        if counter>1:
            ratio = d_counter/counter
        return ratio
      
    def prc_rrc(domain):
        """
        calculate the Ratio of Repeated Characters in a subdomain
        """
        subdomain = ignoreVPS(domain)
        subdomain = re.sub("[.]", "", subdomain)
        char_num=0
        repeated_char_num=0
        d = collections.defaultdict(int)
        for c in list(subdomain):
            d[c] += 1
        for item in d:
            char_num +=1
            if d[item]>1:
                repeated_char_num +=1
        ratio = repeated_char_num/char_num
        return ratio

    def prc_rcc(domain):
        """
        calculate the Ratio of Consecutive Consonants
        """
        VOWELS = set('aeiou')
        counter = 0
        cons_counter=0
        subdomain = ignoreVPS(domain)
        for item in subdomain:
            i = 0
            if item.isalpha() and item not in VOWELS:
                counter+=1
            else:
                if counter>1:
                    cons_counter+=counter
                counter=0
            i+=1
        if i==len(subdomain) and counter>1:
            cons_counter+=counter
        ratio = cons_counter/len(subdomain)
        return ratio

    def prc_rcd(domain):
        """
        calculate the ratio of consecutive digits
        """
        counter = 0
        digit_counter=0
        subdomain = ignoreVPS(domain)
        for item in subdomain:
            i = 0
            if item.isdigit():
                counter+=1
            else:
                if counter>1:
                    digit_counter+=counter
                counter=0
            i+=1
        if i==len(subdomain) and counter>1:
            digit_counter+=counter
        ratio = digit_counter/len(subdomain)
        return ratio

    def prc_entropy(domain):
        """
        calculate the entropy of subdomain
        :param domain_str: subdomain
        :return: the value of entropy
        """
        subdomain = ignoreVPS(domain)
        # get probability of chars in string
        prob = [float(subdomain.count(c)) / len(subdomain) for c in dict.fromkeys(list(subdomain))]

        # calculate the entropy
        entropy = - sum([p * math.log(p) / math.log(2.0) for p in prob])
        return entropy

    #defining those function in "extract_features" which will be used for creating new categories
    #def extract_features():
    input_list=[]
    domain_length1=domain_length(domain)
    subdomains_number1=subdomains_number(domain)
    subdomain_length_mean1=subdomain_length_mean(domain)
    contains_digit1=contains_digit(domain)
    vowel_ratio1=vowel_ratio(domain)
    digit_ratio1=digit_ratio(domain)
    prc_rrc1=prc_rrc(domain)
    prc_rcc1=prc_rcc(domain)
    prc_rcd1=prc_rcd(domain)
    prc_entropy1=prc_entropy(domain)

    input_list.append(domain_length1)
    input_list.append(subdomains_number1)
    input_list.append(subdomain_length_mean1)
    input_list.append(contains_digit1)
    input_list.append(vowel_ratio1)
    input_list.append(digit_ratio1)
    input_list.append(prc_rrc1)
    input_list.append(prc_rcc1)
    input_list.append(prc_rcd1)
    input_list.append(prc_entropy1)

    #extract_features() #calling the function to create input array

    #input_arr=input_list.toarray()
    input_arr=np.array(input_list)
    input_arr=input_arr.reshape(1,-1)

    #Loading my Classifier pickle file on which the dataset is trained upon
    pickle_in=open(r'RandomForestClassifier.pkl','rb')
    rf=pickle.load(pickle_in)

    prediction=rf.predict(input_arr)
    
    if prediction[0]==0:
        output_html="Normal"
    elif prediction[0]==1:
        output_html="DGA"
    

    return render_template('index1.html', prediction_text='The predicted choice is :{}'.format(output_html))


if __name__=="__main__":
    app.debug = True
    app.run()
