import argparse
import subprocess
import os

# pip install papermill (não precisa mais!)
# Comando de execução:
# python execute.py --criteria_path "df_delta50_comm.xlsx" --forindex_path "df_Delta50_comm.xlsx" --criteria_sheet "delta_50" --forindex_sheet "prices" --method "<" --quantils 5 --dc_name "date"

parser = argparse.ArgumentParser(description='Executar script Python com parâmetros')
parser.add_argument('--cpf', type=str, required=True)
parser.add_argument('--filtro', type=str, required=False)


args = parser.parse_args()

# Define o nome do script que você quer executar
script_to_run = 'src\scrapper.py'  

# Monta os argumentos para passar para o subprocess
command = [
    'python', script_to_run,
    '--cpf', args.cpf,
    '--filtro', args.filtro,
]

# Executa o script com os argumentos
subprocess.run(command)