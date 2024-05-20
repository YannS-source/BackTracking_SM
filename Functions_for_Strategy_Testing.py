import numpy as np

################################
# Functions to apply conditions and to specify them.
################################

def apply_conditions(df, conditions, order):
    result_df = df.copy()
    for condition_name in order:
        condition_func, params = conditions.get(condition_name)
        if condition_func:
            result_df = condition_func(result_df, *params)
    return result_df


def c_col_inf_sup(df, col, threshold_below, threshold_above):
    return df[(df[col] > threshold_below) & (df[col] < threshold_above)]

def c_col_inf_sup_double(df, col, threshold_below, threshold_above):
    return df[(df[col] < threshold_below) | (df[col] > threshold_above)]

def c_3D_sup_W(df, threshold=1):
    return df[df['Change 3 Days'] > threshold*df['Change 7 Days']]

def c_W_sup_M(df, threshold=1):
    return df[(df['Change 28 Days'] >= 0) & (1/threshold*df['Change 7 Days'] > df['Change 28 Days']) |
              (df['Change 28 Days'] < 0) & (df['Change 7 Days'] > threshold*df['Change 28 Days'])]

def c_largest_change(df, n, col):
    return df.nlargest(n, col)

def c_smallest_change(df, n, col):
    return df.nsmallest(n, col)

def n_largest_difference(df, n, col1, col2):
    df['difference'] = (df[col1] - df[col2]).abs()
    result = df.nlargest(n, 'difference')
    result = result.drop(columns=['difference'])
    return result


################################
# Function to exit a position early
################################

def when_to_exit(df, limit, condition=False):
    if df['Change Close to 16'].empty:
        return 0
    else:
        if condition == False:
            return np.mean(df['Change Close to 16'])

        else:
            def adjusted_return(row):
              if row['Change Current 9 to 10'] + row['Change Current 10 to 11'] <= limit:
                return row['Change Close to 11']
              else:
                return row['Change Close to 16']

            df['Adjusted Return'] = df.apply(adjusted_return, axis=1)
            return np.mean(df['Adjusted Return'])