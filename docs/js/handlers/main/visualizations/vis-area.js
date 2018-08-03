
LineChart = function(_parentElement, _data, _fullHeight, _sortParam) {
    this.parentElement = _parentElement;
    this.displayData = _data;
    this.fullHeight = _fullHeight;
    this.sortParam = _sortParam;

    this.initVis();
};

LineChart.prototype.initVis = function() {
    var vis = this;

    vis.margin = { top: 0, right: 20, bottom: 0, left: 70 };

    vis.width = $('#' + vis.parentElement).width() - vis.margin.left - vis.margin.right,
        vis.height = vis.fullHeight - vis.margin.top - vis.margin.bottom;

    vis.svg = d3.select('#' + vis.parentElement)
        .append('svg')
        .attr('width', vis.width + vis.margin.left + vis.margin.right)
        .attr('height', vis.height + vis.margin.top + vis.margin.bottom)
        .append('g')
        .attr('transform', "translate(" + vis.margin.left + "," + vis.margin.top + ")");

    vis.xScale = d3.scaleLinear()
        .rangeRound([0, vis.width])
        .domain([0, vis.displayData.length]);

    if (vis.sortParam === "link_count") {
        vis.yScale = d3.scaleLog();
    } else {
        vis.yScale = d3.scaleLinear();
    }

    vis.yScale
        .range([vis.height, 0])
        .domain(d3.extent(vis.displayData, function(d) { return d[vis.sortParam]; }));

    vis.line = d3.area()
        .x(function(d, i){ return vis.xScale(i);})
        .y0(function(d) {
            if (vis.sortParam === "link_count") {
                return vis.height;
            } else {
                var val = Math.min(0, d[vis.sortParam]);
                return vis.yScale(val);
            }
        })
        .y1(function(d) {
            if (vis.sortParam === "link_count") {
                return vis.yScale(d[vis.sortParam]);
            } else {
                var val = Math.max(0, d[vis.sortParam]);
                return vis.yScale(val);
            }
        })
        .curve(d3.curveCardinal);

    vis.brush = d3.brushX()
        .extent([[0, 0], [vis.width, vis.height]]);

    vis.wrangleData();
};

LineChart.prototype.wrangleData = function() {
    var vis = this;

    vis.displayData.sort(function(a, b) {
        return b[vis.sortParam] - a[vis.sortParam];
    });

    domainData = vis.displayData;
    domainData.forEach(function(d, i) {
        d.index = i
    });

    vis.updateChart();
};

LineChart.prototype.updateChart = function() {
    var vis = this;

    var line = vis.svg.selectAll('.all-line')
        .data([vis.displayData]);

    line.enter()
        .append('path')
        .attr('class', 'all-line')
        .merge(line)
        .transition()
        .duration(1000)
        .attr("d", vis.line)
        .attr("fill", baseColor);

    line.exit().remove();

    vis.brushItem = vis.svg.append("g")
        .attr("class", "brush");

    vis.brushItem.call(vis.brush)
        .call(vis.brush.move, [vis.xScale(0), vis.xScale(zoomThreshold)]);

    // removes handle to resize the brush
    d3.selectAll('.brush>.handle').remove();
    // removes crosshair cursor
    d3.selectAll('.brush>.overlay').remove();
};