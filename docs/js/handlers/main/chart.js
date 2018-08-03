//////////////////////////////////////////////////////////////////////
// Generic Chart Object with fucntions common across different types// 
//////////////////////////////////////////////////////////////////////

// initiate object
Chart = function(_chartTitle, _chosenClass, _chartElements, _textData, _chartParam, _chartGenerator) {
    this.chartTitle = _chartTitle;
    this.chosenClass = _chosenClass; // type of chart
    this.chartElements = _chartElements; // html elements of chart
    this.textData = _textData; // chart description
    this.chartParam = _chartParam; // parameter for bar chart height
    this.chartGenerator = _chartGenerator; // function that generates chart
};

Chart.prototype.setTitle = function() {
    $(".chart-title").html(this.chartTitle);
};

Chart.prototype.setDescription = function() {
    $("#chart-description").html(generateText(this.textData));
};

Chart.prototype.setContainer = function() {
    $("#chart-container").html(this.chartElements);
};

Chart.prototype.setCharts = function() {
    this.chartObjects = this.chartGenerator(this.chartParam);

    // if there is a secondary chart, add a brush to it
    if (this.chartObjects.secondaryChart !== null) {
        this.chartObjects.secondaryChart.brush.on("brush end", filterBarChart);
    }
};

// alters chart based on user's search
Chart.prototype.searchChart = function(id, domain) {
    var chart = this;

    var barSearch = function(id) {

        // get window to show, with searched domain in the middle
        var minThreshold = Math.max(id - zoomThreshold / 2, 0);
        var maxThreshold = minThreshold + zoomThreshold;
        if (maxThreshold > domainData.length) {
            maxThreshold = domainData.length;
            minThreshold = maxThreshold - zoomThreshold;
        }

        // adjust brush on area slider based on window
        var areaChart = chart.chartObjects.secondaryChart;
        areaChart.brushItem.call(areaChart.brush)
            .call(areaChart.brush.move, [areaChart.xScale(minThreshold), areaChart.xScale(maxThreshold)]);

        // removes handle to resize the brush
        d3.selectAll('.brush>.handle').remove();
        // removes crosshair cursor
        d3.selectAll('.brush>.overlay').remove();
    };

    if (chart.chosenClass === 'bar') {
        barSearch(id);
    }

    // highlight item on chart that corresponds to searched domain
    d3.selectAll("." + chart.chosenClass)
        .attr("class", function(d) {
            if (d.domain === domain) {
                return chart.chosenClass + " selected";
            } else {
                return chart.chosenClass + " unselected";
            }
        });
};

Chart.prototype.clearSearch = function() {
    d3.selectAll("." + this.chosenClass)
        .attr("class", this.chosenClass);
};

Chart.prototype.renderChart = function() {
    this.setTitle();
    this.setDescription();
    this.setContainer();
    this.setCharts();
};


