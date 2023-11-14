# BreastRecurrence_Transformer
We developed a transformer based NLP method that enables identification of the occurrence and timing of metastatic breast cancer recurrence from EMRs. This approach may be adaptable to other cancer sites and could help to unlock the potential of EMRs for research on real-world cancer outcomes.

In order to run the labeling code, please following the following steps -
	1. Create the conda environment as - conda env create -f environment.yml 
	2. Create a model and download the trained models there - https://drive.google.com/drive/folders/1vEp5SsW93oX1hMDJkIq2qhQrnUOkqAdL?usp=sharing 
	3. Create a outcome folder
	4. Update the parameters in test.sh
	5. Clinic notes, radiology reports, pathology reports files are needed in .xlsx format.
	6. Each file should have the following columns - ANON_ID - Patient identified NOTE_TYPE - e.g. 'Discharge', 'Oncology consultatiions', 'ICU notes' NOTE_DATE - Date of the encounter NOTE - String blob
	7. Run the model as ./test.sh
	8. Model will save the output in ./outcome folder



