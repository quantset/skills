let
    // QuantSet Excel Power Query (M) Loader
    // Works immediately with "mw_demo" on sample tickers (us:NVDA, us:AAPL, us:MSFT, us:IVV, global:SHEL.L, global:1301.T, global:RELIANCE.NS, crypto:BTCUSDT, index:SPX).
    // Claim 250 free credits (no credit card) at https://quantset.dev/signup to unlock all 90,000+ symbols across 67 countries.
    ApiKey = "mw_demo",
    Endpoint = "api/v1/financial-statements/income",
    QueryParams = [
        tickers = "us:NVDA,us:AAPL",
        period = "annual",
        limit_per_instrument = "5",
        format = "csv"
    ],
    Source = Csv.Document(
        Web.Contents("https://api.quantset.dev", [
            RelativePath = Endpoint,
            Query = QueryParams,
            Headers = [#"X-API-Key" = ApiKey]
        ]),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true])
in
    PromotedHeaders
