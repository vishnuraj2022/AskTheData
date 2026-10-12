Day-1
Initialised repo

Points to note:
Text to SQL accuracy depends on clear data modelling and documentation. Need good data governance.\\

Context engineering means giving the model exactly the information it needs for the task: the schema, the definitions, the rules, and sometimes worked examples


Removing the data dictionary dropped accuracy from 7/7 to 4/7" is a strong, specific line for your post.


Evaluation:

1. Data QUality checks - Make sure the data is structured and governed
2. Agent set up to answer the exact query in the last sql command as it might have trailing memory?
3. Evaluation was done on a human generated SQL to check if it was mathcig. COuld be a case where human was wrong. So use another model to pass the evaluation phase where this new model is a judge. hence implementing LLM-as-Judge