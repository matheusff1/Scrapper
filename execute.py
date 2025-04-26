import argparse
import subprocess
import os

# Comando de execução:
# python execute.py --cpf "161.012.713-24" --filtro "" 

parser = argparse.ArgumentParser(description='Executar script Python com parâmetros')
parser.add_argument('--cpf', type=str, required=True)
parser.add_argument('--filtro', type=str, required=False)


args = parser.parse_args()

script_to_run = 'src/main.py'  

command = [
    'python', script_to_run,
    '--cpf', args.cpf,
    '--filtro', args.filtro if args.filtro else "",
]

subprocess.run(command)