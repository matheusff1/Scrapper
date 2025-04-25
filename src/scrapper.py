from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time
import argparse
import pandas as pd

"""
parser = argparse.ArgumentParser(description='Script para busca de dados no Portal da Transparência')
parser.add_argument('--cpf', type=str, required=True, help='CPF da pessoa a ser buscada')
parser.add_argument('--filtro', type=str, required=False, help='Filtro adicional para a busca')
args = parser.parse_args()
########
cpf = args.cpf
filtro = args.filtro
"""

cpf = "161.012.713-24"
filtro = ""

options = webdriver.ChromeOptions()

options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)

driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """
})

def human_pause(min_seconds=1.5, max_seconds=3.5):
    time.sleep(random.uniform(min_seconds, max_seconds))

def clean_df(df):
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df = df[~df.apply(lambda row: all(str(val) in df.columns for val in row), axis=1)]
    df = df[~(df == '').any(axis=1)]

    df.reset_index(drop=True, inplace=True)
    return df


def save_to_csv(df, filename):
    try:
        df.to_csv(f'outputs/{filename}', index=False)
        print(f"DataFrame salvo em outputs/{filename}")
    except Exception as e:
        print(f"Erro ao salvar o DataFrame: {e}")

def human_scroll(driver, amount='end'):
    if amount == 'end':
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    elif amount == 'top':
        driver.execute_script("window.scrollTo(0, 0);")
    else:
        driver.execute_script(f"window.scrollBy(0, {amount});")
    human_pause(1, 2)

def human_move_to_element(driver, element):
    actions = ActionChains(driver)
    offset_x = random.randint(-5, 5)
    offset_y = random.randint(-5, 5)
    actions.move_to_element_with_offset(element, offset_x, offset_y).perform()
    human_pause(0.5, 1.5)

def human_click(element):
    human_pause(0.3, 0.8)
    element.click()

def verify_cookies(driver):
    try:
        cookies = driver.find_element(By.ID, 'accept-all-btn')
        human_move_to_element(driver, cookies)
        cookies.click()
        human_pause()
    except:
        print("Cookies not found or already accepted.")

def wait_until_table(driver, timeout=10):
    WebDriverWait(driver, timeout).until(
        lambda d: (
            (celulas := d.find_elements(By.XPATH, '//*[@role="row" and (@class="odd" or @class="even")]/td'))
            and any(c.text.strip() for c in celulas)
        )
    )

def read_lines(df, driver):
    wait_until_table(driver)
    print("Lendo linhas...")
    linhas = driver.find_elements(By.XPATH, '//*[@role="row" and (@class="odd" or @class="even")]')
    for linha in linhas:
        dados = [celula.text for celula in linha.find_elements(By.TAG_NAME, "td")]
        df.loc[len(df)] = dados
        print(dados)
        print("-----------------------------------------------------")
        human_pause(0.2, 0.6)


def p1_achar_pessoa(cpf, filtro, driver):
    driver.get('https://portaldatransparencia.gov.br/pessoa-fisica/busca/lista?pagina=1&tamanhoPagina=10')

    human_pause(3, 5)

    verify_cookies(driver)

    input_cpf = driver.find_element(By.ID, 'termo')
    human_move_to_element(driver, input_cpf)
    input_cpf.send_keys(cpf)

    human_pause(1, 2)

    botao = driver.find_element(By.ID, 'accordion1')
    human_move_to_element(driver, botao)
    botao.click()

    human_pause(1.5, 3)

    if filtro != "":
        checkboxes = driver.find_elements(By.XPATH, '//input[@type="checkbox"]')
        for checkbox in checkboxes:
            print(checkbox.get_attribute('id'))
            if (filtro in checkbox.get_attribute('id')):
                label = driver.find_element(By.XPATH, f'//label[@for="{checkbox.get_attribute("id")}"]')
                human_move_to_element(driver, label)
                label.click()
                human_pause(0.8, 1.5)

    consultar = driver.find_element(By.ID, 'btnConsultarPF')
    human_move_to_element(driver, consultar)
    human_click(consultar)

    human_pause(3, 6)

    human_scroll(driver, amount=random.randint(-300, -100))  
    human_scroll(driver)  

    items = driver.find_elements(By.CSS_SELECTOR, 'div.br-item.py-2.px-0[role="listitem"]')

    for item in items:
        print(item.text)
        href = item.find_element(By.TAG_NAME, 'a').get_attribute('href')
        p2_aprofundar_busca(driver, href)
        print("-----------------------------------------------------")

    human_pause(10, 15)


def p2_aprofundar_busca(driver, href):
    driver.get(href)
    human_pause(3, 5)

    verify_cookies(driver)

    recebimentos = driver.find_element(By.XPATH, '//*[@aria-controls="accordion-recebimentos-recursos"]')
    human_move_to_element(driver, recebimentos)
    human_click(recebimentos)

    human_pause(1, 2)

    detalhar = driver.find_elements(By.XPATH, "//*[contains(@id, 'btnDetalhar')]")
    for i in range(len(detalhar)):
        href = detalhar[i].get_attribute('href')
        human_pause(0.5, 1.5)
        human_move_to_element(driver, detalhar[i])

        if i % 2 == 0:
            human_scroll(driver, amount=random.randint(-200, -50))

        p3_acessar_detalhes(driver, href)


def p3_acessar_detalhes(driver, href):
    driver.get(href)
    human_pause(3, 5)
    verify_cookies(driver)

    colunas = driver.find_elements(By.XPATH,
        '//*[@scope="col" and @aria-controls="tabelaDetalheValoresRecebidos"]')
    columns = [col.text for col in colunas]
    df = pd.DataFrame(columns=columns)
    human_pause(2, 4)

    btn_pagina = driver.find_element(By.ID, 'btnPaginacaoCompleta')
    human_move_to_element(driver, btn_pagina)
    human_click(btn_pagina)
    time.sleep(4)

    pagination = driver.find_element(By.XPATH, '//ul[@class="pagination"]')
    buttons = pagination.find_elements(By.CLASS_NAME, 'paginate_button')

    for i in range(1, len(buttons) - 1):
        human_pause(0.5, 1.5)
        pagination = driver.find_element(By.XPATH, '//ul[@class="pagination"]')
        buttons = pagination.find_elements(By.CLASS_NAME, 'paginate_button')

        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});",buttons[i])
        WebDriverWait(driver, 10).until(lambda d: buttons[i].is_displayed() and buttons[i].is_enabled())

        human_click(buttons[i])
        human_pause(0.6, 1.9)
        read_lines(df, driver)



    for i in df.iterrows():
        print(i)
        print("-----------------------------------------------------")


    print(df.isnull().sum())
    print(df.isna())
    df = clean_df(df)
    print(df.info())
    save_to_csv(df, f"detalhes_{cpf}.csv")

# Chamando a função de teste
p3_acessar_detalhes(
    driver,
    "https://portaldatransparencia.gov.br/beneficios/bolsa-familia/271756870?ordenarPor=mesReferencia&direcao=desc"
)
