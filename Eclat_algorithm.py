
import pandas as pd
import ast
import tkinter as tk
from tkinter import filedialog
import time

def is_vertical_data(df):
    if df.columns[0] =='TiD':
        return False
    else:
        return True

def to_vert(df):
    vertical_data = {}
    for index, row in df.iterrows():
        transaction_id = row['TiD']
        items = row['items'].split(',')
        for item in items:
            if item in vertical_data:
                vertical_data[item].append(transaction_id)
            else:
                vertical_data[item] = [transaction_id]
    vertical_df = pd.DataFrame(list(vertical_data.items()), columns=['item', 'transaction_ids'])
    return vertical_df

def eclat(data, min_support):
    frequent_itemsets = []
    for item, transactions in data.items():
        support = len(set(transactions))
        if support >= min_support:
            frequent_itemsets.append(([item], support))
    freq_k=[]
    end=len(frequent_itemsets)
    for i in range(end):
        for j in range(i+1, end):
            itemset1, support1 = frequent_itemsets[i]
            itemset2, support2 = frequent_itemsets[j]
            transactions1 = data[itemset1[0]]
            transactions2 = data[itemset2[0]]
            common_transactions = list(set(transactions1) & set(transactions2))
            support = len(set(common_transactions))
            if support >= min_support:
                 itemset = (itemset1 + itemset2)
                 frequent_itemsets.append((itemset, support))
                 freq_k.append((itemset, support))
    k = 2
    while k < len(data):
        candidates = []
        for i in range(len(freq_k)):
            for j in range(i+1, len(freq_k)):
                itemset1, support1 = freq_k[i]
                itemset2, support2 = freq_k[j]
                if(itemset1[0:len(itemset1)-1]==itemset2[0:len(itemset2)-1]):
                     transactions1=set(data[itemset1[0]])
                     for item in itemset1:
                        tr=set(data[item])
                        transactions1=transactions1&tr
                     transactions2=set(data[itemset2[0]])
                     for item in itemset2:
                        tr=set(data[item])
                        transactions2=transactions2&tr
                     common_transactions = list(set(transactions1) & set(transactions2))
                     support = len(set(common_transactions))
                     if support >= min_support:
                        itemset = (itemset1 + list(itemset2[len(itemset2)-1]))
                        candidates.append((itemset, support))
        if len(candidates) == 0:
            break
        else:
            freq_k=candidates.copy()
            frequent_itemsets.extend(candidates)
            k += 1
    return frequent_itemsets

def calculate_lift(antecedent_support, consequent_support, support, total_transactions):
    lift = (support / total_transactions) / (antecedent_support / total_transactions) * (consequent_support / total_transactions)
    return lift

def generate_association_rules(frequent_itemsets, min_confidence,total_transactions):
    all_rules = []
    strong_rules = []
    for itemset, support in frequent_itemsets:
        if len(itemset) > 1:
            for i in range(1, len(itemset)):
                antecedent = itemset[:i]
                consequent = itemset[i:]
                for set_item, set_support in frequent_itemsets:
                    if set_item == antecedent:
                        antecedent_support = set_support
                        break
                for set_item, set_support in frequent_itemsets:
                    if set_item == consequent:
                        consequent_support = set_support
                        break
                if antecedent_support is not None and consequent_support is not None:
                    confidence = support / antecedent_support
                    lift=calculate_lift(antecedent_support,consequent_support,support,total_transactions)
                    rule = {
                        'antecedent': antecedent,
                        'consequent': consequent,
                        'support': support,
                        'confidence': confidence,
                        'lift':lift
                    }
                    all_rules.append(rule)
                    if confidence >= min_confidence:
                        strong_rules.append(rule)
                    lift=calculate_lift(antecedent_support,consequent_support,support,total_transactions)
                    reversed_rule = {
                        'antecedent': consequent,
                        'consequent': antecedent,
                        'support': support,
                        'confidence': confidence,
                        'lift':lift
                    }
                    all_rules.append(reversed_rule)

                    if confidence >= min_confidence:
                        strong_rules.append(reversed_rule)

    return all_rules, strong_rules
print ("choose excel file to load you will be redirected to choose after 3 seconds")
time.sleep(3)
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(
        title="Select Excel file",
        filetypes=[("Excel files", "*.xlsx;*.xls"), ("All files", "*.*")]
    )
df = pd.read_excel(file_path)
min_support = input("enter the minimum support\n")
min_support= int(min_support)
min_confidence=input("enter the minimum confidence\n")
min_confidence=float(min_confidence)
if is_vertical_data(df):
    all_tr=[]
    for index, row in df.iterrows():
        transaction_ids_value = row['Transaction IDs']
        result_list = ast.literal_eval(transaction_ids_value)
        all_tr+=result_list
    total_transactions=len(set(all_tr))
    data = df.set_index(df.columns[0])[df.columns[1]].apply(lambda x: x.split(',')).to_dict()
else:
    total_transactions=len(df)
    df = to_vert(df)
    data = df.set_index('item')['transaction_ids'].to_dict()
frequent_itemsets = eclat(data, min_support)
for itemset, support in frequent_itemsets:
    print(f'Itemset: {itemset}, Support: {support}')
all_rules, strong_rules = generate_association_rules(frequent_itemsets, min_confidence,total_transactions)
print("\n-------All Rules---------:")
for rule in all_rules:
    print(f'Rule: {rule["antecedent"]} => {rule["consequent"]}, Support: {rule["support"]}, Confidence: {rule["confidence"]},lift: {rule["lift"]}1')
print("\n------Strong Rules-------:")
for rule in strong_rules:
    print(f'Rule: {rule["antecedent"]} => {rule["consequent"]}, Support: {rule["support"]}, Confidence: {rule["confidence"]},lift: {rule["lift"]}')
