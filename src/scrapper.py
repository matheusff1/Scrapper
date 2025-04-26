from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time
import pandas as pd

class HumanBehavior:
    def __init__(self, driver):
        self.driver = driver

    def human_pause(self, min_seconds=1.5, max_seconds=3.5):
        time.sleep(random.uniform(min_seconds, max_seconds))

    def human_move_to_element(self, element):
        actions = ActionChains(self.driver)
        offset_x = random.randint(-5, 5)
        offset_y = random.randint(-5, 5)
        actions.move_to_element_with_offset(element, offset_x, offset_y).perform()
        self.human_pause(0.5, 1.5)

    def human_click(self, element):
        self.human_pause(0.3, 0.8)
        element.click()
    
    def human_scroll(self, amount='end'):
        if amount == 'end':
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        elif amount == 'top':
            self.driver.execute_script("window.scrollTo(0, 0);")
        else:
            self.driver.execute_script(f"window.scrollBy(0, {amount});")
        self.human_pause(1, 2)
    
    def wait_until_table(self, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            lambda d: (
                (celulas := d.find_elements(By.XPATH, '//*[@role="row" and (@class="odd" or @class="even")]/td'))
                and any(c.text.strip() for c in celulas)
            )
        )

class PortalTransparenciaScraper:
    def __init__(self, cpf, driver, filtro=""):
        self.cpf = cpf
        self.filtro = filtro
        self.driver = driver
        self.human = HumanBehavior(driver)
        self.base_url = 'https://portaldatransparencia.gov.br/pessoa-fisica/busca/lista?pagina=1&tamanhoPagina=10'
        self.df = pd.DataFrame()

    def __search_p1(self):
        self.driver.get(self.base_url)
        self.human.human_pause(3, 5)

        self.__verify_cookies()

        try:
            input_cpf = self.driver.find_element(By.ID, 'termo')
            self.human.human_move_to_element(input_cpf)
            input_cpf.send_keys(self.cpf)
        except Exception as e:
            print(f"Erro ao encontrar/clicar no campo CPF: {e}")
            return []

        self.human.human_pause(1, 2)

        try:
            botao = self.driver.find_element(By.ID, 'accordion1')
            self.human.human_move_to_element(botao)
            botao.click()
        except Exception as e:
            print(f"Erro ao encontrar/clicar no botão de filtro: {e}")
            return []

        self.human.human_pause(1.5, 3)

        if self.filtro != "":
            try:
                checkboxes = self.driver.find_elements(By.XPATH, '//input[@type="checkbox"]')
                for checkbox in checkboxes:
                    if self.filtro in checkbox.get_attribute('id'):
                        try:
                            label = self.driver.find_element(By.XPATH, f'//label[@for="{checkbox.get_attribute("id")}"]')
                            self.human.human_move_to_element(label)
                            label.click()
                            self.human.human_pause(0.8, 1.5)
                        except Exception as e:
                            print(f"Erro ao clicar no checkbox com id {checkbox.get_attribute('id')}: {e}")
            except Exception as e:
                print(f"Erro ao buscar checkboxes: {e}")
                return []

        try:
            consult_btn = self.driver.find_element(By.ID, 'btnConsultarPF')
            self.human.human_move_to_element(consult_btn)
            self.human.human_click(consult_btn)
        except Exception as e:
            print(f"Erro ao clicar no botão Consultar: {e}")
            return []

        self.human.human_pause(3, 6)

        self.human.human_scroll(amount=random.randint(-300, -100))

        try:
            items = self.driver.find_elements(By.CSS_SELECTOR, 'div.br-item.py-2.px-0[role="listitem"]')
        except Exception as e:
            print(f"Erro ao buscar os itens da lista: {e}")
            return []

        href_list = []
        for item in items:
            try:
                href = item.find_element(By.TAG_NAME, 'a').get_attribute('href')
                href_list.append(href)
            except Exception as e:
                print(f"Erro ao extrair href de um item: {e}")

        return href_list

        
    def __verify_p2(self, href):
        self.driver.get(href)
        self.human.human_pause(3, 5)

        self.__verify_cookies()

        try:
            received_resources = self.driver.find_element(By.XPATH, '//*[@aria-controls="accordion-recebimentos-recursos"]')
        except Exception as e:
            print(f"Erro ao encontrar o elemento de recursos recebidos: {e}")
            return

        self.human.human_move_to_element(received_resources)
        self.human.human_click(received_resources)

        self.human.human_pause(1, 2)

        try:
            details_buttons = self.driver.find_elements(By.XPATH, "//*[contains(@id, 'btnDetalhar')]")
        except Exception as e:
            print(f"Erro ao encontrar os botões de detalhes: {e}")
            return

        href_list = []
        resources_list = []
        for i in range(len(details_buttons)):
            resource = details_buttons[i].get_attribute('id')
            resource = resource[11:]
            href = details_buttons[i].get_attribute('href')
            href_list.append(href)
            resources_list.append(resource)
            self.human.human_pause(0.5, 1.5)
            self.human.human_move_to_element(details_buttons[i])

            if i % 2 == 0:
                self.human.human_scroll(amount=random.randint(-200, -50))
        
        return href_list, resources_list
    
    
    def __get_data_p3(self, href):
        self.driver.get(href)
        self.human.human_pause(3, 5)
        self.__verify_cookies()
        
        try:
            headers = self.driver.find_elements(By.XPATH,'//*[@scope="col" and @aria-controls="tabelaDetalheValoresRecebidos"]')
        except Exception as e:
            print(f"Erro ao encontrar os cabeçalhos: {e}")
            return

        columns = [col.text for col in headers]
        df = pd.DataFrame(columns=columns)
        self.human.human_pause(2, 4)

        try:
            btn_pagination = self.driver.find_element(By.ID, 'btnPaginacaoCompleta')
        except Exception as e:
            print(f"Erro ao encontrar o botão de paginação: {e}")
            return

        self.human.human_move_to_element(btn_pagination)
        self.human.human_click(btn_pagination)
        self.human.human_pause(4, 4)

        try:
            pagination = self.driver.find_element(By.XPATH, '//ul[@class="pagination"]')
            buttons = pagination.find_elements(By.CLASS_NAME, 'paginate_button')
        except Exception as e:
            print(f"Erro ao encontrar os botões de paginação: {e}")
            return

        for i in range(1, len(buttons) - 1):
            self.human.human_pause(0.5, 1.5)

            try:
                pagination = self.driver.find_element(By.XPATH, '//ul[@class="pagination"]')
                buttons = pagination.find_elements(By.CLASS_NAME, 'paginate_button')
            except Exception as e:
                print(f"Erro ao encontrar os botões de paginação: {e}")
                break

                
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", buttons[i])
            WebDriverWait(self.driver, 10).until(lambda d: buttons[i].is_displayed() and buttons[i].is_enabled())

            self.human.human_click(buttons[i])
            self.human.human_pause(0.6, 1.9)
            self.read_lines(df, self.driver)

        #rever função clean_df/ otimizar o uso da função
        self.df = self.__clean_df(df)
        

    def __process(self):
        href_list = self.__search_p1()
        for href in href_list:
            p2_hrefs, resources = self.__verify_p2(href)
            for i in range(len(p2_hrefs)):
                self.__get_data_p3(p2_hrefs[i])
                self.__save_to_csv(f"detalhes_{self.cpf}_{resources[i]}.csv")
                self.__save_to_json(f"detalhes_{self.cpf}_{resources[i]}.json")

    def run(self):
        try:
            self.__process()
            print("Processamento concluído com sucesso.")
        except Exception as e:
            print(f"Erro durante o processamento: {e}")
        finally:
            self.driver.quit()

    def read_lines(self):
        self.human.wait_until_table()

        linhas = self.driver.find_elements(By.XPATH, '//*[@role="row" and (@class="odd" or @class="even")]')

        for linha in linhas:

            dados = [celula.text for celula in linha.find_elements(By.TAG_NAME, "td")]
            self.df.loc[len(self.df)] = dados

            self.human.human_pause(0.2, 0.6)

    def __verify_cookies(self):
        try:
            cookies = self.driver.find_element(By.ID, 'accept-all-btn')
            self.human.human_move_to_element(cookies)
            cookies.click()
            self.human.human_pause()
        except:
            print("Cookies not found or already accepted.")

    def __save_to_csv(self, filename):
        try:
            self.df.to_csv(f'outputs/csv/{filename}', index=False)
        except Exception as e:
            print(f"Erro ao salvar o DataFrame: {e}")

    #rever função clean_df/ otimizar o uso da função
    def __clean_df(self, df):
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        df = df[~df.apply(lambda row: all(str(val) in df.columns for val in row), axis=1)]
        df = df[~(df == '').any(axis=1)]

        df.reset_index(drop=True, inplace=True)
        return df

    def __save_to_json(self, filename):
        try:
            self.df.to_json(f'outputs/json/{filename}', orient='records', lines=True)
        except Exception as e:
            print(f"Erro ao salvar o DataFrame: {e}")
