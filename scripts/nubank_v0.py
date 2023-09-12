#%%
import re

import pandas as pd
import tabula


def treat_tabula_df(df_pdf, filename):
    pdf_columns = ["data", "icone", "descricao", "valor"]
    final_columns = ["data", "descricao", "valor", "mes_referencia"]
    df_final = pd.DataFrame(columns=final_columns)

    # extrai o ano e o mes do nome do arquivo
    match = re.search(r"Nubank_(\d{4})-(\d{2})-(\d{2}).pdf", filename)
    ano_arquivo, mes_arquivo, _ = match.groups()
    mes_referencia = pd.to_datetime(f"{ano_arquivo}-{mes_arquivo}-01") - pd.DateOffset(months=1)
    mes_referencia_str = mes_referencia.strftime("%m/%Y")

    for i in range(len(df_pdf)):
        df=df_pdf[i].T

        # Move a primeira linha para uma nova linha
        df = df.reset_index().T

        # Define os nomes das novas colunas novamente
        df.columns = pdf_columns

        # drop column icon
        df.drop('icone', axis=1, inplace=True)
        # remove rows with all null values
        df.dropna(how='all', inplace=True)

        df.reset_index(drop=True, inplace=True)

        # concatena o df final com o df tratado
        df_final = pd.concat([df_final, df], ignore_index=True)

    # Cria um dicionário com as abreviações dos meses e seus valores numéricos correspondentes
    meses = {"JAN": "01", "FEV": "02", "MAR": "03", "ABR": "04", "MAI": "05", "JUN": "06", "JUL": "07", "AGO": "08", "SET": "09", "OUT": "10", "NOV": "11", "DEZ": "12"}

    # Adiciona a nova coluna com a data formatada corretamente
    df_final["data_formatada"] = df_final["data"].apply(lambda x: f"{x.split()[0]}/{meses[x.split()[1]]}/{ano_arquivo}")

    # # Converte a nova coluna para o formato de data do pandas
    # df_final["data_completa"] = pd.to_datetime(df_final["data_formatada"], format="%d/%m/%Y")

    # adiciona a coluna de mes_referencia
    df_final["mes_referencia"] = mes_referencia_str

    # drop column data
    df_final.drop('data', axis=1, inplace=True)

    # criar coluna categoria sem valor
    df_final["categoria"] = ""

    # se descriçãõ começar com 99 ou Uber, independente do capitalização, então categoria é Uber
    df_final.loc[df_final["descricao"].str.contains(r"^(99|Uber)", case=False), "categoria"] = "Uber"

    # se descriçãõ começar com 99 ou Uber, independente do capitalização, então categoria é Uber
    df_final.loc[df_final["descricao"].str.contains(r"^(Bus)", case=False), "categoria"] = "Ônibus"

    # se tiver supermercado, iembo, savegnago, buenoserv,onii,tiquinho no nome da descrição, então categoria é Mercado
    df_final.loc[df_final["descricao"].str.contains(r"(supermercado|iembo|savegnago|buenoserv|onii|tiquinho|casa de carne|compre bem)", case=False), "categoria"] = "Mercado"

    # se tiver farma,droga no nome da descrição, então categoria é Farmácia
    df_final.loc[df_final["descricao"].str.contains(r"(farma|droga)", case=False), "categoria"] = "Farmacia"

    # se tiver - numero/numero no nome da descrição a categoria é parcelamento
    df_final.loc[df_final["descricao"].str.contains(r"-\s\d+/\d+", case=False), "categoria"] = "Parcelamento"

    # se tiver agro no nome da descrição, então categoria é Yoshi
    df_final.loc[df_final["descricao"].str.contains(r"(agro|yoshi)", case=False), "categoria"] = "Yoshi"

    # se tiver Alcilene no nome da descrição, então categoria é Utilidades
    df_final.loc[df_final["descricao"].str.contains(r"(alcilene|utilidad)", case=False), "categoria"] = "Utilidades"

    # se tiver acai, sorvet no nome da descrição, então categoria é Sorveteria
    df_final.loc[df_final["descricao"].str.contains(r"(acai|sorvet|casquinh)", case=False), "categoria"] = "Sorveteria"

    # se tiver lanche, burger,pizza no nome da descrição, então categoria é Lanchonete
    df_final.loc[df_final["descricao"].str.contains(r"(lanche|burger|pizza|espetinho|pastel|picanha|bar|Sabor|sushi|rotisser|Cooking|restaurant)", case=False), "categoria"] = "Lanchonete/Restaurante/Bar"

    # se tiver claro, amazonprime, rewards, assinatura no nome da descrição, então categoria é Assinatura
    df_final.loc[df_final["descricao"].str.contains(r"(claro|amazonprime|rewards|assinatura)", case=False), "categoria"] = "Assinatura"

    # se tiver cicbeu no nome da descrição, então categoria é frances
    df_final.loc[df_final["descricao"].str.contains(r"cicbeu", case=False), "categoria"] = "Frances"

    # se tiver ifood ou ifd no nome da descrição, então categoria é Ifood
    df_final.loc[df_final["descricao"].str.contains(r"(Ifood|Ifd)", case=False), "categoria"] = "Ifood"

    # se tiver padaria no nome da descrição, então categoria é Padaria
    df_final.loc[df_final["descricao"].str.contains(r"(padaria|pao|posto|gordon|salgado|Salgado)", case=False), "categoria"] = "Padaria"

    return df_final


if __name__ == "__main__":
    # lista todos os arquivos no diretório atual que correspondem ao padrão Nubank_YYYY_MM_DD.pdf
    import glob
    filenames = glob.glob("Nubank_*.pdf")

    # processa cada arquivo da lista
    for filename in filenames:
        # Lê o arquivo PDF e converte em um DataFrame do Pandas
        df = tabula.read_pdf(filename, pages='all')

        # Trata o DataFrame do PDF
        result = treat_tabula_df(df, filename)

        # cria um arquivo CSV com o resultado
        csv_filename = filename.replace(".pdf", ".csv")
        result.to_csv(csv_filename, index=False)