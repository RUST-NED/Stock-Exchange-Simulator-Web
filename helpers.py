import requests

# L82CMPPBCCTOC7FQ
# Alphavantage API key: L82CMPPBCCTOC7FQ
def get_stock_data(symbol, api_key):
    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
        response = requests.get(url)
        data1 = response.json()

        # get name of stock from symbol
        url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={symbol}&apikey={api_key}"
        response = requests.get(url)
        data2 = response.json()
        name = data2["bestMatches"][0]["2. name"]

        return {
            "name": name,
            "price": float(data1["Global Quote"]["05. price"]),
            "symbol": data1["Global Quote"]["01. symbol"]
        }
    except:
        return None
    # # return data["Global Quote"]["05. price"]

def usd(value):
    return f"${value:,.2f}"

# print(quote_stock("MSFT", "L82CMPPBCCTOC7FQ"))

def signin_user(session, user_name, api_key):
    session["user_name"] = user_name
    session["api_key"] = api_key


def signout_user(session):
    session.clear()