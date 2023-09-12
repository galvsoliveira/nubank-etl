import re
import pandas as pd
import tabula
import glob

def read_and_process_pdf_file(filename):
    df_pdf = tabula.read_pdf(filename, pages='all')
    year, month = extract_month_year_from_filename(filename)

    if year and month:
        return treat_tabula_df(df_pdf, year, month)
    else:
        return None

def extract_month_year_from_filename(filename):
    match = re.search(r"Nubank_(\d{4})-(\d{2})-(\d{2}).pdf", filename)
    if match:
        year, month, _ = match.groups()
        return year, month
    else:
        return None, None

def treat_tabula_df(df_pdf, year, month):
    pdf_columns = ["data", "icone", "descricao", "valor"]
    final_columns = ["data", "descricao", "valor", "mes_referencia"]
    df_final = pd.DataFrame(columns=final_columns)

    mes_referencia = pd.to_datetime(f"{year}-{month}-01") - pd.DateOffset(months=1)
    mes_referencia_str = mes_referencia.strftime("%m/%Y")

    for i in range(len(df_pdf)):
        df = df_pdf[i].T
        df = df.reset_index().T
        df.columns = pdf_columns
        df.drop('icone', axis=1, inplace=True)
        df.dropna(how='all', inplace=True)
        df.reset_index(drop=True, inplace=True)
        df_final = pd.concat([df_final, df], ignore_index=True)

    meses = {
        "JAN": "01", "FEV": "02", "MAR": "03", "ABR": "04", "MAI": "05", "JUN": "06",
        "JUL": "07", "AGO": "08", "SET": "09", "OUT": "10", "NOV": "11", "DEZ": "12"
    }

    df_final["data_formatada"] = df_final["data"].apply(lambda x: f"{x.split()[0]}/{meses[x.split()[1]]}/{year}")
    df_final["mes_referencia"] = mes_referencia_str
    df_final.drop('data', axis=1, inplace=True)
    df_final["categoria"] = ""

    categories = {
        r"^(99|Uber)": "Uber",
        r"^(Bus)": "Ônibus",
        r"(supermercado|iembo|savegnago|buenoserv|onii|tiquinho|casa de carne|compre bem)": "Mercado",
        r"(farma|droga)": "Farmacia",
        r"-\s\d+/\d+": "Parcelamento",
        r"(agro|yoshi)": "Yoshi",
        r"(alcilene|utilidad)": "Utilidades",
        r"(acai|sorvet|casquinh)": "Sorveteria",
        r"(lanche|burger|pizza|espetinho|pastel|picanha|bar|Sabor|sushi|rotisser|Cooking|restaurant)": "Lanchonete/Restaurante/Bar",
        r"(claro|amazonprime|rewards|assinatura)": "Assinatura",
        r"cicbeu": "Frances",
        r"(Ifood|Ifd)": "Ifood",
        r"(padaria|pao|posto|gordon|salgado|Salgado)": "Padaria"
    }

    for pattern, category in categories.items():
        df_final.loc[df_final["descricao"].str.contains(pattern, case=False), "categoria"] = category

    return df_final

if __name__ == "__main__":
    filenames = glob.glob("Nubank_*.pdf")

    for filename in filenames:
        result = read_and_process_pdf_file(filename)

        if result is not None:
            csv_filename = filename.replace(".pdf", ".csv")
            result.to_csv(csv_filename, index=False)
