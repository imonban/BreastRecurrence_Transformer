import torch
from tqdm.notebook import tqdm

from transformers import BertTokenizer
from torch.utils.data import TensorDataset
from sklearn.model_selection import train_test_split
from transformers import BertForSequenceClassification
import pandas as pd
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler
from transformers import AdamW, get_linear_schedule_with_warmup
from sklearn.metrics import f1_score
from sklearn.metrics import precision_recall_fscore_support
import random
import numpy as np
from transformers import AutoTokenizer, AutoModel


def f1_score_func(preds, labels):
    preds_flat = np.argmax(preds, axis=1).flatten()
    labels_flat = labels.flatten()
    return f1_score(labels_flat, preds_flat, average='weighted')

def f1_score_class(preds, labels):
    preds_flat = np.argmax(preds, axis=1).flatten()
    labels_flat = labels.flatten()
    return precision_recall_fscore_support(labels_flat, preds_flat, average=None)

def accuracy_per_class(preds, labels):
    label_dict_inverse = {v: k for k, v in label_dict.items()}
    
    preds_flat = np.argmax(preds, axis=1).flatten()
    labels_flat = labels.flatten()

    for label in np.unique(labels_flat):
        y_preds = preds_flat[labels_flat==label]
        y_true = labels_flat[labels_flat==label]
        print(f'Class: {label_dict_inverse[label]}')
        print(f'Accuracy: {len(y_preds[y_preds==label])}/{len(y_true)}\n')

def data_split(critical):
    X_train, X_val, y_train, y_val = train_test_split(critical.index.values, 
                                                  critical.Label.values, 
                                                  test_size=0.15, 
                                                  random_state=42, 
                                                  stratify=critical.Label.values)
    critical['data_type'] = ['not_set']*critical.shape[0]
    critical.loc[X_train, 'data_type'] = 'train'
    critical.loc[X_val, 'data_type'] = 'val'
    return critical

def data_length(dataset, classes):
    length = [0]*classes
    for i in range(len(dataset)):
        for j in range(classes):
            if dataset[i] == j:
                length[j] += 1
    return length

def tokenizationBERT(df):
    tokenizer = AutoTokenizer.from_pretrained("emilyalsentzer/Bio_ClinicalBERT", 
                                          do_lower_case=True)
    tokenizer.save_pretrained("clinicalbert_tokenizer")
    possible_labels = df.Label.unique()
    label_dict = {}
    for index, possible_label in enumerate(possible_labels):
        label_dict[possible_label] = index
    input_ids = []
    attention_masks = []
    for sentence in df['text']:
        encoded_sentence = tokenizer.encode_plus(
        sentence,
        add_special_tokens=True,
        max_length=156,
        truncation=True,
        pad_to_max_length=True,
        return_attention_mask=True,
        return_tensors='pt',
        )
        input_ids.append(encoded_sentence['input_ids'])
        attention_masks.append(encoded_sentence['attention_mask'])
    labels = list(df['Label'])
    train_ids, val_ids, train_masks, val_masks, train_labels, val_labels = train_test_split(input_ids,attention_masks, labels,     test_size=0.2, stratify=labels)
    train_ids = torch.cat(train_ids, dim=0)
    train_masks = torch.cat(train_masks, dim=0)
    train_labels = torch.tensor(train_labels)

    val_ids = torch.cat(val_ids, dim=0)
    val_masks = torch.cat(val_masks, dim=0)
    val_labels = torch.tensor(val_labels)
    dataset_train = TensorDataset(train_ids, train_masks, train_labels)
    dataset_val = TensorDataset(val_ids, val_masks, val_labels)

    return dataset_train, dataset_val 


def tokenizationBERT_test(df):
    tokenizer = AutoTokenizer.from_pretrained("emilyalsentzer/Bio_ClinicalBERT", 
                                          do_lower_case=True)
    tokenizer.save_pretrained("clinicalbert_tokenizer")
    possible_labels = df.label.unique()
    label_dict = {}
    for index, possible_label in enumerate(possible_labels):
        label_dict[possible_label] = index
    input_ids = []
    attention_masks = []
    for sentence in df['text']:
        encoded_sentence = tokenizer.encode_plus(
        sentence,
        add_special_tokens=True,
        max_length=156,
        truncation=True,
        pad_to_max_length=True,
        return_attention_mask=True,
        return_tensors='pt',
        )
        input_ids.append(encoded_sentence['input_ids'])
        attention_masks.append(encoded_sentence['attention_mask'])
    labels = list(df['label'])
    input_ids = torch.cat(input_ids, dim=0)
    attention_masks = torch.cat(attention_masks, dim=0)
    labels = torch.tensor(labels)
    dataset_val = TensorDataset(input_ids,attention_masks, labels)
    return dataset_val 

def evaluate(model, dataloader_val, device):

    model.eval()
    
    loss_val_total = 0
    predictions, true_vals = [], []
    
    for batch in dataloader_val:
        
        batch = tuple(b.to(device) for b in batch)
        
        inputs = {'input_ids':      batch[0],
                  'attention_mask': batch[1],
                  'labels':         batch[2],
                 }

        with torch.no_grad():        
            outputs = model(**inputs)
            
        loss = outputs[0]
        logits = outputs[1]
        loss_val_total += loss.item()

        logits = logits.detach().cpu().numpy()
        label_ids = inputs['labels'].cpu().numpy()
        predictions.append(logits)
        true_vals.append(label_ids)
    
    loss_val_avg = loss_val_total/len(dataloader_val) 
    
    predictions = np.concatenate(predictions, axis=0)
    true_vals = np.concatenate(true_vals, axis=0)
            
    return loss_val_avg, predictions, true_vals


def generate_label(preds):
    col = ['0','1']
    preds_flat = np.argmax(preds, axis=1).flatten()
    preds = []
    for p in preds_flat:
        preds.append(col[p])
    return(preds)

def clinicalmodeltraining(df):
    df = data_split(df)
    dataset_train, dataset_val = tokenizationBERT(df)
    model = BertForSequenceClassification.from_pretrained(
        #"bert-base-uncased", # Use the 12-layer BERT model, with an uncased vocab.
        "emilyalsentzer/Bio_ClinicalBERT",
        num_labels = 2, # The number of output labels--2 for binary classification.
                        # You can increase this for multi-class tasks.   
        output_attentions = False, # Whether the model returns attentions weights.
        output_hidden_states = False, # Whether the model returns all hidden-states.
      )

    batch_size = 5
    dataloader_train = DataLoader(dataset_train, 
                              sampler=RandomSampler(dataset_train), 
                              batch_size=batch_size)
    dataloader_validation = DataLoader(dataset_val, 
                                   sampler=SequentialSampler(dataset_val), 
                                   batch_size=batch_size)
    model.cuda()
    lr = 0.00002
    optimizer = AdamW(model.parameters(), lr=lr, eps=1e-8)
    
    epochs = 10

    scheduler = get_linear_schedule_with_warmup(optimizer, 
                                            num_warmup_steps=0,
                                            num_training_steps=len(dataloader_train)*epochs)
    seed_val = 17
    random.seed(seed_val)
    np.random.seed(seed_val)
    torch.manual_seed(seed_val)
    torch.cuda.manual_seed_all(seed_val)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    print(device)
    for epoch in tqdm(range(1, epochs+1)):
        model.train()
        loss_train_total = 0
        progress_bar = tqdm(dataloader_train, desc='Epoch {:1d}'.format(epoch), leave=False, disable=False)
        for batch in progress_bar:
            model.zero_grad()
            batch = tuple(b.to(device) for b in batch)
            inputs = {'input_ids':      batch[0],
                  'attention_mask': batch[1],
                  'labels':         batch[2],
                 }       
            outputs = model(**inputs)
        
            loss = outputs[0]
            loss_train_total += loss.item()
            loss.backward()

            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
        
            progress_bar.set_postfix({'training_loss': '{:.3f}'.format(loss.item()/len(batch))})
         
        torch.save(model.state_dict(), f'finetuned_ClinicalBERT_epoch_{epoch}.model')
        
        tqdm.write(f'\nEpoch {epoch}')
    
        loss_train_avg = loss_train_total/len(dataloader_train)            
        tqdm.write(f'Training loss: {loss_train_avg}')
    
        val_loss, predictions, true_vals = evaluate(model, dataloader_validation, device)
        val_f1 = f1_score_func(predictions, true_vals)
        tqdm.write(f'Validation loss: {val_loss}')
        tqdm.write(f'F1 Score (Weighted): {val_f1}')
    model.save_pretrained("cliniclbert")
    
    _, predictions, true_vals = evaluate(dataloader_validation)
    return model


def generate_label(preds):
    col = ['Non-Recurrence', 'Recurrence']
    preds_flat = np.argmax(preds, axis=1).flatten()
    preds = []
    for p in preds_flat:
        preds.append(col[p])
    return(preds)

def clinicalmodeltest(df):
    df['label'] =0
    model = torch.load('./model/clinicBERT_recurrence.pt')
    
    '''
    model = BertForSequenceClassification.from_pretrained(
        "bert-base-uncased", # Use the 12-layer BERT model, with an uncased vocab.
        #"cliniclbert",
        num_labels = 2, # The number of output labels--2 for binary classification.
                        # You can increase this for multi-class tasks.   
        output_attentions = False, # Whether the model returns attentions weights.
        output_hidden_states = False, # Whether the model returns all hidden-states.
      )
    model.load_state_dict(torch.load('./model/finetuned_ClinicalBERT_epoch_7.model'))
    '''
    dataset_val = tokenizationBERT_test(df)
    batch_size = 5
    dataloader_validation = DataLoader(dataset_val, 
                                   sampler=SequentialSampler(dataset_val), 
                                   batch_size=batch_size)
    model.cuda()
    seed_val = 17
    random.seed(seed_val)
    np.random.seed(seed_val)
    torch.manual_seed(seed_val)
    torch.cuda.manual_seed_all(seed_val)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    print(device)
    _, predictions, true_vals = evaluate(model, dataloader_validation, device)
    df['Prediction'] = generate_label(predictions)
    return df