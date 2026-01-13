# Fuzzy String Matching in Python

This repository documents the end-to-end design, implementation, and real-world application of a **fuzzy string matching system built in Python**, developed and used in a production work environment.

---

## Business Problem

During my time working in a large pharmaceutical company, a daily challenge was the data consistency. The company uses public and internal databases and joins them both to perform different analysis, however, the problem always was the fact that the names among the different data bases weren't consistent, furthermore, to join the data it required a lot of manual data cleaning, resulting in a high amount of weekly hours just to create the database without any analysis performed.

For this use case, the company i worked with needed to perform a customer segmentation based on the conversion funnel (Awareness, consideration, conversion, loyalty, advocacy) in order to determine levels of priority to the customers and the action plan to each of them: The goal is to convert the customers to advocacy customers, and keep the ones who currently are. The data they used came from a public dataset (df_prestadores) which had the names of the health care providers, as well as other useful information such as address, city, amount of patients based on the pathology,etc. This dataset was needed because it had the Oncologos del occidente - Pereira, Oncologos del occidentegranular information for each health care provider, but it lack grouping because different locations of the same institution couldn´t be grouped into one sigle patern name (ex, a single patern institution might have different locations accross the country, and each of them had a different name in some way, and the name of the patern institution was not in the dataset)

The internal dataset (df_instituciones) had the patern name of the institutions, as well as other internal information collected by the company. The goal with the MasterData is to unify the information, reduce the time of preprocessing to Zero (before the masterdata it was near 2 hrs of cleaning each time they needed to unify some data like this) and be able to complete the segmentation analysis without wasting time in data join

Typical examples:

- `"Hospital Universitario San Ignacio"` vs `"HU San ignacio"`
- `"Oncologos del Occidente SA"` vs `"Oncologos del Occidente"`
- `"Instituto de diagnostico medico S.A IDIME"` vs `"Instituto de diagnostico medico IDIME"`
- `"Unidad Laser del Atlantico Clinica Oftalmologica"` vs `"Clinica Oftalmologica Unidad Laser del Atlantico"`

The table join couldn´t be completed because the only key available was the name of the institution, since the names were not exactly the same, the analysis took a long time to be completed.

---

## First Approach

Originally, the datasets contained information from two different tables, using pandas and using fuzzy wuzzy and match was made to find the most close strings, to create a relationship between those two.

The process followed these steps:

1. **Data cleaning**  
   To perform the match, i first cleaned the data using regular expressions (regex) in which, i created a pattern recognition to delete the sufixes in the names (`"S.A", "S.A.", "SAS", "S.A.S", "LTDA", "E.S.E", "LIMITADA", "E.U"`). Then, clean the text columns and delete accents, convert to uppercase all the characters, discard extra spaces

2. **Create the function of the fuzzy imputation**  
   For the text columns, eliminate the accents


Even though the function does what is intended to do, the function only matches properly about 5% of the observations, the remaining data is not matched correctly with problems like false positive (matching names that are not correctly matched). The iterative steps followed to refine the function were the following

---

## Second Approach

1. **Analysis of the output:** Identify why the function doesn´t work as expected
2. **Hypothesis:** Bring one or multiple solutions to eliminate the problem
3. **Implementation:** Create the new version
4. **Validation and test:** Test the new solution with a set of know observations (successful and failed attempts) to verify if the improvements work properly, or if they introduce new complications
5. **Deployment and monitoring:** Apply the final solution and verify its performance

---

In this case, the function may not be working properly because the scorer doesn´t penalize enough the differences between strings, as possible solutions we can change the scorer to one that is more strict, more pre-processing of the strings before the function of imputation, match of multiple steps or a more complex logic.

| Options to refine the function |
| --- |
| Increase the threshold to a higher value (ex. 85). However, this could exclude some correct matches |
| Logic of multiple steps: The first step is a nearly perfect match (threshold of  ~95 with **fuzz.ratio**), then, for the remaining observations a more flexible fuzzy matching |
| A custom scorer, that combines multiple metrics such as the length of the string, verification of the first token, plus the fuzzywuzzy scorers |


All of the process above and the code is in the repository.