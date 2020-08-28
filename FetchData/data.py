import pdblp
import numpy as np
import pandas as pd
import datetime as dt
import math

def bbg_conn(debug=False):
    return pdblp.BCon(debug = debug, port = 8194, timeout = 150000)

tenor_map = pd.DataFrame(data={'bdays': [1,5,10,15,21,42,63,84,126,189,252,378,504,756,1008,1260,1512,1764,2016,2268,
                                         2520,3780,5040,6300,7560],
                               'months':[1/21,5/21,10/21,15/21,1,2,3,4,6,9,12,18,24,36,48,60,72,84,96,108,120,180,240,
                                         300,360],
                               'years':[1/252,5/252,10/252,15/252,1/12,2/12,0.25,1/3,0.5,0.75,1,1.5,2,3,4,5,6,7,
                                        8,9,10,15,20,25,30]},
                         index=['1d','1w','2w','3w','1m','2m','3m', '4m','6m','9m','1y','18m',
                                '2y','3y','4y','5y','6y','7y','8y','9y','10y','15y','20y','25y','30y'])

class holding():
    def __init__(self, underlier, instrument, expN, proxy_vol_type, proxy_k):
        self.underlier = underlier
        self.instrument = instrument
        self.expN = expN
        self.proxy_vol_type = proxy_vol_type
        self.proxy_k = proxy_k

    def __str__(self):
        return("I am a " + str(self.expN) + "d " + self.instrument + " on" + self.underlier +
               " being proxyed by a " + str(self.proxy_k) + " " + self.proxy_vol_type)

class underlier():
    def __init__(self, ticker):
        self.ticker = ticker

    def ivol(self):
        pass

    def rvol(self, wdw, start_dt, end_dt, connection = None, price_choice = 'px_last',
             source = 'bloomberg', period = 1, asc =False, ann_factor = 252):
        if connection == None:
            print('No Bloomberg connection was initiated!')
        else:
            #Format data
            self.ticker = self.ticker.str.lower()
            if type(self.ticker) is not list:
                self.ticker = list(self.ticker)

            #Use 3 calendar lag to address for week ends
            data_start_dt = (start_dt - dt.timedelta(math.ceil(wdw * 365/252) + 3)).strftime('%Y%m%d')
            data_end_dt = end_dt.strftime('%Y%m%d')
            #Push Market Data
            price = connection.bdh(self.ticker, price_choice, data_start_dt, data_end_dt,
                                   elms = [('adjustmentAbnormal', True), ('adjustmentNormal', True),
                                           ('adjustmentSplit', True)])[self.ticker]
            log_ret = np.log(price.shift(1) / price) ** 2
            rv = (log_ret.rolling(wdw).sum() * ann_factor / wdw) ** (1/2) * 100
            rv = rv.loc[start_dt:end_dt]
            rv = rv.xs(field, axis = 1, level = 1)

        if not asc:
            rv = rv[::-1]

        return rv


class equity(underlier):

    def __init(self, ticker):
        underlier.__init__(self,ticker)

    def ivol(self,tenor, vol_type, strike, start_dt=None, end_dt=None, dts=None,
             connection=None, p_or_c="p", price_choice="px_last", source="bvol", asc=False):
        '''
            Get implied volatility time series for specific strike or instrument and tenor
            by returning a pandas Dataframe with columns as Tickers and index as dates for:

            Parameters
            ----------
            ticker: {list, string}
                String or list of strings corresponding to tickers
            tenor: integer
                Integer corresponding to tenor in business days
            vol_type: string
                String corresponding to surface strike reference (delta, atm...) or
                instrument related (varswap...)
            strike: integer
                Integer referring to strike point for surface strike reference vol type
            start_dt: string
                String in format yyyymmdd for time series starting date
            end_dt: string
                String in format yyyymmdd for time series ending date
            dts: list
                List of strings representing dates in strings with yyyymmdd format
            p_or_c: string
                String corresponding to option type put or call
            price_choice: string
                String corresponding to price choice bid, mid or ask
            source: string
                String corresponding to volatility data provider
            asc: boolean
                Boolean corresponding to the sorting of the time series timestamp in ascending order

            Output
            ------
            Percentage implied vol time series

            Features
            --------
            Tenor: discrete data if available otherwise interpolating linearly variances
                    Live (Mid):'1m','2m','3m','6m','1y','18m','2y'
                    Live(Bid/Offer): '1m','2m','3m','6m','9m','1y','18m','2y','3y','4y','5y','7y','10y'
                    Bvol:'1w','2w','3w','1m','2m','3m','6m','9m','1y','18m','2y','3y',
                         '4y','5y','6y','7y','8y','9y','10y','15y','20y','25y','30y'
            Strike: available data points of source only (no interpolation)
                    live (Bid/Offer): delta: 50, 40, 35, 30, 25, 20, 15, 13, 10, 7, 5
                    live (Mid): 10, 25, 40, 50
                    Bvol: 5, 10, 15, 25, 35, 50
            Start_dt: Not available for Live Bid/Offer
            End_dt: Not available for Live Bid/Offer
            Dts: Only for Live Bid/Offer
            P_or_c: can be entered as 'put', 'p', 'call' or 'c'
            Price_choice: accepts px_last = mid, bid, ask, Live only bid/offer
            Source: Bloomberg Bvol and Live available.
                    Live: bid/offer is callable only point by point whereas mid as a time series.
        '''

        if connection == None:
            print('No Bloomberg connection was initiated!')
            return None
        else:
            # Build a tenor map for available data points in accessible sources
            discrete_tenor ={'live':['1m','2m','3m','6m','1y','18m','2y'],
                             'bvol':['1w','2w','3w','1m','2m','3m','6m','9m','1y','18m','2y','3y',
                                     '4y','5y','6y','7y','8y','9y','10y','15y','20y','25y','30y']}

            # Check if tenor is available, if not interpolates
            discrete = tenor in list(tenor_map.loc[discrete_tenor[source.lower()]]['bdays'])
            if discrete:
                # convert bdays tenor to string discrete tenor
                tenor = tenor_map.index[tenor_map['bdays'] == tenor][0]
                iv = self.ivol_discrete(tenor, vol_type, strike, start_dt=start_dt,end_dt=end_dt,dts=dts,
                                        connection=connection,p_or_c=p_or_c, source=source, price_choice=price_choice,
                                        asc=asc)
            else:
                tenor_bounds = tenor_map.index[tenor_map['bdays'].loc[(tenor_map['bdays'] - tenor)<0].argmax()+[0,1]]
                # Get iv for surrounding discrete tenors
                iv = list(map(lambda x: self.ivol_discrete(x, vol_type, strike, start_dt=start_dt, end_dt=end_dt,
                                                           connection=connection, p_or_c=p_or_c, source=source,
                                                           price_choice=price_choice, asc=asc),
                             tenor_bounds))
                # Interpolate for target tenor if not point not available
                iv = {tick: pd.concat([df[tick] for df in iv], axis=1) for tick in self.ticker}
                iv = pd.concat({tick: iv_tick.pow(2).apply(lambda x: np.interp(tenor,
                                                                      list(tenor_map.loc[tenor_bounds, 'bdays']),
                                                                      list(x)) ** 0.5, axis=1)
                                for tick,iv_tick in iv.items()},axis =1)


        return iv

    def ivol_discrete(self, tenor, vol_type, strike, start_dt=None, end_dt=None, dts=None, connection=None,
                      p_or_c="p",
                      price_choice="px_last", source="bvol", asc=False):
        '''
            Returns implied volatility time series for data points discretely available
            Input: underlying ticker vector and surface point passed parameter
            Output: percentage implied vol time series

            Features
            --------
            Ticker: must enter Bloomberg "Equity" or "Index" complement, naked only with database format
        '''

        if connection == None:
            print('No Bloomberg connection was initiated!')
            return (None)
        else:
            #Format Ticker List#########################################################################################
            if type(self.ticker) is list:
                self.ticker = [x.lower() for x in self.ticker]
            else:
                self.ticker = [self.ticker.lower()]

            #Format Dates###############################################################################################
            if type(start_dt) is dt.date:
                start_dt = start_dt.strftime("%Y%m%d")
            if type(end_dt) is dt.date:
                end_dt = end_dt.strftime("%Y%m%d")

            if source.lower() == "bvol":
                # Ticker construct##########################################################################################
                strike = str(strike)
                if vol_type.lower() == "delta":
                    strike = str(strike) + vol_type[0] + p_or_c.lower()[0]
                elif vol_type.lower() == 'atm':
                    strike = '100'
                elif vol_type.lower() != "pct" or vol_type.lower() != "moneyness":
                    print(f'Volatility Type "{vol_type}" is not supported!')
                    return None

                ticker_bvol = [" ".join([tick.replace(" equity" if tick.find("eq") > 0 else " index", ''),
                                         tenor, strike, "vol bvol",
                                         "equity" if tick.find("eq") > 0 else "index"]) for tick in self.ticker]

                #Push Market Data###########################################################################################
                iv = connection.bdh(ticker_bvol, price_choice, start_dt, end_dt)[ticker_bvol]
                iv = iv.xs(price_choice, axis=1, level=1)
                iv.rename(columns=dict(zip(iv.columns, self.ticker)), inplace = True)

            elif source.lower() == "live":
                if price_choice.lower() == "mid" or price_choice.lower() == "px_last":
                    #Format Bloomberg call##################################################################################
                    tenor_map ={'1m':30, '2m':60, '3m':90, '6m':180, '1y':360, '18m':540, '2y':720}
                    bbg_overds =[('ivol_delta_put_or_call', 'ivol_' + ('put' if p_or_c == 'p' else 'call')),
                                 ('ivol_maturity', 'maturity' + str(tenor_map[tenor]) + 'd'),
                                 ('ivol_delta_level', 'delta_lvl' + str(strike))]

                    #Push Market Data#######################################################################################
                    iv = connection.bdh(self.ticker, 'ivol_delta', start_dt, end_dt, ovrds = bbg_overds).xs('ivol_delta',
                          axis =1, level = 1)

                else:
                    if type(dts) != list:
                        print('Dates needs to be entered as a list')
                        return None
                    # Format Bloomberg call######################################################################################
                    tenor_map = {"1m": 1, "2m": 2, "3m": 3, "6m": 6, "9m": 9, "ly": 12, "18m": 18, "2y": 24, "3y": 36,
                                 "4y": 48, "5y": 60, "7y": 84, "10y": 120}
                    bbg_ovrds = [("ivol_surface_axis_type", "Tenor/De1ta"), ("ivol_surface_source", "LIVE"),
                                 ("ivol_price_choice", price_choice),
                                 ("ivol_strike_range", str(strike * 0.01) + " /0.01/" + str(strike * 0.01)),
                                 ("ivol_time_range", str(tenor_map[tenor]) + str(tenor_map[tenor]))]

                    # Push Market Data###########################################################################################
                    iv = connection.bulkref_hist(self.ticker, "ivol_surface", dates=dts, ovrds=bbg_ovrds).dropna(
                        subset=['value'])

                    # Clean Data#################################################################################################
                    # Filter option type
                    iv = iv.loc[iv['position'] == (0 if p_or_c[0].lower() == 'p' else 1), ::]
                    # Extract iv
                    iv = iv[['date', 'ticker', 'value']].loc[iv['name'] == 'Implied Volatility']
                    # Format Output dataframe
                    iv['date'] = pd.to_datetime(iv['date'].astype(str), format='%Y%m%d')
                    iv = iv.set_index('date')
                    iv = iv.groupby('date').apply(lambda x: x.set_index('ticker').T).droplevel(1)
            else:
                print('Requested data source is not available!')
                return None

        if not asc:
            iv = iv[::-1]

        return iv

class fx(underlier):

    def __init(self, ticker):
        underlier.__init__(self,ticker)

    def ivol(self,tenor, vol_type, strike, start_dt=None, end_dt=None, dts=None,
             connection=None, p_or_c="p", price_choice="px_last", source="bvol", asc=False):
        '''
            Get implied volatility time series for specific strike or instrument and tenor
            by returning a pandas Dataframe with columns as Tickers and index as dates for:

            Parameters
            ----------
            ticker: {list, string}
                String or list of strings corresponding to tickers
            tenor: integer
                Integer corresponding to tenor in business days
            vol_type: string
                String corresponding to surface strike reference (delta, atm...) or
                instrument related (varswap...)
            strike: integer
                Integer referring to strike point for surface strike reference vol type
            start_dt: string
                String in format yyyymmdd for time series starting date
            end_dt: string
                String in format yyyymmdd for time series ending date
            dts: list
                List of strings representing dates in strings with yyyymmdd format
            p_or_c: string
                String corresponding to option type put or call
            price_choice: string
                String corresponding to price choice bid, mid or ask
            source: string
                String corresponding to volatility data provider
            asc: boolean
                Boolean corresponding to the sorting of the time series timestamp in ascending order

            Output
            ------
            Percentage implied vol time series

            Features
            --------
            Tenor: discrete data if available otherwise interpolating linearly variances
                    Bgn (Mid):'1w', '2w', '3w','1m','2m','3m', '4m', '6m','9m','1y','2y','3y','5y',
                              '7y', '10y','15y','30y'
                    Bvol:'1d','1w','2w','3w','1m','2m','3m','6m','9m','1y','18m','2y','3y',
                         '4y','5y','7y','10y'
            Strike: available data points of source only (no interpolation)
                    Bgn: delta:  35, 25, 15, 10, 5
                    Bvol: 5, 10, 15, 25, 35, 50
            Start_dt: Not available for Live Bid/Offer
            End_dt: Not available for Live Bid/Offer
            Dts: Only for Live Bid/Offer
            P_or_c: can be entered as 'put', 'p', 'call' or 'c'
            Price_choice: accepts px_last = mid, bid, ask.
            Source: Bloomberg Bvol and Bgn available.

        '''

        if connection == None:
            print('No Bloomberg connection was initiated!')
            return None
        else:
            # Build a tenor map for available data points in accessible sources
            discrete_tenor ={'bgn':['1w','2w','3w','1m','2m','3m','4m','6m','9m','1y', '2y','3y',
                                    '5y','7y','10y','15y','30y'],
                             'bvol':['1d','1w','2w','3w','1m','2m','3m','6m','9m','1y','18m','2y','3y',
                                     '4y','5y','7y','10y']}

            # Check if tenor is available, if not interpolates
            discrete = tenor in list(tenor_map.loc[discrete_tenor[source.lower()]]['bdays'])
            if discrete:
                # convert bdays tenor to string discrete tenor
                tenor = tenor_map.index[tenor_map['bdays'] == tenor][0]
                iv = self.ivol_discrete(tenor, vol_type, strike, start_dt=start_dt,end_dt=end_dt,
                                        connection=connection,p_or_c=p_or_c, source=source, price_choice=price_choice,
                                        asc=asc)
            else:
                tenor_bounds = tenor_map.index[tenor_map['bdays'].loc[(tenor_map['bdays'] - tenor)<0].argmax()+[0,1]]
                # Get iv for surrounding discrete tenors
                iv = list(map(lambda x: self.ivol_discrete(x, vol_type, strike, start_dt=start_dt, end_dt=end_dt,
                                                           connection=connection, p_or_c=p_or_c, source=source,
                                                           price_choice=price_choice, asc=asc),
                             tenor_bounds))
                # Interpolate for target tenor if  point unavailable
                iv = {tick: pd.concat([df[tick] for df in iv], axis=1) for tick in self.ticker}
                iv = pd.concat({tick: iv_tick.pow(2).apply(lambda x: np.interp(tenor,
                                                                      list(tenor_map.loc[tenor_bounds, 'bdays']),
                                                                      list(x) )** 0.5, axis=1)
                                for tick, iv_tick in iv.items()},
                               axis =1)


        return iv

    def ivol_discrete(self, tenor, vol_type, strike, start_dt=None, end_dt=None, dts=None, connection=None,
                      p_or_c="p", price_choice="px_last", source="bvol", asc=False):
        '''
            Returns implied volatility time series for data points discretely available in the data source
            Input: underlying ticker vector and surface point passed parameter

            Parameters:
            ----------
            ticker: {list,string}
                String or list of strings corresponding to tickers with or without their asset class ("Eurusd"
                or "Eurusd curncy")
            tenor: string
                String corresponding to tenor in vol expiry convention ('1m', '3m',...)
            vol_type: string
                String corresponding to surface strike reference (delta, atm...) or instrument related
                transformation (varswap...)
            strike: integer
                Integer referring to strike point for surface strike reference vol type (delta or moneyness)
            start_dt:string
                String in format yyyymmdd for time series starting date
            end_dt:string
                String in format yyyymmdd for time series ending date
            p_or_c: string
                String corresponding to option type put or call
            price_choice:
                String corresponding to price choice bid, ask or mid
            source: string
                String corresponding to the volatility data provider
            asc: boolean
                Boolean corresponding to the sorting of the time series timestamp in ascending order

            Features
            --------
            Tenor: discrete data if available otherwise interpolating linearly variances
                    Bgn (Mid):'1w', '2w', '3w','1m','2m','3m', '4m', '6m','9m','1y','2y','3y','5y',
                              '7y', '10y','15y','30y'
                    Bvol:'1d','1w','2w','3w','1m','2m','3m','6m','9m','1y','18m','2y','3y','4y','5y','7y','10y'
            Vol_type: atm and delta available
            Strike: available data points of source only (no interpolation)
                    Bgn: delta:  35, 25, 15, 10, 5
                    Bvol: 50, 45, 40, 35, 30,25, 20, 15,10,5
            P_or_c: can be entered as 'put', 'p', 'call' or 'c'
            Price_choice: accepts px_last = mid, bid, ask.
            Source: Bloomberg Bvol and Bgn available.

            Output:
            ------
            percentage implied vol time series
        '''

        if connection == None:
            print('No Bloomberg connection was initiated!')
            return (None)
        else:
            #Format Ticker List#########################################################################################
            if type(self.ticker) is list:
                self.ticker = [x.lower() for x in self.ticker]
            else:
                self.ticker = [self.ticker.lower()]

            #Format Dates###############################################################################################
            if type(start_dt) is dt.date:
                start_dt = start_dt.strftime("%Y%m%d")
            if type(end_dt) is dt.date:
                end_dt = end_dt.strftime("%Y%m%d")

            if source.lower() == "bvol":
                # Ticker construct######################################################################################
                strike = str(strike)
                if vol_type.lower() == "delta":
                    strike = str(strike) + vol_type[0] + p_or_c.lower()[0]
                elif vol_type.lower() == 'atm':
                    strike = '100'
                elif vol_type.lower() != "pct" or vol_type.lower() != "moneyness":
                    print(f'Volatility Type "{vol_type}" is not supported!')
                    return None

                ticker_bvol = [" ".join([tick.replace(" curncy" if tick.find("cur") > 0 else tick, ''),
                                         tenor, strike, "vol bvol", "Curncy"]).lower() for tick in self.ticker]

                #Push Market Data#######################################################################################
                iv = connection.bdh(ticker_bvol, price_choice, start_dt, end_dt)[ticker_bvol]
                iv = iv.xs(price_choice, axis=1, level=1)
                iv.rename(columns=dict(zip(iv.columns, self.ticker)), inplace = True)

            elif source.lower() == "bgn":
                #Ticker construction####################################################################################
                strike = str(strike)
                vol_strats = ['v','r','b']
                ticker_strats = {type: [(tick.replace(' curncy', '') if tick.find('cur') > 0 else tick)
                                        + ('' if type == 'v' else strike) + type + tenor + ' curncy' for tick in self.ticker]
                                 for type in vol_strats}
                if vol_type.lower() == 'delta':
                    #Delta vols are calculated through risk reversal (r), butterfly (b) and atm vols
                    iv = {i: connection.bdh(j, price_choice, start_dt, end_dt)[j].xs(price_choice, axis=1, level=1)
                          for i,j in ticker_strats.items()}
                    iv = {i: j.rename(columns = dict(zip(j.columns, self.ticker))) for i,j in iv.items()}
                    iv = iv['b'] + iv['v'] + (-1 if p_or_c[0] == 'p' else 1) * iv['r']/2
                elif vol_type.lower() == 'atm':
                    #Push Market Data###################################################################################
                    iv = connection.bdh(ticker_strats['v'], price_choice, start_dt, end_dt)[ticker_strats['v']].xs(
                        price_choice, axis = 1, level = 1)
                    iv.rename(columns = dict(zip(iv.columns, self.ticker)), inplace = True)
                elif vol_type.lower() != 'pct' or vol_type.lower() != 'moneyness':
                    print("Volatility Type " + vol_type + "is not supported!")
                    return None
            else:
                print('Requested data source is not available!')
                return None

        if not asc:
            iv = iv[::-1]

        return iv



