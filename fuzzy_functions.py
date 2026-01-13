import pandas as pd
from fuzzywuzzy import fuzz, process 

### First approach

## Data cleaning

def data_clean(df):

    sufixes_replace = ["S.A", "S.A.", "SAS", "S.A.S", "LTDA", "E.S.E", "LIMITADA", "E.U"] # Removing the sufixes

    # Create the regex pattern
    regex_sufixes = r'\b(' + '|'.join(re.escape(s) for s in sufixes_replace) + r')\b'

    # Work in a copy
    df_copy = df.copy()

    # Clean only the text columns
    for col in df_copy.columns:
        if pd.api.types.is_string_dtype(df_copy[col]):
            df_copy[col] = (df_copy[col]
                            .str.normalize('NFKD')
                            .str.encode('ascii', errors='ignore')
                            .str.decode('utf-8')) # accent elimination

            df_copy[col] = df_copy[col].str.upper() # Convert to uppercase
            df_copy[col] = df_copy[col].str.replace(regex_sufixes, "", regex=True) # Replace sufixes
            df_copy[col] = df_copy[col].str.replace(r'\s+', ' ', regex=True).str.strip() # Eliminate extra spaces

    return df_copy



# First function of imputation

def imputacion_difusa(df_instituciones, df_prestadores, scorer): # Two datasets and the scorer used

  # Define the columns in which the analysis will be made
  columna_instituciones = 'prestador'
  columna_prestadores = 'prestador'

  # Define the minimum threshold of similarity
  umbral_minimo = 80

  df_prestadores_copy = df_prestadores.copy()

  # Convert the 'prestador' column to string type to handle potential non-string values
  df_prestadores_copy[columna_prestadores] = df_prestadores_copy[columna_prestadores].astype(str)


  df_prestadores_copy['match'] = df_prestadores_copy[columna_prestadores].apply(lambda x: process.extractOne(x, df_instituciones[columna_instituciones], scorer=scorer))

  # Create one column for the name of the match and other for the score
  df_prestadores_copy['match_nombre'] = df_prestadores_copy['match'].apply(lambda x: x[0] if x is not None and x[1] >= umbral_minimo else None)
  df_prestadores_copy['match_score'] = df_prestadores_copy['match'].apply(lambda x: x[1] if x is not None and x[1] >= umbral_minimo else None)


  return df_prestadores_copy


### Second approach

# Second function of imputation, with two step logic

def imputacion_estricta(df_instituciones, df_prestadores, scorer_difuso):
    '''
      Complete a fuzzy string matchin with a two step logic.
    '''
    # Define the columns to work with
    columna_instituciones = 'prestador'
    columna_prestadores = 'prestador'

    # Define the minimum thresholds
    umbral_exacto = 95  # Threshold for exact matching
    umbral_difuso = 80  # Threshold for fuzzy matching
    umbral_primera_palabra = 80

    df_prestadores_copy = df_prestadores.copy()
    df_prestadores_copy['match_nombre'] = None
    df_prestadores_copy['match_score'] = 0.0 

    df_prestadores_copy[columna_prestadores] = df_prestadores_copy[columna_prestadores].astype(str)
    
    # Step 1: Exact matching 
    matches_exactos = df_prestadores_copy[columna_prestadores].apply(
        lambda x: process.extractOne(x, df_instituciones[columna_instituciones], scorer=fuzz.ratio)
    )

    mask_exacto = matches_exactos.apply(lambda x: x is not None and x[1] >= umbral_exacto)

    df_prestadores_copy.loc[mask_exacto, 'match_nombre'] = matches_exactos[mask_exacto].apply(lambda x: x[0])
    df_prestadores_copy.loc[mask_exacto, 'match_score'] = matches_exactos[mask_exacto].apply(lambda x: float(x[1]))

    # Step 2: Fuzzy string matching for the remaining observations
    mask_no_encontrado = df_prestadores_copy['match_nombre'].isnull()
    df_no_encontrados = df_prestadores_copy[mask_no_encontrado].copy() 

    # --- Cleaning the options for fuzzywuzzy ---
    choices_list = [str(c) for c in df_instituciones[columna_instituciones] if pd.notnull(c) and str(c).strip()]

    def strict_scorer(query, choices_list):
        if not choices_list: 
            return None
        
        query_first_word = query.split()[0] if query and query.split() else ''

        # Use the clean list 'choices_list'
        best_match = process.extractOne(query, choices_list, scorer=scorer_difuso) 

        if not best_match:
            return None

        match_name, score = best_match

        match_first_word = match_name.split()[0] if match_name and match_name.split() else ''
        first_word_score = fuzz.ratio(query_first_word, match_first_word)

        if first_word_score < umbral_primera_palabra:
            return (match_name, score * 0.75)

        return best_match

    # Apply the logic for the values that weren´t found
    df_no_encontrados['match_difuso'] = df_no_encontrados[columna_prestadores].apply(
        lambda x: strict_scorer(x, choices_list) if pd.notnull(x) else None 
    )

    mask_fuzzy_strict = df_no_encontrados['match_difuso'].apply(lambda x: x is not None and x[1] >= umbral_difuso)

    df_prestadores_copy.loc[mask_no_encontrado & mask_fuzzy_strict, 'match_nombre'] = df_no_encontrados.loc[mask_fuzzy_strict, 'match_difuso'].apply(lambda x: x[0])
    df_prestadores_copy.loc[mask_no_encontrado & mask_fuzzy_strict, 'match_score'] = df_no_encontrados.loc[mask_fuzzy_strict, 'match_difuso'].apply(lambda x: float(x[1]))

    # Return the df final, without the temporal columns
    return df_prestadores_copy.drop(columns=['match_difuso', 'matches_exactos'], errors='ignore')
  # Return the df final
  return df_prestadores_copy.drop(columns=['match_exacto', 'match_difuso'], errors='ignore')