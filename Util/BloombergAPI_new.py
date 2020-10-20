
# -*- coding: utf-8 -*-

#https://github.com/691175002/BLPInterface/issues/3
""" A wrapper for the Bloomberg API.

Designed to roughly emulate the Excel API.

All requests return well-formed Series or DataFrames where appropriate and can
handle any number of securities and fields within a single request.

Excel BDH: historicalRequest()
Excel BDP: referenceRequest()
Excel BDS: bulkRequest()

Note: Securities may be fetched by ticker, bbgid or cusip using the following
      formats: "BMO CN Equity", "BBG0000000000", or "/cusip/000000000"

Created July 2015

@author: ryan
"""
import socket
import itertools
from datetime import datetime, date, time

import pandas as pd
import numpy as np
from pandas import Series
from pandas import DataFrame

# Default Connections
BLP_HOST = 'localhost'
BLP_PORT = 8194
PROXY_HOST = ''
PROXY_PORT = 5001


class RequestError(Exception):
    """A RequestError is raised when there is a problem with a Bloomberg API response."""

    def __init__(self, description, value=None):
        self.value = value
        self.description = description

    def __str__(self):
        if self.value is not None:
            return self.description + '\n' + self.value
        return self.description


def _uwrap(s):
    """Helper function to convert a string or list into a list of unique entries."""
    s = [s] if isinstance(s, str) else s
    return list(set(s))


def _convertDate(d):
    """Helper function to convert dates and datetimes into blpapi strings."""
    if isinstance(d, np.datetime64):
        d = pd.Timestamp(d)
    elif isinstance(d, pd.Period):
        d = d.to_timestamp(freq='D')

    if isinstance(d, date):
        if isinstance(d, datetime) and (d.time() != time(0)):
            return d.strftime('%Y-%m-%dT%H:%M:%S')
        else:
            return d.strftime('%Y%m%d')
    return d


# Attempt to import the Bloomberg API.  Technically this is a bad idea as it
# can mask unrelated ImportErrors but whatever.
try:
    # noinspection PyUnresolvedReferences
    import blpapi

    # The Bloomberg API was successfully imported - Create the normal
    # BLPInterface class.

    DEFAULT_HOST = BLP_HOST
    DEFAULT_PORT = BLP_PORT


    class BLPInterface:
        """ A wrapper for the Bloomberg API that returns DataFrames.  This class
            manages a //BLP/refdata service and therefore does not handle event
            subscriptions.

            All calls are blocking and responses are parsed and returned as
            DataFrames where appropriate.

            A RequestError is raised when an invalid security is queried.  Invalid
            fields will fail silently and may result in an empty DataFrame.
        """

        # noinspection PyShadowingBuiltins
        def __init__(self, host=BLP_HOST, port=BLP_PORT, open=True):
            self.active = False
            self.host = host
            self.port = port
            self.session = None
            self.refDataService = None
            if open:
                self.open()

        def open(self):
            if not self.active:
                sessionOptions = blpapi.SessionOptions()
                sessionOptions.setServerHost(self.host)
                sessionOptions.setServerPort(self.port)
                sessionOptions.setAutoRestartOnDisconnection(True)

                self.session = blpapi.Session(sessionOptions)
                if (not self.session.start()) or (not self.session.openService("//blp/refdata")):
                    raise RequestError('Failed to start session')

                self.refDataService = self.session.getService('//BLP/refdata')
                self.active = True

        def close(self):
            if self.active:
                self.session.stop()
                self.active = False

        def historicalRequest(self, securities, fields, startDate, endDate='', overrides=None, **kwargs):
            """ Equivalent to the Excel BDH Function.

                If securities are provided as a list, the returned DataFrame will
                have a MultiIndex.

                StartDate and endDate should be a datetime.date or YYYYMMDD string.
                Datetimes or Timestamps with a non-zero time component will not be
                recognized correctly by the Bloomberg API.

                Useful kwargs are periodicitySelection, adjustmentNormal,
                adjustmentAbnormal, adjustmentSplit, and currency.
            """
            defaults = {'startDate': startDate.replace('-', '') if isinstance(startDate, str) else startDate,
                        'endDate': endDate.replace('-', '') if isinstance(endDate, str) else endDate,
                        'periodicityAdjustment': 'CALENDAR',
                        'periodicitySelection': 'DAILY',
                        'nonTradingDayFillOption': 'NON_TRADING_WEEKDAYS',
                        'adjustmentNormal': False,
                        'adjustmentAbnormal': False,
                        'adjustmentSplit': True,
                        'adjustmentFollowDPDF': False}


            defaults.update(kwargs)
            usecurities = _uwrap(securities)
            ufields = _uwrap(fields)
            response = self.sendRequest('HistoricalData', usecurities, ufields, overrides, defaults)

            data = []
            keys = []

            for msg in response:
                securityData = msg.getElement('securityData')
                fieldData = securityData.getElement('fieldData')
                fieldDataList = [fieldData.getValueAsElement(i) for i in range(fieldData.numValues())]

                df = DataFrame(columns=ufields)

                for fld in fieldDataList:
                    for v in [fld.getElement(i) for i in range(fld.numElements())
                              if fld.getElement(i).name() != 'date']:
                        df.loc[fld.getElementAsDatetime('date'), str(v.name())] = v.getValue()

                df.index = pd.to_datetime(df.index)
                df.replace('#N/A History', np.nan, inplace=True)

                keys.append(securityData.getElementAsString('security'))
                data.append(df)

            if len(data) == 0:
                return DataFrame()
            else:
                data = pd.concat(data, keys=keys, axis=1, names=['Security', 'Field']).sort_index()
                data.index.name = 'Date'

            if isinstance(securities, str) and isinstance(fields, str):
                data = data.iloc[:, 0]
                data.name = fields
            elif isinstance(securities, str):
                data.columns = data.columns.droplevel('Security')
                data = data[fields]
            elif isinstance(fields, str):
                data.columns = data.columns.droplevel('Field')
                data = data[securities]
            else:
                data = data[list(itertools.product(securities, fields))]
            return data

        def referenceRequest(self, securities, fields, overrides=None, **kwargs):
            """ Equivalent to the Excel BDP Function.

                If either securities or fields are provided as lists, a DataFrame
                will be returned.
            """
            usecurities = _uwrap(securities)
            ufields = _uwrap(fields)
            response = self.sendRequest('ReferenceData', usecurities, ufields, overrides, kwargs)
            data = DataFrame(index=usecurities, columns=ufields)

            for msg in response:
                securityData = msg.getElement('securityData')
                securityDataList = [securityData.getValueAsElement(i) for i in range(securityData.numValues())]

                for sec in securityDataList:
                    fieldData = sec.getElement('fieldData')
                    fieldDataList = [fieldData.getElement(i) for i in range(fieldData.numElements())]

                    for fld in fieldDataList:
                        # data.ix[sec.getElementAsString('security'), str(fld.name())] = fld.getValue()
                        data.loc[sec.getElementAsString('security'), str(fld.name())] = fld.getValue()

            if data.empty:
                return DataFrame()
            else:
                data.index.name = 'Security'
                data.columns.name = 'Field'

            if isinstance(securities, str) and isinstance(fields, str):
                data = data.iloc[0, 0]
            elif isinstance(securities, str):
                data = data.iloc[0, :][fields]
            elif isinstance(fields, str):
                data = data.iloc[:, 0][securities]
            else:
                data = data.loc[securities, fields]
            return data

        def bulkRequest(self, securities, fields, overrides=None, **kwargs):
            """ Equivalent to the Excel BDS Function.

                If securities are provided as a list, the returned DataFrame will
                have a MultiIndex.

                You may also pass a list of fields to a bulkRequest.  An appropriate
                MultiIndex will be generated, however such a DataFrame is unlikely
                to be useful unless the bulk data fields contain overlapping columns.
            """
            response = self.sendRequest('ReferenceData', securities, fields, overrides, kwargs)

            data = []
            keys = []

            for msg in response:
                securityData = msg.getElement('securityData')
                securityDataList = [securityData.getValueAsElement(i) for i in range(securityData.numValues())]

                for sec in securityDataList:
                    fieldData = sec.getElement('fieldData')
                    fieldDataList = [fieldData.getElement(i) for i in range(fieldData.numElements())]

                    fldData = []
                    fldKeys = []

                    for fld in fieldDataList:
                        df = DataFrame()
                        for v in [fld.getValueAsElement(i) for i in range(fld.numValues())]:
                            s = Series()
                            for d in [v.getElement(i) for i in range(v.numElements())]:
                                try:
                                    s[str(d.name())] = d.getValue()
                                except:
                                    # There is seriously no end to the shit getValue() can raise.
                                    pass
                            # Bloomberg returns this magic number instead of NaN for certain bulk fields.
                            df = df.append(s.where(s != -2.4245362661989844e-14, np.nan), ignore_index=True)

                        try:
                            df = df.set_index(df.columns[0])
                            if not df.empty:
                                fldKeys.append(str(fld.name()))
                                fldData.append(df)
                        except IndexError:
                            pass

                    if fldData:
                        keys.append(sec.getElementAsString('security'))
                        data.append(pd.concat(fldData, keys=fldKeys, names=['Field']))

            if data:
                data = pd.concat(data, keys=keys, names=['Security'])
                data.columns.name = 'Element'
            else:
                return DataFrame()

            if isinstance(securities, str) and isinstance(fields, str):
                data = data.reset_index(['Security', 'Field'], drop=True)
            elif isinstance(securities, str):
                data = data.reset_index('Security', drop=True)
            elif isinstance(fields, str):
                data = data.reset_index('Field', drop=True)
            return data

        def portfolioDataRequest(self, securities, fields, overrides=None, **kwargs):
            response = self.sendRequest('PortfolioData', securities, fields, overrides, kwargs)
            # TODO: Read exactly like bulkrequest
            return response

        def intradayBarRequest(self, security, startDate, endDate, **kwargs):
            """ Performs an IntradayBarRequest.

                IntradayBarRequests can only include a single security and will
                return a predefined set of fields.  The granularity of this
                request can be set via the interval parameter in minutes.

                To receive data, startDate and endDate must include a UTC time.
            """
            defaults = {'startDateTime': startDate,
                        'endDateTime': endDate,
                        'eventType': 'TRADE',
                        'interval': 5,
                        'adjustmentNormal': False,
                        'adjustmentAbnormal': False,
                        'adjustmentSplit': True,
                        'adjustmentFollowDPDF': False}
            defaults.update(kwargs)

            response = self.sendRequest('IntradayBar', security, [], None, defaults)

            data = DataFrame()
            for msg in response:
                tickData = msg.getElement('barData').getElement('barTickData')
                tickDataList = [tickData.getValueAsElement(i) for i in range(tickData.numValues())]

                for tick in tickDataList:
                    dt = tick.getElementAsDatetime('time').replace(tzinfo=None)
                    for v in [tick.getElement(i) for i in range(1, tick.numElements())]:
                        # Get every value as a string and cast to the apropriate type later
                        # This is pretty dirty but network latency dominates the runtime of this function
                        data.ix[dt, str(v.name())] = v.getValueAsString()

            data.index.name = 'Date'
            return data.apply(pd.to_numeric, errors='coerce').sort_index()

        def intradayTickRequest(self, security, startDate, endDate, **kwargs):
            """ Performs an IntradayTickRequest.

                IntradayTickRequests can only include a single security and will
                return a predefined set of fields.

                To receive data, startDate and endDate must include a UTC time.
            """
            defaults = {'startDateTime': startDate,
                        'endDateTime': endDate,
                        'eventTypes': ['TRADE']}
            defaults.update(kwargs)

            response = self.sendRequest('IntradayTick', security, [], None, defaults)

            data = DataFrame()
            for msg in response:
                tickData = msg.getElement('tickData').getElement('tickData')
                tickDataList = [tickData.getValueAsElement(i) for i in range(tickData.numValues())]

                for tick in tickDataList:
                    dt = tick.getElementAsDatetime('time').replace(tzinfo=None)
                    for v in [tick.getElement(i) for i in range(1, tick.numElements())]:
                        data.ix[dt, str(v.name())] = v.getValueAsString()

            data.index.name = 'Date'
            return data.apply(pd.to_numeric, errors='coerce').sort_index()

        def sendRequest(self, requestType, securities, fields, overrides, elements):
            """ Prepares and sends a request then blocks until it can return
                the complete response.

                Depending on the complexity of your request, incomplete and/or
                unrelated messages may be returned as part of the response.
            """
            request = self.refDataService.createRequest(requestType + 'Request')

            if isinstance(securities, str):
                securities = [securities]
            if isinstance(fields, str):
                fields = [fields]

            for s in securities:
                try:
                    request.getElement("securities").appendValue(s)
                except:
                    request.set('security', s)

            for f in fields:
                request.getElement("fields").appendValue(f)

            for k, v in elements.items():
                if isinstance(v, list):
                    for i in v:
                        request.getElement(k).appendValue(_convertDate(i))
                else:
                    request.set(k, _convertDate(v))

            if overrides is not None:
                for k, v in overrides.items():
                    ovr = request.getElement('overrides').appendElement()
                    ovr.setElement("fieldId", str(k))
                    ovr.setElement('value', str(_convertDate(v)))

            self.session.sendRequest(request)

            response = []
            while True:
                event = self.session.nextEvent(100)
                for msg in event:
                    if msg.hasElement('responseError'):
                        raise RequestError('Response Error', str(msg.getElement('responseError')))
                    if msg.hasElement('securityData'):
                        if msg.getElement('securityData').hasElement('fieldExceptions') and \
                                (msg.getElement('securityData').getElement('fieldExceptions').numValues() > 0):
                            raise RequestError('Field Error',
                                               str(msg.getElement('securityData').getElement('fieldExceptions')))
                        if msg.getElement('securityData').hasElement('securityError'):
                            raise RequestError('Security Error',
                                               str(msg.getElement('securityData').getElement('securityError')))

                    if msg.messageType() == requestType + 'Response':
                        response.append(msg)

                if event.eventType() == blpapi.Event.RESPONSE:
                    break

            return response

        def __enter__(self):
            self.open()
            return self

        # noinspection PyUnusedLocal
        def __exit__(self, exc_type, exc_val, exc_tb):
            self.close()

        def __del__(self):
            self.close()

except ImportError:
    # The Bloomberg API was not found - Implement a Proxy BLPInterface
    # instead.
    from rqm.source import net

    DEFAULT_HOST = PROXY_HOST
    DEFAULT_PORT = PROXY_PORT


    class BLPInterface:
        """ A wrapper for the Bloomberg API that returns DataFrames.  This is
            the Proxy version of the BLPInterface and was created as the
            current environment does not have Bloomberg access.

            All requests will be forwarded to (host, port).  Run BLPServer.py
            on a computer to fulfil requests.

            All calls are blocking and responses are parsed and returned as
            DataFrames where appropriate.
        """

        # noinspection PyShadowingBuiltins
        def __init__(self, host=PROXY_HOST, port=PROXY_PORT, open=True):
            self.active = False
            self.host = host
            self.port = port
            self.socket = None
            if open:
                self.open()

        def open(self):
            if not self.active:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(60)
                self.socket.connect((self.host, self.port))
                self.active = True

        def historicalRequest(self, securities, fields, startDate, endDate='', overrides=None, **kwargs):
            kwargs['securities'] = securities
            kwargs['fields'] = fields
            kwargs['startDate'] = startDate
            kwargs['endDate'] = endDate
            kwargs['overrides'] = overrides
            return self.sendRequest('historicalRequest', kwargs)

        def referenceRequest(self, securities, fields, overrides=None, **kwargs):
            kwargs['securities'] = securities
            kwargs['fields'] = fields
            kwargs['overrides'] = overrides
            return self.sendRequest('referenceRequest', kwargs)

        def bulkRequest(self, securities, fields, overrides=None, **kwargs):
            kwargs['securities'] = securities
            kwargs['fields'] = fields
            kwargs['overrides'] = overrides
            return self.sendRequest('bulkRequest', kwargs)

        def intradayBarRequest(self, security, startDate, endDate, **kwargs):
            kwargs['security'] = security
            kwargs['startDate'] = startDate
            kwargs['endDate'] = endDate
            return self.sendRequest('intradayBarRequest', kwargs)

        def intradayTickRequest(self, security, startDate, endDate, **kwargs):
            kwargs['security'] = security
            kwargs['startDate'] = startDate
            kwargs['endDate'] = endDate
            return self.sendRequest('intradayTickRequest', kwargs)

        # noinspection PyTypeChecker
        def sendRequest(self, requestType, arguments):
            net.sendObject(self.socket, [requestType, arguments])
            return net.receiveObject(self.socket)

        def close(self):
            if self.active:
                self.socket.close()
                self.active = False

        def __enter__(self):
            self.open()
            return self

        # noinspection PyUnusedLocal
        def __exit__(self, exc_type, exc_val, exc_tb):
            self.close()

        def __del__(self):
            self.close()


def main():
    """ Basic usage examples.

        Note that if any tickers have changed since these examples were written
        a RequestError will be raised.
    """
    try:
        blp = BLPInterface()

        # ==============================
        # = HistoricalRequest Examples =
        # ==============================
        # Requesting a single security and field returns a simple Series.
        print(blp.historicalRequest('BMO CN Equity', 'PX_LAST', '20141231', '20150131'))

        # Requesting multiple fields returns a DataFrame.  Dates may also be passed as a datetime.
        print(blp.historicalRequest('BNS CN Equity', ['PX_LAST', 'PX_VOLUME'],
                                    datetime(2014, 12, 31), datetime(2015, 1, 31)))

        # Requesting multiple securities and fields returns a DataFrame with a MultiIndex.
        print(blp.historicalRequest(['CM CN Equity', 'NA CN Equity'], ['PX_LAST', 'PX_VOLUME'],
                                    '20141231', '20150131'))

        # You may force the returned data to be of a specific format by passing arguments as lists.
        print(blp.historicalRequest(['NA CN Equity'], ['PX_LAST'], '20141231', '20150131'))

        # Keyword arguments are added to the request, allowing you to perform advanced queries.
        print(blp.historicalRequest('TD CN Equity', 'PCT_CHG_INSIDER_HOLDINGS', '20141231', '20150131',
                                    periodicitySelection='WEEKLY'))

        blp.close()

        # The BLPInterface Class can also be used as a ContextManager.
        with BLPInterface() as blp:
            # =============================
            # = ReferenceRequest Examples =
            # =============================
            # Requesting a single security/field will return the single value, not a DataFrame.
            print(blp.referenceRequest('BBD/B CN Equity', 'GICS_SECTOR'))

            # Requesting multiple securities or fields will return a Series or DataFrame.
            print(blp.referenceRequest(['CNR CN Equity', 'CP CN Equity'], ['SECURITY_NAME_REALTIME', 'LAST_PRICE']))

            # You may force any request to return a DataFrame by passing the arguments as lists.
            print(blp.referenceRequest(['MDA CN Equity'], ['NAME_RT']))

            # Passing overrides in a dictionary is also supported
            print(blp.referenceRequest('TCK/B CN Equity', 'BICS_REVENUE_%_LEVEL_ASSIGNED',
                                       overrides={'EQY_FUNDS_SEGMENT_NUMBER': 1}))

            print(blp.referenceRequest(['IBM US Equity', 'MSFT US Equity'], ['PX_LAST', 'DS002', 'EQY_WEIGHTED_AVG_PX'],
                                       overrides={'VWAP_START_TIME': '9:30',
                                                  'VWAP_END_TIME': '11:30'}))
            # ========================
            # = BulkRequest Examples =
            # ========================
            # Requesting a single security and field will return a DataFrame.
            print(blp.bulkRequest('CIG CN Equity', 'EQY_DVD_ADJUST_FACT'))

            # You may request multiple securities and/or fields to receive a MultiIndex
            # print (blp.bulkRequest(['CP CN Equity','CNR CN Equity'],'PG_REVENUE'))
            # print (blp.bulkRequest('CIG CN Equity',['EQY_DVD_ADJUST_FACT','DVD_HIST_ALL']))

            # ========================
            # = Tick Examples ========
            # ========================
            # Tick requests can only contain a single security.
            print(blp.intradayBarRequest('BMO CN Equity', '2015-08-21T6:00:00', '2015-08-21T16:00:00'))
            print(blp.intradayTickRequest('ZCL CN Equity', '2015-08-21T6:00:00', '2015-08-21T16:00:00'))

    except RequestError:
        raise


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Ctrl+C pressed. Stopping...")
