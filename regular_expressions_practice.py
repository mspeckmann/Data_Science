#Utilizing regular expressions to extract ICD-Codes from a PDF that are in a list format in a table

import re
import pandas as pd
import csv



def Tokenize(s,m,d,o):

    if re.findall(r"\bInclude all\b",s):
        Statement = []
    elif re.findall(r"\bInclude\b",s):
        Statement = re.findall(r"Include (\w+):?([0-9VE,\- ]+)$", s)
        incexc = "Include"
        print (Statement)
    elif re.findall(r"\bExclude\b",s):
        Statement = re.findall(r"Exclude (\w+):?([0-9VE,\- ]+)$", s)
        incexc = "Exclude"
        print(Statement)
    elif re.findall(r"\bSee MS-DRG\b",s):
        Statement = re.findall(r"See MS-DRG (\d+)",s)
        print(Statement)
    else:
        Statement = []


    diagproc = ""
    if len(Statement) == 0:
        output = 'Remove'
        return output

    elif len(Statement[0]) == 2:
        diagproc = "DX" if (Statement[0][0][0:1] == 'd') else "PX"
        list = Statement[0][1]
        items = list.split(",")
        output = []

        for item in items:
            item = item.strip()
            pieces = re.findall(r"([EV0-9]+)(-(\d+))?", item)
            if pieces[0][2] == "":
                output.append((m,d,o,incexc, diagproc, pieces[0][0]))
            else:
                rangeEnd = pieces[0][2]
                nRight = len(rangeEnd)
                lenLeft = len(pieces[0][0])
                offset = lenLeft - nRight
                rangeStart = pieces[0][0][offset:]
                prefix = pieces[0][0][:offset]
                rangeStart = int(rangeStart)
                rangeEnd = int(rangeEnd)
                for n in range(rangeStart, rangeEnd + 1):
                    suffix = str(n)
                    output.append((m,d,o,incexc, diagproc, prefix + suffix))
        #print (output)
        return output
    elif len(Statement[0]) == 3:
        output = Statement[0]
        #print(output)
        return output



def loadspecialty():
    df_spec = pd.read_csv('//Cifs2/cce$/APPI/DSS/Team/Melinda/US News 2018/Analysis Part 2 prep for 2019/all_drgs.csv'
                          ,dtype={'MS- DRG':str})
    df_spec = df_spec.replace(r'\n',' ',regex = True)
    #df_spec['Extracted ICD9'] = df_spec['ICD-9-CM'].apply(Tokenize)
    df_spec['Extracted ICD9'] = df_spec.apply(lambda x: Tokenize(x['IC9-CM'],x['MS- DRG'],x['DRG Title'],x['Severity']), axis=1)
    a = 'Remove'
    df_spec = df_spec[df_spec['Extracted ICD9'] != a]
    df_spec_num = df_spec[df_spec['Extracted ICD9'].str.len() == 3]
    #df_spec_num = df_spec[(df_spec['Extracted ICD9'].str.len() == 3) & (df_spec['Extracted ICD9'].str.contains('e')==False)]
    #df_spec_num['Extracted ICD9'] = df_spec_num['Extracted ICD9'].apply(pd.to_numeric, errors='coerce')
    df_spec_list = df_spec[df_spec['Extracted ICD9'].str.len() != 3]
    #df_spec_list = df_spec[(df_spec['Extracted ICD9'].str.len() != 3) | (df_spec['MS- DRG'] == '456')]
    df_spec_num2 = pd.merge(df_spec_num,df_spec_list, how= 'left', left_on='Extracted ICD9',right_on='MS- DRG')
    df_spec_num2 = df_spec_num2.drop('Extracted ICD9_x',1)
    df_spec_num2 = df_spec_num2.drop('Specialty_y', 1)
    df_spec_num2 = df_spec_num2.drop('MS- DRG_y', 1)
    df_spec_num2 = df_spec_num2.drop('Medical/ Surgical_y', 1)
    df_spec_num2 = df_spec_num2.drop('DRG Title_y', 1)
    df_spec_num2 = df_spec_num2.drop('Severity_y', 1)
    df_spec_num2 = df_spec_num2.drop('Weight_y', 1)
    df_spec_num2 = df_spec_num2.drop('IC9-CM_y', 1)
    df_spec_num2.columns = ['Specialty','MS- DRG','Medical/ Surgical','DRG Title','IC9-CM','Severity','Weight','Extracted ICD9']
    df_spec_new = pd.concat([df_spec_list,df_spec_num2])

    directory = '//Cifs2/cce$/APPI/DSS/Team/Melinda/US News 2018/Analysis Part 2 prep for 2019/I_alldrgs.csv'
    with open(directory, 'w') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(("MSDRG",'DRGTitle','Severity',"Action","Type","ICD9"))
        i = 0
        while i < len(df_spec_new):
            list_of_tuples = df_spec_new.iloc[i]['Extracted ICD9']
            list_of_lists = [list(elem) for elem in list_of_tuples]
            j = 0
            while j < len( df_spec_new.iloc[i]['Extracted ICD9']):
                list_of_lists[j][0] = df_spec_new.iloc[i]['MS- DRG']
                list_of_lists[j][1] = df_spec_new.iloc[i]['DRG Title']
                list_of_lists[j][2] = df_spec_new.iloc[i]['Severity']
                writer.writerow(list_of_lists[j])
                j += 1
            i += 1


    '''df = df_spec_new[['Extracted ICD9']]
    dflist = df.values.tolist()
    directory = '//Cifs2/cce$/DSS/Team/Melinda/US News 2018/Input Output MSDRG Mappings/Neuro/I_Neuro.csv'
    with open(directory, 'w') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(("MSDRG",'DRGTitle','Severity',"Action","Type","ICD9"))
        x = 0
        while x < len(dflist):
            i = 0
            while i < len(dflist[x]):
                onelist = list(dflist[x][i])
                writer.writerow(onelist)
                i += 1
            x += 1'''


    df_spec.to_csv('testUSNWR.csv', index = False, sep = ',')
    #return df_spec_new.iloc[0]['Extracted ICD9'][0]
    #return "This is complete"




df_spec = loadspecialty()
print(df_spec)


