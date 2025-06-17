import os
import requests
import pandas as pd
from IPython.display import display
from tqdm import tqdm

def ensure_upload_dir():
    upload_dir = 'upload'
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    return upload_dir

def get_aggregados_raw():
    url = "https://servicodados.ibge.gov.br/api/v3/agregados"
    resp = requests.get(url)
    resp.raise_for_status()
    return pd.json_normalize(resp.json())

def normalize_agregados(df_raw):
    list_cols = [c for c in df_raw.columns if df_raw[c].apply(lambda x: isinstance(x, list)).any()]
    if not list_cols:
        raise ValueError(f"Nenhuma coluna de lista encontrada em df_raw. Colunas disponíveis: {df_raw.columns.tolist()}")
    col = list_cols[0]
    df = df_raw[['id', 'nome', col]].rename(columns={'nome': 'Agregado'})
    df = df.explode(col)
    df['ID'] = df[col].apply(lambda x: x.get('id') if isinstance(x, dict) else None)
    df['Descrição'] = df[col].apply(lambda x: x.get('nome') if isinstance(x, dict) else None)
    df = df.drop(columns=[col])
    return df

def get_agregado_detail(agregado_id):
    url = f"https://servicodados.ibge.gov.br/api/v3/agregados/{agregado_id}"
    resp = requests.get(url)
    resp.raise_for_status()
    return pd.json_normalize(resp.json())

def run_pipeline(save_prefix="ibge"):
    upload_dir = ensure_upload_dir()

    raw = get_aggregados_raw()
    norm = normalize_agregados(raw)
    display(norm.head())

    path_list = os.path.join(upload_dir, f"{save_prefix}_agregados_list.csv")
    norm.to_csv(
        path_list,
        sep=';', decimal=',', encoding='utf-8-sig', index=False
    )
    print(f"✅ Arquivo de lista salvo em {path_list}")

    detalhes = []
    for aid in tqdm(raw['id'], desc="Buscando detalhes"):
        try:
            df_det = get_agregado_detail(aid)
            df_det['agregado_id'] = aid
            detalhes.append(df_det)
        except Exception as e:
            print(f" Ddados coletados {aid}: {e}")

    if detalhes:
        all_det = pd.concat(detalhes, ignore_index=True)
        path_det = os.path.join(upload_dir, f"{save_prefix}_agregados_details.csv")
        all_det.to_csv(
            path_det,
            sep=';', decimal=',', encoding='utf-8-sig', index=False
        )
        print(f"✅ Arquivo de detalhes salvo em {path_det}")
        display(all_det.head())

if __name__ == "__main__":
    run_pipeline(save_prefix="ibge")

