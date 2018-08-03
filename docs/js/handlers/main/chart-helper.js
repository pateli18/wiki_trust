/////////////////////////////////////////////////////////////////
//Chart generator function and helper functions for chart class//
/////////////////////////////////////////////////////////////////

// creates objects for each of the charts in the site
function createCharts() {
    var chartElements = {
        alphaBar: {
            title: "Trust Alpha",
            chosenClass: "bar",
            elements: '<div id="secondary-chart"></div>' +
            '<div class="slider-label">Slide to Filter</div>' +
            '<div id="primary-chart"></div>',
            textData:textData["alphaBar"],
            param: "trust_factor",
            chartGenerator: barChartGenerator
        },
        alphaScatter: {
            title: "Citations vs. Popularity",
            chosenClass: "scatter-point",
            elements: '<div id="primary-chart"></div>',
            textData:textData["alphaScatter"],
            param: null,
            chartGenerator: scatterChartGenerator
        },
        citationBar: {
            title: "Citations in Wikipedia",
            chosenClass: "bar",
            elements: '<div id="secondary-chart"></div>' +
            '<div class="slider-label">Slide to Filter</div>' +
            '<div id="primary-chart"></div>',
            textData:textData["citationBar"],
            param: "link_count",
            chartGenerator: barChartGenerator
        },
        connectionGraph: {
            title: "Citation Connections in Wikipedia",
            chosenClass: "node",
            elements: '<div id="primary-chart"></div>',
            textData: textData["connectedGraph"],
            param: null,
            chartGenerator: connectedGraphGenerator
        }

    };

    // loop through each chart and add to object to dict
    for (var chart in chartElements) {
        var elements = chartElements[chart];
        charts[chart] = new Chart(elements.title, elements.chosenClass, elements.elements, elements.textData, elements.param, elements.chartGenerator);
    }
};

var barChartGenerator = function(chartParam) {
    return {
        primaryChart: new BarChart("primary-chart", domainData, chartParam),
        secondaryChart: new LineChart("secondary-chart", domainData, 50, chartParam)
    };
};

var scatterChartGenerator = function(chartParam) {
    return {
        primaryChart: new ScatterChart("primary-chart", domainData),
        secondaryChart: null
    };
};

var connectedGraphGenerator = function(chartParam) {
    return {
        primaryChart: new ForceVis("primary-chart", connectionsData),
        secondaryChart: null
    };
};

// filters bar chart when area chart is brushed
function filterBarChart() {
    if (d3.event !== null) {
        barDomainFilters = d3.event.selection.map(selectedChart.chartObjects.secondaryChart.xScale.invert, selectedChart.chartObjects.secondaryChart.xScale);
        selectedChart.chartObjects.primaryChart.wrangleData();
    }
};

// resizes chart when user resizes screen
function resizeChart() {
    selectedChart.renderChart();
};