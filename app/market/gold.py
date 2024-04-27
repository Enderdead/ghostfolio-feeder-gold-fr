import csv
import json
import os
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime, timedelta
# Import utils
try:
    from market import utils
except ImportError:
    import utils


_GOLD_TICKER_URL = {
   "NapCoq20F" :  "https://www.gold.fr/napoleon-or-20-francs-louis-or/?begin_date={origin_year}&compare_to=#graphs",
   "Nap20F"    :  "https://www.gold.fr/napoleon-20-francs-non-boursable/?begin_date={origin_year}&compare_to=#graphs",
   "1KgGoldBar":  "https://www.gold.fr/lingot-d-or-1-kg/?begin_date={origin_year}&compare_to=#graphs",
   "500gGoldBar"    :  "https://www.gold.fr/lingotin-d-or-500g/?begin_date={origin_year}&compare_to=#graphs",
   "250gGoldBar"    :  "https://www.gold.fr/lingotin-d-or-250g/?begin_date={origin_year}&compare_to=#graphs",
   "100gGoldBar"    :  "https://www.gold.fr/lingotin-d-or-100g/?begin_date={origin_year}&compare_to=#graphs",
   "50gGoldBar"    :  "https://www.gold.fr/lingotin-d-or-50g/?begin_date={origin_year}&compare_to=#graphs",
   "10gGoldBar"    :  "https://www.gold.fr/lingotin-d-or-50g/?begin_date={origin_year}&compare_to=#graphs",
   "5gGoldBar"    :  "https://www.gold.fr/lingotin-d-or-5g/?begin_date={origin_year}&compare_to=#graphs",
   "Eagle20" :  "https://www.gold.fr/20-us/?begin_date={origin_year}&compare_to=#graphs",
   "Eagle10" :  "https://www.gold.fr/10-us/?begin_date={origin_year}&compare_to=#graphs",
   "Eagle5" :  "https://www.gold.fr/10-us/?begin_date={origin_year}&compare_to=#graphs",
   "Swiss20F" :  "https://www.gold.fr/20-francs-suisses/?begin_date={origin_year}&compare_to=#graphs",
   "50Pesos" :  "https://www.gold.fr/50-pesos/?begin_date={origin_year}&compare_to=#graphs",
   "Krug" :  "https://www.gold.fr/krugerrand/?begin_date={origin_year}&compare_to=#graphs",
   "GeoSovGV" :  "https://www.gold.fr/souverain/?begin_date={origin_year}&compare_to=#graphs",
   "ElizSovEII" :  "https://www.gold.fr/elisabeth-ii/?begin_date={origin_year}&compare_to=#graphs",
   "NapCoq10F" :  "https://www.gold.fr/demi-napoleon/?begin_date={origin_year}&compare_to=#graphs",
   "HalfSov" :  "https://www.gold.fr/demi-souverain/?begin_date={origin_year}&compare_to=#graphs",
   "Flor10" :  "https://www.gold.fr/10-florins?begin_date={origin_year}&compare_to=#graphs",
   "Reich20" :  "https://www.gold.fr/reichmark/?begin_date={origin_year}&compare_to=#graphs",
   "UL20F" :  "https://www.gold.fr/union-latine/?begin_date={origin_year}&compare_to=#graphs",
   "BritGold1-4Oz" :  "https://www.gold.fr/britannia-1-4-oz-or/?begin_date={origin_year}&compare_to=#graphs",
   "BritSilverOz" :  "https://www.gold.fr/britannia-1oz/?begin_date={origin_year}&compare_to=#graphs",
}



def _recover_data(name, origin_year):
    if not (name in _GOLD_TICKER_URL):
        raise RuntimeError("Ticker unknown from the gold_fr database !")
    response = requests.get(_GOLD_TICKER_URL[name].format(origin_year=origin_year))

    # Check if the request succeed
    if response.status_code == 200:
        # Load the content to b4
        soup = BeautifulSoup(response.text, 'html.parser')
    else:
        raise(f"Unable to load the page (receive code: {response.status_code})")


    script_list = soup.findAll("script")


    for script in script_list:
        if "series" in script.text:
            target_script = script.text
            break
    # Use regex to load all the JS static data
    allprice = re.findall("Date.UTC\(20[0-9][0-9], [0-9]*\s*,\s*[0-9]*\), [0-9.]*", target_script)

    # Recover dates and values
    dates = [re.findall(r'Date.UTC\((\d+),\s*(\d+)\s*,\s*(\d+)\)', element)[0] for element in allprice]
    valeurs = [float(re.findall(r'\),\s*([\d.]+)', element)[0]) for element in allprice]

    # Convert into datatime
    dates_converties = [datetime(int(d[0]), int(d[1])+1, int(d[2])) for d in dates]

    # Return df
    return pd.DataFrame(index=dates_converties, data={"marketPrice": valeurs})

def gold_fr(ticker: str, start_date: str | None = None, end_date: str | None = None) -> list:
    """
    Retrieve market data for a given ticker from a local JSON and from gold fr API.

    Args:
        ticker (str): The ticker symbol for the market data.
        start_date (str, optional): The start date in "YYYY-MM-DD" format. Defaults to None.
        end_date (str, optional): The end date in "YYYY-MM-DD" format. Defaults to None.

    Returns:
        list: A list of dictionaries containing historical market data in the following format:
            {'date': 'yyyy-mm-dd', 'marketPrice': int}

    Raises:
        ValueError: If the file format is not supported. Only JSON or CSV files are supported.
    """

    # Define the file path
    file_path = os.path.join("data","local",ticker.lower()+".csv")

    # Check if  data file exists.
    if os.path.exists(file_path):
        data_df = pd.read_csv(file_path) #date,marketPrice
        data_df['date'] = pd.to_datetime(data_df['date'])
        data_df.set_index('date', inplace=True)
        start_year = min(data_df.index[-1].year, int(start_date.split("-")[0]))

    else:
        # If file doesn't exist start downloading data sequencially from the start date.
        data_df = pd.DataFrame()
        start_year = int(start_date.split("-")[0])




    # Recover data sequentially in order to fix the myope data realize of the website.
    end_year = datetime.now().year + 1

    for year in range(start_year, end_year):
        batch_df = _recover_data(ticker, year)
        if len(data_df)>0:
            merged_data_df = pd.merge(data_df, batch_df, left_index=True, right_index=True, how='outer',suffixes=('_df1', '_df2'))
            merged_data_df["marketPrice"] =  merged_data_df['marketPrice_df1'].combine_first(merged_data_df['marketPrice_df2'])
            data_df = merged_data_df[["marketPrice"]]
        else:
            data_df = batch_df
    # Save data 
    data_df.to_csv(file_path, index_label="date")

    # Filter data according to the starte_date and end_date
    if end_date is not None:
        data_df = data_df[data_df.index<datetime.strptime(end_date, "%Y-%m-%d")]
    data_df = data_df[data_df.index>datetime.strptime(start_date, "%Y-%m-%d")]

    # Conver to the original depo pur python datatype
    marked_data_converted = list()
    for idx, row in data_df.iterrows():
        marked_data_converted.append({ "date" : idx.strftime("%Y-%m-%d") ,  "marketPrice": float(row["marketPrice"])})

    # Fill missing dates
    marked_data_converted = utils.fill_missing_dates(marked_data_converted, start_date=start_date, end_date=end_date)

    return marked_data_converted


if __name__ == "__main__":
    utils.print_list(gold_fr("250gGoldBar", start_date="2012-01-01"))
