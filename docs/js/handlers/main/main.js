
///////////////////////
// GLOBAL VARIABLES //
/////////////////////

var charts = {}; // dict of all chart objects
var selectedChart; // corresponds to chart displayed on screen

var zoomThreshold = 20; // number of bars to show in bar chart
var barDomainFilters = [0, zoomThreshold]; // window of bars to show, changes on user search

var domainData; // csv data with metrics
var connectionsData; // json data with connections between domains
var textData; // text description data

var baseColor = "black"; // color for area charts

var trustColorDomain; // domain for trust scale
var trustColorScale = d3.scaleLinear() // color scale for trust metric
    .range(['#d73027', '#fee08b', '#1a9850']) // red, yellow, green
    .interpolate(d3.interpolateHcl);

var searchParam = {id:null, label:null}; // stores domain user has searched for

// load datasets and initiate chart build
queue()
    .defer(d3.csv, "data/domain_metrics.csv")
    .defer(d3.json, "data/domain_connections.json")
    .defer(d3.json, "data/writeups.json")
    .await(function(error, domainDataRaw, connectionsDataRaw, textDataRaw){

        // loop through each item in data and convert to numeric
        domainDataRaw.forEach(function(d, i) {
            d.index = i; // create index for each item
            d.trust_factor_ordinal_rank = +d.trust_factor_ordinal_rank
            d.alexa_rank = +d.alexa_rank
            d.alexa_linksincount = +d.alexa_linksincount
            d.news_site = +d.news_site
            d.link_count = +d.link_count
            d.trust_factor = +d.trust_factor
        });
        domainData = domainDataRaw;

        // loop through each node and create index value
        connectionsDataRaw["nodes"].forEach(function(d, i) {
            d.index = i;
        });
        connectionsData = connectionsDataRaw;

        textData = textDataRaw;

        // calculate trust color domain based on min / max of data
        trustColorDomain = d3.max(domainData, function(d) {
            return Math.abs(d.trust_factor);
        });
        trustColorScale.domain([-trustColorDomain, 0, trustColorDomain]);

        // create trust factor legend
        generateLegend();

        // autocomplete for earch bar
        initiateAutoComplete();

        // start on alpha bar button
        createCharts();
        $("#alpha-bar-button").click();
    });

// creates html elements from text
function generateText(textElements) {
    var text = "";
    textElements.forEach(function(d) {
        text += "<p>" + d + "</p>";
    });

    return text;
}

// displays chart when button is clicked
$(".nav-buttons button").click(function() {

    // unhighlight all non-clicked buttons while highlighting clicked button
    d3.selectAll("button").attr("class", "");
    $(this).addClass("clicked");

    // select relevant chart and display it
    selectedChart = charts[this.value]; 
    selectedChart.renderChart();

    initiateAutoComplete();

    // if user has searched for a specific domain, display results
    if (searchParam.id !== null) {
        console.log("reading search param");
        domainData.forEach(function(d, i) {
           if (d.domain === searchParam.label) {
               searchParam.id = d.index;
           }
        });
        initiateSearch(searchParam.id, searchParam.label);
    }
});
