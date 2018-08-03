ScatterChart = function(_parentElement, _data) {
    this.parentElement = _parentElement;
    this.data = _data;
    this.displayData = _data;

    this.initVis();
};

ScatterChart.prototype.initVis = function() {
    var vis = this;

    vis.margin = { top: 30, right: 20, bottom: 50, left: 70 };

    vis.width = $('#' + vis.parentElement).width() - vis.margin.left - vis.margin.right;
    vis.height = $('#' + vis.parentElement).height() - vis.margin.top - vis.margin.bottom;

    vis.svg = d3.select('#' + vis.parentElement)
        .append('svg')
        .attr('width', vis.width + vis.margin.left + vis.margin.right)
        .attr('height', vis.height + vis.margin.top + vis.margin.bottom)
        .append('g')
        .attr('transform', "translate(" + vis.margin.left + "," + vis.margin.top + ")");

    vis.xScale = d3.scaleLog()
        .range([0, vis.width]);

    vis.yScale = d3.scaleLog()
        .range([vis.height, 0]);

    vis.xAxis = d3.axisBottom()
        .scale(vis.xScale)
        .ticks(5, ",");

    vis.yAxis = d3.axisLeft()
        .scale(vis.yScale)
        .ticks(5, ",");

    vis.svg.append("g")
        .attr("class", "x-axis axis")
        .attr("transform", "translate(0," + vis.height + ")");

    vis.svg.append("g")
        .attr("class", "y-axis");

    vis.svg.append('text')
        .attr('class', 'axis-label')
        .attr('x', 0)
        .attr('y', -10)
        .text("# of citations");

    vis.svg.append('text')
        .attr('class', 'axis-label')
        .attr('text-anchor', 'end')
        .attr('x', vis.width)
        .attr('y', vis.height - 10)
        .text("# of links in");

    vis.toolTip = d3.tip()
        .attr('class', 'd3-tip')
        .offset([-8, 0]);

    vis.wrangleData();
};

ScatterChart.prototype.wrangleData = function() {
    var vis = this;

    vis.yVar = "link_count";
    vis.xVar = "alexa_linksincount";
    vis.colorVar = "trust_factor";

    vis.displayData = vis.data.filter(function(d) {
        return d[vis.yVar] > 0;
    });
    
    vis.xScale.domain(d3.extent(vis.displayData, function(d) { return d[vis.xVar] }));
    vis.yScale.domain(d3.extent(vis.displayData, function(d) { return d[vis.yVar]; }));

    vis.updateChart();
};

ScatterChart.prototype.updateChart = function() {
    var vis = this;

    vis.toolTip.html(function(d) {
        var spacing = "   ";
        return "<div class='tipRow'><span class='tipLabel'>Domain</span>" + spacing  + "<span class='tipValue'><a href=" + d.domain + ">" + d.domain + "</a></span></div>"
            + "<div class='tipRow'><span class='tipLabel'>Citations</span>" + spacing  + "<span class='tipValue'>" + d3.format(",")(d.link_count) + "</span></div>"
            + "<div class='tipRow'><span class='tipLabel'>Alexa Rank</span>" + spacing  + "<span class='tipValue'>" + d3.format(",")(d.trust_factor_ordinal_rank) + "</span></div>"
            + "<div class='tipRow'><span class='tipLabel'>Alexa Links Into</span>" + spacing  + "<span class='tipValue'>" + d3.format(",")(d.alexa_linksincount) + "</span></div>"
            + "<div class='tipRow'><span class='tipLabel'>Trust Alpha</span>" + spacing  + "<span class='tipValue' style='color: " + trustColorScale(d.trust_factor) + ";'>" + d3.format(".2f")(d.trust_factor) + "</span></div>";
    });

    vis.svg.call(vis.toolTip);

    var point = vis.svg.selectAll(".scatter-point")
        .data(vis.displayData);

    point.enter()
        .append("circle")
        .attr("class", "scatter-point")
        .attr("id", function(d) {
            return "point-" + d.trust_factor_ordinal_rank;
        })
        .on("mouseover", vis.toolTip.show)
        .on("mouseout", vis.toolTip.hide)
        .merge(point)
        .attr("cx", function(d) { return vis.xScale(d[vis.xVar]);})
        .attr("cy", function(d) { return vis.yScale(d[vis.yVar]);})
        .attr("r", 5)
        .attr("fill", function(d) {
            return trustColorScale(d.trust_factor);
        });

    point.exit().remove();

    vis.svg.select(".x-axis").transition().duration(1000).call(vis.xAxis);
    vis.svg.select(".y-axis").transition().duration(1000).call(vis.yAxis);
};