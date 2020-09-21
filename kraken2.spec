/*
A KBase module: kraken2
*/

module kraken2 {
    typedef structure {
        string report_name;
        string report_ref;
    } ReportResults;

    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */
    funcdef run_kraken2(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;
    funcdef exec_kraken2(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;

};
