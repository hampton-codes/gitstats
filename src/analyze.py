import datetime
import numpy as np
import pandas as pd
from io import StringIO

from utils import logger

TOP_LANGS = 20
BUCKETS = [
    (0,30),
    (31,60),
    (61,90),
    (91,120),
    (120,180),
    (180,365),
    (0,366)
]

def get_stats(f):
    df = pd.read_csv(f)
    now = datetime.datetime.now()
    df['created_at_dt'] = pd.to_datetime(df['created_at'], format='%Y-%m-%dT%H:%M:%SZ')
    df['updated_at_dt'] = pd.to_datetime(df['updated_at'], format='%Y-%m-%dT%H:%M:%SZ')
    df['pushed_at_dt'] = pd.to_datetime(df['pushed_at'], format='%Y-%m-%dT%H:%M:%SZ')
    df['last_modifed_at_dt'] = df[['updated_at_dt', 'pushed_at_dt']].max(axis=1)
    df['days_since_last_updated'] = df['last_modifed_at_dt'].sub(now).div(np.timedelta64(1, 'D')).abs().round()
    df['days_since_created'] = df['created_at_dt'].sub(now).div(np.timedelta64(1, 'D')).abs().round()
    
    lang_cols = [col for col in df.columns if col.find('languages') == 0]
    oldest_repo_dt = df['created_at_dt'].min().strftime('%Y-%m-%d')
    num_repos = df.shape[0]
    top_X_langs = df[lang_cols].sum(axis=0).sort_values(ascending=False).iloc[:TOP_LANGS]
    
    
    # Plot top_X_langs
    x_langs = []
    x_langs_csv = ["language,count"]
    for k,v in top_X_langs.items():
        x_langs.append({
            f'{k.split(".")[1]}': v
        })
        x_langs_csv.append(f'{k.split(".")[1]},{v}')
    df2 = pd.read_csv(StringIO('\n'.join(x_langs_csv)))
    ax = df2[['language', 'count']].plot(kind='bar', x='language', y='count', legend=True, title=f'Top {TOP_LANGS} Languages in use', figsize=(11,8))
    fig = ax.get_figure()
    top_languages_plot_file = f'/tmp/plot-top{TOP_LANGS}langs-{now.strftime("%Y%m%d")}.pdf'
    fig.savefig(top_languages_plot_file)
    
    # Prepare age_buckets
    age_buckets = []
    age_buckets_csv = ['left,days_since_last_update,count']
    for l,r in BUCKETS[:-1]:
        count = df['days_since_last_updated'].between(l,r).value_counts().to_dict()
        if True in count.keys():
            count = count[True]
        else:
            count = 0
        age_buckets.append({
            "left": l,
            "right": r,
            "count": count
        })
        age_buckets_csv.append(f'{l},{r},{count}')
    left = BUCKETS[-1][1]
    right = int(df["days_since_created"].max().round())
    if right > left:
        count = df['days_since_last_updated'].between(BUCKETS[-1][0], BUCKETS[-1][1]).value_counts().to_dict()
        if False in count.keys():
            count = count[False]
        else:
            count = 0
        age_buckets.append({
            "left": left,
            "right": right,
            "count": count
        })
        age_buckets_csv.append(f'{left},{right},{count}')
    
    # Plot age_buckets
    df2 = pd.read_csv(StringIO('\n'.join(age_buckets_csv)))
    ax = df2[['days_since_last_update', 'count']].plot(kind='bar', x='days_since_last_update', y='count', legend=True, title='Repositories by age', figsize=(11,8))
    fig = ax.get_figure()
    file_name = f'/tmp/plot-{now.strftime("%Y%m%d")}.pdf'
    fig.savefig(file_name)
    
    data = {
        'num_languages': len(lang_cols),
        'top_languages': x_langs,
        'oldest_repository_dt': oldest_repo_dt,
        'num_repositories': num_repos,
        'age_buckets': age_buckets,
        'age_buckets_plot_file': file_name,
        'top_languages_plot_file': top_languages_plot_file
    }
    return data