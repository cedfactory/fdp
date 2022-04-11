fdp
=

[![Build](https://github.com/cedfactory/fdp/actions/workflows/deploy.yml/badge.svg)](https://github.com/cedfactory/fdp/actions)
[![codecov](https://codecov.io/gh/cedfactory/fdp/branch/main/graph/badge.svg)](https://codecov.io/gh/cedfactory/fdp)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=cedfactory_fdp&metric=alert_status)](https://sonarcloud.io/dashboard?id=cedfactory_fdp)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=cedfactory_fdp&metric=bugs)](https://sonarcloud.io/dashboard?id=cedfactory_fdp)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=cedfactory_fdp&metric=code_smells)](https://sonarcloud.io/dashboard?id=cedfactory_fdp)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=cedfactory_fdp&metric=ncloc)](https://sonarcloud.io/dashboard?id=cedfactory_fdp)


API
=

## list

- *exchanges* : for crypto may be hitbtc, bitmex, binance, ftx, speratated with ','

example :

```
localhost:5000/list?exchanges=ftx
```

## symbol

- *screener* : should be crypto.
- *exchange* : may be hitbtc, bitmex, binance, ftx.
- *symbols* : symbols separated with ',' and '/' replaced with '_'

example :

```
localhost:5000/symbol?screener=crypto&exchange=ftx&symbols=ETH_EUR
```

## history

- *exchange* : may be hitbtc, bitmex, binance, ftx.
- *symbol* : symbols separated with ',' and '/' replaced with '_'
- *start* : date with format dd_mm_yyyy
- *length* (optional) : 

example :

```
localhost:5000/history?exchange=ftx&symbol=ETH_EUR&start=01_01_2022
```

## recommendations

- *symbols* (optional) : symbols separated with ',' and '/' replaced with '_'
- *screener* : should be crypto
- *exchange* : may be hitbtc, bitmex, binance, ftx.
- *interval* : may be 1m, 5m, 15m, 30m, 1h, 2h, 4h, 1d, 1W, 1M

example :

```
http://localhost:5000/recommendations?symbols=ETHEUR&screener=crypto&exchange=ftx&interval=1h
```

## portfolio

- *exchange* : may be hitbtc, bitmex, binance, ftx (default).
- *recommendations* : may be STRONG_SELL, SELL, NEUTRAL, BUY, STRONG_BUY
- *intervals* : may be 1m, 5m, 15m, 30m, 1h, 2h, 4h, 1d, 1W, 1M

example :

```
localhost:5000/portfolio?recommendations=STRONG_BUY,BUY&intervals=15m,30m,1h,2h,4h
```

