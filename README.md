# BreastRecurrence_Transformer
We developed a transformer based NLP method that enables identification of the occurrence and timing of metastatic breast cancer recurrence from EMRs. This approach may be adaptable to other cancer sites and could help to unlock the potential of EMRs for research on real-world cancer outcomes.

In order to run the labeling code, please following the following steps -
	Create the conda environment as - 
	Create a model and download the trained models there - https://drive.google.com/drive/folders/1vEp5SsW93oX1hMDJkIq2qhQrnUOkqAdL?usp=sharing
	Create a outcome folder
	Update the parameters in test.sh
	Clinic notes, radiology reports, pathology reports files are needed in .xlsx format.
	Each file should have the following columns - ANON_ID - Patient identified NOTE_TYPE - e.g. 'Discharge', 'Oncology consultatiions', 'ICU notes' NOTE_DATE - Date of the encounter NOTE - String blob
	Run the model as ./test.sh
	Model will save the output in ./outcome folder



