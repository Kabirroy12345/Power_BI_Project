// ============================================================================
// POWER QUERY (M) STAR SCHEMA LOADER — MANUFACTURING OEE PROJECT
// ============================================================================

let
    DataFolder = "c:\\Users\\HP\\Downloads\\Power_BI\\data\\processed\\",
    LoadCsv = (fileName as text) =>
        let
            Source = Csv.Document(File.Contents(DataFolder & fileName), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
            PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
        in
            PromotedHeaders
in
    LoadCsv
