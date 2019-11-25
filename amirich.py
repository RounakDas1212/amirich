import click
import requests
import pandas
from io import StringIO
import re
import os


class CurrencyCode(click.ParamType):
    name = 'symbol'

    def convert(self, value, param, ctx):
        if value.isalpha():
            return value.upper()
        self.fail('%s is not a valid symbol' % value, param, ctx)


class PortfolioEntry(click.ParamType):
    name = 'portfolio'

    def convert(self, value, param, ctx):
        if re.match("^[0-9]+x[A-Z]+$", value):
            arg_parts = value.split('x')
            return dict(
                symbol=arg_parts[1],
                count=int(arg_parts[0])
            )
        self.fail('%s does not follow the specified format: <Count>x<Symbol>. e.g. 100xMSFT' % value, param, ctx)


CURRENCY_CODE_TYPE = CurrencyCode()
PORTFOLIO_ENTRY_TYPE = PortfolioEntry()


@click.command()
@click.option('--in', '-i', 'in_currency', type=CURRENCY_CODE_TYPE, default='USD')
@click.argument('portfolios', type=PORTFOLIO_ENTRY_TYPE, nargs=-1)
def cli(portfolios, in_currency):
    """ Calcuate the value of stocks in chosen currency

    Pass in you portfolio in this format: <Count>x<Symbol>.
    For example, if you have 100 Microsoft stock, pass: 100xMSFT.
    The script will calculate the value of your portfolio.
    You can pass the `--in` parameter to specify a currency to use for the evaluation.
    The script will use the latest exchange rate for the day.
    \f

    :param tuple portfolios: Argument
    :param str in_currency: currency used for evaluation"""

    api_key = os.environ.get('ALPHAVANTAGE_API_KEY')
    if not api_key:
        click.echo('AlphaVantage API Key not set. Please set the ALPHAVANTAGE_API_KEY variable', err=True)
        raise click.ClickException('AlphaVantage API KEY not set!')

    alphavantage = AlphaVantage(api_key)

    total_in_usd = 0.0

    with click.progressbar(portfolios, label='Fetching the latest stock price', length=len(portfolios)) as pb:
        for portfolio in pb:
            latest_price = alphavantage.get_latest_stock_value(portfolio['symbol'])
            total_in_usd += latest_price * portfolio['count']

    click.echo("Total value in USD: {:20,.2f}".format(total_in_usd))

    if in_currency != 'USD':
        exchange_rate = alphavantage.get_latest_exchange_rate(to_currency=in_currency)
        click.echo("Latest exchange rate for {}: {} ".format(in_currency, exchange_rate))
        total_in_currency = total_in_usd * exchange_rate
        click.echo("Total value in {}: {:20,.2f}".format(in_currency, total_in_currency))


class AlphaVantage:

    BASE_URL = "https://www.alphavantage.co/query"
    TIME_SERIES_DAILY_FUNC = 'TIME_SERIES_DAILY'
    FOREX_FUNC = 'CURRENCY_EXCHANGE_RATE'

    def __init__(self, api_key):
        self._api_key = api_key

    def get_latest_stock_value(self, symbol):
        try:
            response = requests.get(
                self.BASE_URL,
                params=dict(
                    function=self.TIME_SERIES_DAILY_FUNC,
                    symbol=symbol,
                    apikey=self._api_key,
                    datatype='csv'
                )
            )
        except requests.exceptions.RequestException as e:
            # TODO: Error handling
            return
        data_table = pandas.read_csv(StringIO(response.text))
        return data_table.iloc[0]['close']

    def get_latest_exchange_rate(self, to_currency, from_currency='USD'):
        try:
            response = requests.get(
                self.BASE_URL,
                params=dict(
                    function=self.FOREX_FUNC,
                    from_currency=from_currency,
                    to_currency=to_currency,
                    apikey=self._api_key
                )
            )
        except requests.exceptions.RequestException as e:
            # TODO: Error handling
            return
        # FIXME: Don't like the hard-coded strings here, can we do something better?
        return float(response.json()['Realtime Currency Exchange Rate']['5. Exchange Rate'])


if __name__ == '__main__':
    cli()
