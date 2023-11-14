from __future__ import print_function
import pandas as pd
import numpy as np
from processing import clean, quarterdivision
import numpy as np
np.random.seed(1337)  # for reproducibility
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelBinarizer
import re
from nltk import word_tokenize
from nltk.corpus import stopwords
import string 
import sys
import argparse
from testing import clinicalmodeltest
## system argument checking

def encoding(note):
    updated_note = note.encode("ascii", "ignore")
    return updated_note

def report_read(df):
    #df.rename(columns={'REPORT': 'NOTE'}, inplace=True)
    #df.rename(columns={'ORDERING_DATE': 'NOTE_DATE'}, inplace=True)
    df = df.fillna('N/A')
    df = df[df['NOTE']!='N/A'].reset_index(drop =  True)
    df['NOTE'] = df['NOTE'].apply(encoding)
    df['NOTE'] = df['NOTE'].astype('str')
    return df

def main(): 
        # Create the parser
    parser = argparse.ArgumentParser(description='This is a script for extracting recurrence timeline from clinic notes.')
    dir = 'C:/Users/imonb/Box/Banerjee-20190326-anonids/'
    # Add the arguments
    parser.add_argument('--model_name', type=str, default="bert",
                    help='the name of the evaluated model')
    parser.add_argument('--patid',  type=str, required=True, default = 'onco_banerjee_anonids.csv',
                    help='the patient id')
    parser.add_argument('--clinicnotes',  type=str, default = 'V4_IMON_NOTES_DATA_TABLE.csv',
                    help='provide a .xlsx file where CLINICAL_DOCUMENT_TEXT column stores the note text.')
    parser.add_argument('--radiologyreports',  type=str, required=True, default = 'Cleaned_Banerjee_onco_radio_reports.csv',
                    help='the radiology report path')
    parser.add_argument('--pathologyreports',  type=str, required=True, default = 'Banerjee_onco_path_reports.csv',
                    help='the pathology report path')
    parser.add_argument('--output',  type=str, required=True, default = './output/PredictedNotes.xlsx',
                    help='the output prediction path')
    parser.add_argument('--batch_size',  type=int, default=1,
                    help='batch size of the testing time')

    # Parse the arguments
    args = parser.parse_args()
    '''
    print('Loading data....')
    ids = pd.read_csv(args.patid)
    ids = list(ids.ANON_ID)
    ## read files
    ## oncology -  progress note
    df3 = pd.read_excel(args.clinicnotes,index_col=False)
    #df3 = df3.loc[(df3['NOTE_TYPE'].str.contains('progress', case=False))|(df3['NOTE_TYPE'].str.contains('consultation', case=False))| 
    #    (df3['NOTE_TYPE'].str.contains('history',case=False))|(df3['NOTE_TYPE'].str.contains('oncology', case=False))|
    #    (df3['NOTE_TYPE'].str.contains('breast',case=False))]
    df3 = df3.fillna('N/A')
    df3 = df3[df3['NOTE']!='N/A']
    df3['NOTE'] = df3['NOTE'].apply(encoding)
    df3['NOTE'] = df3['NOTE'].astype('str')
    df3 = df3[df3['ANON_ID'].isin(ids)].reset_index(drop = True)
    print ('Number of progress note' + str(df3.shape))
    ## radiology
    df1 = pd.read_excel(args.radiologyreports, index_col=False)
    df1 = df1[df1['ANON_ID'].isin(ids)].reset_index(drop = True)
    df1 = report_read(df1)
    df1['NOTE_TYPE'] = 'RAD_REPORT'
    print ('Number of radiology note' + str(df1.shape))
    ## pathology
    df2 = pd.read_excel(args.pathologyreports, index_col=False)
    df2 = df2[df2['ANON_ID'].isin(ids)].reset_index(drop = True)
    df2 = report_read(df2)
    df2['NOTE_TYPE'] = 'PAT_REPORT'
    print ('Number of pathology note' + str(df2.shape))
    ## merge notes
    dfall = df1
    dfall = dfall.append(df2, ignore_index = True, sort=True)
    dfall = dfall.append(df3, ignore_index = True, sort=True)
    print ('df all: ', dfall.shape)
    del df1, df2, df3

    dfall = dfall.fillna('N/A')
    dfall['NOTE']=dfall['NOTE'].astype('str')
    dfall = dfall[dfall.NOTE_DATE != 'N/A']
    ## preprocessing
    print('Preprocessing data....')
    notes = clean(dfall)
    notes['NOTE_DATE'] =  pd.to_datetime(notes['NOTE_DATE'], errors = 'coerce')

    notes = notes[notes['NOTE_DATE']> '2008-03-01']
    del dfall
    Quarter = quarterdivision(notes)
    del notes
    '''
    ##classification
    Quarter = pd.read_csv('./outcome/quarters.csv')
    pred  = clinicalmodeltest(Quarter)
    pred['START_DATE'] =  pd.to_datetime(pred['START_DATE'])
    pred['END_DATE'] =  pd.to_datetime(pred['END_DATE'])
    pred.to_excel(args.output)

if __name__ == "__main__":
    main()
