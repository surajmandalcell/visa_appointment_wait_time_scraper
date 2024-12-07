import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from typing import List, Optional, Dict, Union, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime
import os
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class ScraperConfig:
    selected_columns: Optional[List[str]] = None
    include_country: bool = True
    output_file: str = "visa_wait_times.csv"
    output_dir: str = "output"


class VisaWaitTimesScraper:
    BASE_URL = "https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/global-visa-wait-times.html"
    CITY_COUNTRY_MAP = {
        # North America
        "Ciudad Juarez": "Mexico",
        "Guadalajara": "Mexico",
        "Hermosillo": "Mexico",
        "Matamoros": "Mexico",
        "Merida": "Mexico",
        "Mexico City": "Mexico",
        "Monterrey": "Mexico",
        "Nogales": "Mexico",
        "Nuevo Laredo": "Mexico",
        "Tijuana": "Mexico",
        "Montreal": "Canada",
        "Ottawa": "Canada",
        "Quebec": "Canada",
        "Toronto": "Canada",
        "Vancouver": "Canada",
        "Calgary": "Canada",
        "Halifax": "Canada",
        "Mexicali Tpf": "Mexico",
        # Asia
        "Beijing": "China",
        "Guangzhou": "China",
        "Shanghai": "China",
        "Shenyang": "China",
        "Wuhan": "China",
        "Chengdu": "China",
        "Hong Kong": "Hong Kong",
        "Mumbai": "India",
        "New Delhi": "India",
        "Chennai": "India",
        "Hyderabad": "India",
        "Kolkata": "India",
        "Chennai ( Madras)": "India",
        "Tokyo": "Japan",
        "Osaka": "Japan",
        "Fukuoka": "Japan",
        "Naha": "Japan",
        "Sapporo": "Japan",
        "Seoul": "South Korea",
        "Taipei": "Taiwan",
        "Kaohsiung": "Taiwan",
        "Singapore": "Singapore",
        "Bangkok": "Thailand",
        "Chiang Mai": "Thailand",
        "Manila": "Philippines",
        "Ho Chi Minh City": "Vietnam",
        "Hanoi": "Vietnam",
        "Vladivostok": "Russia",
        "Yekaterinburg": "Russia",
        # Middle East and Central Asia
        "Dubai": "United Arab Emirates",
        "Abu Dhabi": "United Arab Emirates",
        "Jerusalem": "Israel",
        "Tel Aviv": "Israel",
        "Ankara": "Turkey",
        "Istanbul": "Turkey",
        "Adana": "Turkey",
        "Doha": "Qatar",
        "Kuwait City": "Kuwait",
        "Riyadh": "Saudi Arabia",
        "Dhahran": "Saudi Arabia",
        "Jeddah": "Saudi Arabia",
        "Almaty": "Kazakhstan",
        "Astana": "Kazakhstan",
        "Tashkent": "Uzbekistan",
        "Bishkek": "Kyrgyzstan",
        "Ashgabat": "Turkmenistan",
        "Dushanbe": "Tajikistan",
        # Europe
        "London": "United Kingdom",
        "Belfast": "United Kingdom",
        "Edinburgh": "United Kingdom",
        "Paris": "France",
        "Marseille": "France",
        "Berlin": "Germany",
        "Frankfurt": "Germany",
        "Munich": "Germany",
        "Rome": "Italy",
        "Milan": "Italy",
        "Naples": "Italy",
        "Florence": "Italy",
        "Madrid": "Spain",
        "Barcelona": "Spain",
        "Amsterdam": "Netherlands",
        "Brussels": "Belgium",
        "Moscow": "Russia",
        "St Petersburg": "Russia",
        "Vienna": "Austria",
        "Warsaw": "Poland",
        "Krakow": "Poland",
        "Prague": "Czech Republic",
        "Budapest": "Hungary",
        "Athens": "Greece",
        "Stockholm": "Sweden",
        "Oslo": "Norway",
        "Copenhagen": "Denmark",
        "Helsinki": "Finland",
        "Dublin": "Ireland",
        "Lisbon": "Portugal",
        "Bucharest": "Romania",
        "Sofia": "Bulgaria",
        "Belgrade": "Serbia",
        "Zagreb": "Croatia",
        "Sarajevo": "Bosnia and Herzegovina",
        "Skopje": "North Macedonia",
        "Podgorica": "Montenegro",
        "Pristina": "Kosovo",
        "Ljubljana": "Slovenia",
        "Bratislava": "Slovakia",
        "Tallinn": "Estonia",
        "Riga": "Latvia",
        "Vilnius": "Lithuania",
        "Minsk": "Belarus",
        "Kyiv": "Ukraine",
        "Chisinau": "Moldova",
        "Valletta": "Malta",
        "Reykjavik": "Iceland",
        "Bern": "Switzerland",
        "Ponta Delgada": "Portugal",
        # Africa
        "Cairo": "Egypt",
        "Alexandria": "Egypt",
        "Johannesburg": "South Africa",
        "Cape Town": "South Africa",
        "Durban": "South Africa",
        "Pretoria": "South Africa",
        "Nairobi": "Kenya",
        "Lagos": "Nigeria",
        "Abuja": "Nigeria",
        "Casablanca": "Morocco",
        "Dakar": "Senegal",
        "Addis Ababa": "Ethiopia",
        "Algiers": "Algeria",
        "Abidjan": "Côte d'Ivoire",
        "Accra": "Ghana",
        "Antananarivo": "Madagascar",
        "Asmara": "Eritrea",
        "Bamako": "Mali",
        "Bangui": "Central African Republic",
        "Banjul": "Gambia",
        "Brazzaville": "Republic of the Congo",
        "Bujumbura": "Burundi",
        "Conakry": "Guinea",
        "Cotonou": "Benin",
        "Dar Es Salaam": "Tanzania",
        "Freetown": "Sierra Leone",
        "Gaborone": "Botswana",
        "Harare": "Zimbabwe",
        "Juba": "South Sudan",
        "Kampala": "Uganda",
        "Khartoum": "Sudan",
        "Kigali": "Rwanda",
        "Kinshasa": "Democratic Republic of the Congo",
        "Libreville": "Gabon",
        "Lilongwe": "Malawi",
        "Lome": "Togo",
        "Luanda": "Angola",
        "Lusaka": "Zambia",
        "Malabo": "Equatorial Guinea",
        "Maputo": "Mozambique",
        "Maseru": "Lesotho",
        "Mbabane": "Eswatini",
        "Monrovia": "Liberia",
        "N`Djamena": "Chad",
        "Niamey": "Niger",
        "Nouakchott": "Mauritania",
        "Ouagadougou": "Burkina Faso",
        "Tripoli": "Libya",
        "Tunis": "Tunisia",
        "Windhoek": "Namibia",
        "Yaounde": "Cameroon",
        # Oceania and Pacific
        "Sydney": "Australia",
        "Melbourne": "Australia",
        "Perth": "Australia",
        "Canberra": "Australia",
        "Auckland": "New Zealand",
        "Wellington": "New Zealand",
        "Apia": "Samoa",
        "Suva": "Fiji",
        "Port Moresby": "Papua New Guinea",
        "Kolonia": "Micronesia",
        "Koror": "Palau",
        "Majuro": "Marshall Islands",
        # South and Central America
        "Buenos Aires": "Argentina",
        "Rio de Janeiro": "Brazil",
        "Sao Paulo": "Brazil",
        "Brasilia": "Brazil",
        "Recife": "Brazil",
        "Porto Alegre": "Brazil",
        "Santiago": "Chile",
        "Lima": "Peru",
        "Bogota": "Colombia",
        "Caracas": "Venezuela",
        "Asuncion": "Paraguay",
        "Montevideo": "Uruguay",
        "La Paz": "Bolivia",
        "Quito": "Ecuador",
        "Guayaquil": "Ecuador",
        "Georgetown": "Guyana",
        "Paramaribo": "Suriname",
        "Bridgetown": "Barbados",
        "Kingston": "Jamaica",
        "Nassau": "Bahamas",
        "Port Au Prince": "Haiti",
        "Santo Domingo": "Dominican Republic",
        "San Jose": "Costa Rica",
        "San Salvador": "El Salvador",
        "Managua": "Nicaragua",
        "Tegucigalpa": "Honduras",
        "Belmopan": "Belize",
        "Panama City": "Panama",
        "St Georges": "Grenada",
        "Port of Spain": "Trinidad and Tobago",
        # Other Regions and Special Cases
        "USUN-New York": "United States",
        "Usun-New York": "United States",
        "Vatican City": "Holy See",
        "Washington Refugee Processing Center": "United States",
        "Amman": "Jordan",
        "Djibouti": "Djibouti",
        "Guatemala City": "Guatemala",
        "Kuwait": "Kuwait",
        "Luxembourg": "Luxembourg",
        "Osaka/Kobe": "Japan",
        "Port Of Spain": "Trinidad and Tobago",
        "Rio De Janeiro": "Brazil",
        "Tijuana Tpf": "Mexico",
        "Tirana": "Albania",
        "Bandar Seri Begawan": "Brunei",
        "Beirut": "Lebanon",
        "Baghdad": "Iraq",
        "Erbil": "Iraq",
        "Baku": "Azerbaijan",
        "Colombo": "Sri Lanka",
        "Curacao": "Curaçao",
        "Damascus": "Syria",
        "Dhaka": "Bangladesh",
        "Dili": "Timor-Leste",
        "Hamilton": "Bermuda",
        "Havana": "Cuba",
        "Islamabad": "Pakistan",
        "Jakarta": "Indonesia",
        "Kabul": "Afghanistan",
        "Karachi": "Pakistan",
        "Kathmandu": "Nepal",
        "Kuala Lumpur": "Malaysia",
        "Lahore": "Pakistan",
        "Manama": "Bahrain",
        "Muscat": "Oman",
        "Nicosia": "Cyprus",
        "Phnom Penh": "Cambodia",
        "Port Louis": "Mauritius",
        "Praia": "Cape Verde",
        "Rangoon": "Myanmar",
        "Sanaa": "Yemen",
        "Surabaya": "Indonesia",
        "Tbilisi": "Georgia",
        "Ulaanbaatar": "Mongolia",
        "Vientiane": "Laos",
        "Yerevan": "Armenia",
    }

    def __init__(self, config: ScraperConfig):
        self.config = config
        self._ensure_output_directory()

    def _ensure_output_directory(self) -> None:
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)

    def _get_country(self, city: str) -> str:
        city = city.strip()
        if city in self.CITY_COUNTRY_MAP:
            return self.CITY_COUNTRY_MAP[city]

        city_variations = [
            city,
            city.replace("-", " "),
            city.split(",")[0].strip(),
            city.split("(")[0].strip(),
        ]

        for variation in city_variations:
            if variation in self.CITY_COUNTRY_MAP:
                return self.CITY_COUNTRY_MAP[variation]

        logger.warning(f"Unknown city: {city}")
        return "Unknown"

    def _parse_table_data(
        self, table: BeautifulSoup
    ) -> Tuple[List[str], List[List[str]]]:
        headers = [re.sub(r"\s+", " ", th.text.strip()) for th in table.find_all("th")]

        data = []
        for row in table.find_all("tr")[1:]:
            cols = row.find_all('td')
            if cols:
                row_data = [col.text.strip() or "N/A" for col in cols]
                data.append(row_data)

        return headers, data

    def _create_dataframe(
        self, headers: List[str], data: List[List[str]]
    ) -> pd.DataFrame:
        df = pd.DataFrame(data, columns=headers)

        if self.config.include_country:
            df["Country"] = df["City/Post"].apply(self._get_country)
            self._log_country_statistics(df)

        if self.config.selected_columns:
            required_cols = ["City/Post"]
            if self.config.include_country:
                required_cols.append("Country")

            selected_cols = list(
                dict.fromkeys(required_cols + self.config.selected_columns)
            )
            existing_cols = [col for col in selected_cols if col in df.columns]
            df = df[existing_cols]

        return df

    def _log_country_statistics(self, df: pd.DataFrame) -> None:
        total_cities = len(df)
        unknown_countries = len(df[df["Country"] == "Unknown"])
        success_rate = (total_cities - unknown_countries) / total_cities * 100

        logger.info(f"\nCountry Detection Statistics:")
        logger.info(f"Total cities: {total_cities}")
        logger.info(f"Successfully mapped: {total_cities - unknown_countries}")
        logger.info(f"Unknown countries: {unknown_countries}")
        logger.info(f"Success rate: {success_rate:.2f}%")

        if unknown_countries > 0:
            logger.warning("\nCities with unknown countries:")
            logger.warning(df[df["Country"] == "Unknown"]["City/Post"].tolist())

    def scrape(self) -> Optional[pd.DataFrame]:
        try:
            response = requests.get(self.BASE_URL)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table")

            if not table:
                raise ValueError("Table not found on the page")

            headers, data = self._parse_table_data(table)
            df = self._create_dataframe(headers, data)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.config.output_file.rsplit('.', 1)[0]}_{timestamp}.csv"
            output_path = os.path.join(self.config.output_dir, filename)

            df.to_csv(output_path, index=False)
            logger.info(f"\nData successfully scraped and saved to {output_path}")

            return df

        except requests.RequestException as e:
            logger.error(f"Error fetching data: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            return None


def run_all_configurations() -> Dict[str, Optional[pd.DataFrame]]:
    results = {}

    configs = {
        "default": ScraperConfig(output_file="visa_wait_times_default.csv"),
        "selected_columns": ScraperConfig(
            selected_columns=[
                "Interview Required Visitors (B1/B2)",
                # 'Interview Required Student/Exchange Visitors (F, M, J)'
            ],
            output_file="visa_wait_times_selected.csv",
        ),
        "no_country": ScraperConfig(
            include_country=False, output_file="visa_wait_times_no_country.csv"
        ),
    }

    for config_name, config in configs.items():
        logger.info(f"\nRunning {config_name} configuration...")
        scraper = VisaWaitTimesScraper(config)
        results[config_name] = scraper.scrape()

    return results


def main():
    logger.info("Starting visa wait times scraping process...")
    results = run_all_configurations()

    success_count = sum(1 for df in results.values() if df is not None)
    total_configs = len(results)

    logger.info(f"\nScraping process completed:")
    logger.info(f"Successful configurations: {success_count}/{total_configs}")

    if success_count < total_configs:
        logger.warning("Some configurations failed. Check the logs above for details.")

    return results


if __name__ == "__main__":
    main()
