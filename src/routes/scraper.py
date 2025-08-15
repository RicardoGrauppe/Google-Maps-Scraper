from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import json
import time
import re
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import requests
from bs4 import BeautifulSoup
import pandas as pd

scraper_bp = Blueprint('scraper', __name__)

class GoogleMapsScraper:
    def __init__(self):
        self.driver = None
        self.results = []
    
    def setup_driver(self):
        """Configura o driver do Chrome para scraping"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Usar o Google Chrome instalado
        chrome_options.binary_location = '/usr/bin/google-chrome-stable'
        
        # Usar webdriver-manager para baixar automaticamente o ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Remover propriedades que indicam automação
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return self.driver
    
    def extract_contact_from_website(self, website_url, timeout=10):
        """Extrai informações de contato do website da empresa"""
        contact_info = {
            'emails': [],
            'phones': [],
            'social_media': {}
        }
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(website_url, headers=headers, timeout=timeout)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            text_content = soup.get_text()
            
            # Extrair emails
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, text_content)
            contact_info['emails'] = list(set(emails))
            
            # Extrair telefones (formato brasileiro e internacional)
            phone_patterns = [
                r'\(\d{2}\)\s*\d{4,5}-?\d{4}',  # (11) 99999-9999
                r'\d{2}\s*\d{4,5}-?\d{4}',      # 11 99999-9999
                r'\+55\s*\d{2}\s*\d{4,5}-?\d{4}' # +55 11 99999-9999
            ]
            
            phones = []
            for pattern in phone_patterns:
                phones.extend(re.findall(pattern, text_content))
            contact_info['phones'] = list(set(phones))
            
            # Extrair redes sociais
            social_patterns = {
                'facebook': r'facebook\.com/[A-Za-z0-9._-]+',
                'instagram': r'instagram\.com/[A-Za-z0-9._-]+',
                'linkedin': r'linkedin\.com/[A-Za-z0-9._/-]+',
                'twitter': r'twitter\.com/[A-Za-z0-9._-]+',
                'whatsapp': r'wa\.me/[0-9]+|api\.whatsapp\.com/send\?phone=[0-9]+'
            }
            
            for platform, pattern in social_patterns.items():
                matches = re.findall(pattern, text_content)
                if matches:
                    contact_info['social_media'][platform] = matches[0]
            
        except Exception as e:
            print(f"Erro ao extrair contato do website {website_url}: {str(e)}")
        
        return contact_info
    
    def scrape_google_maps(self, search_query, max_results=50):
        """Faz scraping do Google Maps baseado em uma query de busca"""
        self.results = []
        
        try:
            self.setup_driver()
            
            # Construir URL de busca do Google Maps
            search_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
            print(f"Acessando URL: {search_url}")
            self.driver.get(search_url)
            
            # Aguardar carregamento da página
            time.sleep(5)
            
            # Aguardar elementos carregarem
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[role='main']"))
                )
            except TimeoutException:
                print("Timeout aguardando carregamento da página")
                return self.results
            
            # Encontrar o painel de resultados
            try:
                results_panel = self.driver.find_element(By.CSS_SELECTOR, "[role='main']")
            except NoSuchElementException:
                print("Painel de resultados não encontrado")
                return self.results
            
            # Rolar para carregar mais resultados
            print("Rolando para carregar mais resultados...")
            for i in range(10):  # Rolar mais vezes para carregar mais resultados
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", results_panel)
                time.sleep(2)
                print(f"Scroll {i+1}/10")
            
            # Aguardar um pouco mais após o scroll
            time.sleep(3)
            
            # Encontrar todos os resultados usando diferentes seletores
            business_elements = []
            selectors = [
                "[data-result-index]",
                "div[jsaction*='mouseover']",
                "a[data-value='Directions']",
                ".hfpxzc",
                "[role='article']"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        business_elements = elements
                        print(f"Encontrados {len(elements)} elementos com seletor: {selector}")
                        break
                except:
                    continue
            
            if not business_elements:
                print("Nenhum elemento de negócio encontrado")
                return self.results
            
            print(f"Processando {min(len(business_elements), max_results)} resultados...")
            
            # Processar cada resultado
            for i, element in enumerate(business_elements[:max_results]):
                try:
                    print(f"Processando resultado {i+1}/{min(len(business_elements), max_results)}")
                    
                    # Scroll para o elemento para garantir que está visível
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    time.sleep(1)
                    
                    # Clicar no elemento para abrir detalhes
                    element.click()
                    time.sleep(3)
                    
                    business_data = self.extract_business_details()
                    if business_data and business_data.get('name') and business_data['name'] != "N/A":
                        self.results.append(business_data)
                        print(f"Dados extraídos para: {business_data.get('name', 'Nome não encontrado')}")
                    else:
                        print(f"Dados insuficientes para o resultado {i+1}")
                    
                except Exception as e:
                    print(f"Erro ao processar resultado {i+1}: {str(e)}")
                    continue
            
            print(f"Scraping concluído. Total de resultados: {len(self.results)}")
            
        except Exception as e:
            print(f"Erro durante scraping: {str(e)}")
        
        finally:
            if self.driver:
                self.driver.quit()
        
        return self.results
    
    def extract_business_details(self):
        """Extrai detalhes de um negócio específico"""
        business_data = {}
        
        try:
            # Aguardar carregamento dos detalhes
            time.sleep(2)
            
            # Nome do negócio - tentar diferentes seletores
            name_selectors = [
                "h1[data-attrid='title']",
                "h1.DUwDvf",
                ".x3AX1-LfntMc-header-title-title",
                ".SPZz6b h1",
                "h1"
            ]
            
            for selector in name_selectors:
                try:
                    name_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if name_element and name_element.text.strip():
                        business_data['name'] = name_element.text.strip()
                        break
                except:
                    continue
            
            if not business_data.get('name'):
                business_data['name'] = "N/A"
            
            # Avaliação
            rating_selectors = [
                ".F7nice span[aria-hidden='true']",
                ".MW4etd",
                "span.ceNzKf"
            ]
            
            for selector in rating_selectors:
                try:
                    rating_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if rating_element and rating_element.text.strip():
                        business_data['rating'] = rating_element.text.strip()
                        break
                except:
                    continue
            
            if not business_data.get('rating'):
                business_data['rating'] = "N/A"
            
            # Endereço
            address_selectors = [
                "[data-item-id='address'] .Io6YTe",
                ".Io6YTe.fontBodyMedium",
                "button[data-item-id='address']",
                ".rogA2c .Io6YTe"
            ]
            
            for selector in address_selectors:
                try:
                    address_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if address_element and address_element.text.strip():
                        business_data['address'] = address_element.text.strip()
                        break
                except:
                    continue
            
            if not business_data.get('address'):
                business_data['address'] = "N/A"
            
            # Telefone
            phone_selectors = [
                "[data-item-id='phone'] .Io6YTe",
                "button[data-item-id='phone']",
                ".rogA2c[data-item-id='phone'] .Io6YTe"
            ]
            
            for selector in phone_selectors:
                try:
                    phone_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if phone_element and phone_element.text.strip():
                        business_data['phone'] = phone_element.text.strip()
                        break
                except:
                    continue
            
            if not business_data.get('phone'):
                business_data['phone'] = "N/A"
            
            # Website
            website_selectors = [
                "[data-item-id='authority'] a",
                "a[data-item-id='authority']",
                ".CsEnBe[data-item-id='authority'] a"
            ]
            
            for selector in website_selectors:
                try:
                    website_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if website_element:
                        href = website_element.get_attribute('href')
                        if href and href.startswith('http'):
                            business_data['website'] = href
                            break
                except:
                    continue
            
            if not business_data.get('website'):
                business_data['website'] = "N/A"
            
            # URL do Google Maps
            business_data['google_maps_url'] = self.driver.current_url
            
            # Extrair informações de contato do website se disponível
            if business_data.get('website') and business_data['website'] != "N/A":
                try:
                    contact_info = self.extract_contact_from_website(business_data['website'])
                    business_data.update(contact_info)
                except:
                    # Se falhar, adicionar campos vazios
                    business_data['emails'] = []
                    business_data['phones'] = []
                    business_data['social_media'] = {}
            else:
                business_data['emails'] = []
                business_data['phones'] = []
                business_data['social_media'] = {}
            
            print(f"Dados extraídos: {business_data.get('name', 'N/A')}")
            
        except Exception as e:
            print(f"Erro ao extrair detalhes do negócio: {str(e)}")
            # Retornar dados básicos mesmo com erro
            if not business_data.get('name'):
                business_data['name'] = "N/A"
            if not business_data.get('address'):
                business_data['address'] = "N/A"
            if not business_data.get('phone'):
                business_data['phone'] = "N/A"
            if not business_data.get('website'):
                business_data['website'] = "N/A"
            if not business_data.get('rating'):
                business_data['rating'] = "N/A"
            business_data['google_maps_url'] = self.driver.current_url if self.driver else "N/A"
            business_data['emails'] = []
            business_data['phones'] = []
            business_data['social_media'] = {}
        
        return business_data

@scraper_bp.route('/scrape', methods=['POST'])
@cross_origin()
def scrape_businesses():
    """Endpoint para fazer scraping de empresas"""
    try:
        data = request.get_json()
        search_query = data.get('search_query', '')
        max_results = data.get('max_results', 50)
        
        if not search_query:
            return jsonify({'error': 'search_query é obrigatório'}), 400
        
        scraper = GoogleMapsScraper()
        results = scraper.scrape_google_maps(search_query, max_results)
        
        return jsonify({
            'success': True,
            'total_results': len(results),
            'results': results
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@scraper_bp.route('/export', methods=['POST'])
@cross_origin()
def export_results():
    """Endpoint para exportar resultados em CSV"""
    try:
        data = request.get_json()
        results = data.get('results', [])
        
        if not results:
            return jsonify({'error': 'Nenhum resultado para exportar'}), 400
        
        # Converter para DataFrame
        df = pd.DataFrame(results)
        
        # Salvar como CSV
        csv_filename = f"google_maps_results_{int(time.time())}.csv"
        csv_path = f"/home/ubuntu/google-maps-scraper/src/static/{csv_filename}"
        df.to_csv(csv_path, index=False, encoding='utf-8')
        
        return jsonify({
            'success': True,
            'download_url': f'/static/{csv_filename}',
            'filename': csv_filename
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@scraper_bp.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """Endpoint para verificar se o serviço está funcionando"""
    return jsonify({
        'status': 'healthy',
        'service': 'Google Maps Scraper',
        'version': '1.0.0'
    })

