python main.py --model_name 'bert' \
--patid '/media/Datacenter_storage/BreastCancerRecurrence/Breast_cancer_recurrence/Data/onco_banerjee_anonids.csv' \
--clinicnotes '/media/Datacenter_storage/BreastCancerRecurrence/Breast_cancer_recurrence/Data/EDTWH_FACT_CLINICAL_DOCUMENTS.xlsx' \
--radiologyreports '/media/Datacenter_storage/BreastCancerRecurrence/Breast_cancer_recurrence/Data/EDTWH_FACT_RADIOLOGY.xlsx' \
--batch_size 5 \
--pathologyreports '/media/Datacenter_storage/BreastCancerRecurrence/Breast_cancer_recurrence/Data/EDTWH_FACT_PATHOLOGY.xlsx' --output '/media/Datacenter_storage/BreastCancerRecurrence/Breast_cancer_recurrence/Code/Recurrence_clinic_BERT/outcome/pred_recur.xlsx'