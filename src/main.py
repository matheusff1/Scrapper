from scrapper import PortalTransparenciaScraper, HumanBehavior
import argparse
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

parser = argparse.ArgumentParser(description='Script para busca de dados no Portal da Transparência')
parser.add_argument('--cpf', type=str, required=True, help='CPF da pessoa a ser buscada')
parser.add_argument('--filtro', type=str, required=False, help='Filtro adicional para a busca')
args = parser.parse_args()

cpf = args.cpf
filtro = args.filtro



options = webdriver.ChromeOptions()

options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """
})

scrapper = PortalTransparenciaScraper(cpf=cpf, driver=driver, filtro=filtro)
scrapper.run()

