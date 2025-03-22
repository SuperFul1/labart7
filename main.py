import json
import matplotlib.pyplot as plt
import os
import requests
import csv
import time
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from typing import List, Dict, Union, Tuple


class CurrenciesInterface(ABC):

    @abstractmethod
    def get_currencies(self, url: str, save_data: bool,
                       file_name: str) -> Union[List[Dict[str, str]], str]:
        pass

    @abstractmethod
    def get_currency_value(
            self, currency_identifier: str
    ) -> Union[None, Tuple[str, str, str, str]]:
        pass

    @abstractmethod
    def visualize_currencies(self, save_to_file: bool, file_name: str) -> None:
        pass


class Currencies(CurrenciesInterface):
    last_updated: int = 0
    update_interval: int = 3600

    def get_currencies(
        self,
        url: str = 'http://www.cbr.ru/scripts/XML_daily.asp',
        save_data: bool = False,
        file_name: str = 'currencies.json'
    ) -> Union[List[Dict[str, str]], str]:

        curr_time = time.time()

        if os.path.exists(file_name) and os.stat(file_name).st_size > 0:
            with open(file_name, 'r', encoding='utf-8') as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    pass
        response = requests.get(url)

        if response.status_code == 200:
            xml_data = response.content
            soup = BeautifulSoup(xml_data, 'xml')
            all_valutes = soup.find_all('Valute')

            currencies_list = []
            for valute in all_valutes:
                name = valute.find('Name').text.strip()
                code = valute.find('CharCode').text.strip()
                value = valute.find('Value').text.strip()
                nominal = valute.find('Nominal').text.strip()
                currencies_list.append({
                    'name': name,
                    'code': code,
                    'value': value,
                    'nominal': nominal
                })

            if save_data:
                with open(file_name, 'w', encoding='utf-8') as file:
                    json.dump(currencies_list, file, ensure_ascii=False, indent=2)

            self.last_updated = curr_time
            return currencies_list
        return "Failed to fetch data"

    def get_currency_value(
            self, currency_identifier: str
    ) -> Union[None, Tuple[str, str, str, str]]:
        currencies = self.get_currencies()
        if isinstance(currencies, list):
            for currency in currencies:
                if currency_identifier in (currency['code'], currency['name']):
                    return (currency['name'], currency['code'], 
                           currency['value'], currency['nominal'])
        return None

    def visualize_currencies(self, save_to_file: bool = False,
                           file_name: str = 'currency_plot.png') -> None:
        currencies = self.get_currencies()
        if isinstance(currencies, list):
            codes = [curr['code'] for curr in currencies]
            values = [float(curr['value'].replace(',', '.')) for curr in currencies]
            
            plt.figure(figsize=(15, 7))
            plt.bar(codes, values)
            plt.xticks(rotation=45)
            plt.title('Currency Values')
            plt.xlabel('Currency Code')
            plt.ylabel('Value (RUB)')
            
            if save_to_file:
                plt.savefig(file_name)
            plt.show()

if __name__ == "__main__":
    curr = Currencies()
    currencies = curr.get_currencies(save_data=True)
    curr.visualize_currencies(save_to_file=True)
