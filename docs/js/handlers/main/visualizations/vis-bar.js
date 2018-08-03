
BarChart = function(_parentElement, _data, _sortParam) {
    this.parentElement = _parentElement;
    this.data = _data;
    this.displayData = _data;
    this.sortParam = _sortParam;

    this.initVis();
};

BarChart.prototype.initVis = function() {
  var vis = this;

    vis.margin = { top: 30, right: 20, bottom: 225, left: 70 };

    vis.width = $('#' + vis.parentElement).width() - vis.margin.left - vis.margin.right;
    vis.height = $('#' + vis.parentElement).height() - vis.margin.top - vis.margin.bottom;

    vis.svg = d3.select('#' + vis.parentElement)
        .append('svg')
        .attr('width', vis.width + vis.margin.left + vis.margin.right)
        .attr('height', vis.height + vis.margin.top + vis.margin.bottom)
        .append('g')
        .attr('transform', "translate(" + vis.margin.left + "," + vis.margin.top + ")");

    vis.xScale = d3.scaleBand()
        .rangeRound([0, vis.width])
        .padding(0.15);

    vis.yScale = d3.scaleLinear()
        .range([vis.height, 0]);

    vis.xAxis = d3.axisBottom()
        .scale(vis.xScale);

    vis.yAxis = d3.axisLeft()
        .scale(vis.yScale)
        .ticks(5);

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

    vis.toolTip = d3.tip()
        .attr('class', 'd3-tip')
        .offset([-8, 0]);

    vis.wrangleData(); 
};

BarChart.prototype.wrangleData = function() {
    var vis = this;

    vis.data.sort(function(a, b) {
        return b[vis.sortParam] - a[vis.sortParam];
    });

    vis.displayData = vis.data.filter(function (d, i) {
        return (i >= barDomainFilters[0]) && (i <= barDomainFilters[1]);
    });

    vis.updateData();
};

BarChart.prototype.updateData = function() {
    var vis = this;

    vis.xScale.domain(vis.displayData.map(function(d) { return d.domain; }));
    if (vis.sortParam === "link_count") {
        vis.yScale.domain([0, d3.max(vis.displayData, function(d) { return d[vis.sortParam]; })]);
    } else {
        var yScaleDomain = d3.extent(vis.displayData, function(d) { return d[vis.sortParam]; });
        vis.yScale.domain([yScaleDomain[0] - 1, yScaleDomain[1] + 1]);
    }


    vis.toolTip.html(function(d) {
        var spacing = "   ";
        return "<div class='tipRow'><span class='tipLabel'>Domain</span>" + spacing  + "<span class='tipValue'><a href=" + d.domain + ">" + d.domain + "</a></span></div>"
            + "<div class='tipRow'><span class='tipLabel'>Citations</span>" + spacing  + "<span class='tipValue'>" + d3.format(",")(d.link_count) + "</span></div>"
            + "<div class='tipRow'><span class='tipLabel'>Alexa Rank</span>" + spacing  + "<span class='tipValue'>" + d3.format(",")(d.trust_factor_ordinal_rank) + "</span></div>"
            + "<div class='tipRow'><span class='tipLabel'>Alexa Links Into</span>" + spacing  + "<span class='tipValue'>" + d3.format(",")(d.alexa_linksincount) + "</span></div>"
            + "<div class='tipRow'><span class='tipLabel'>Trust Alpha</span>" + spacing  + "<span class='tipValue' style='color: " + trustColorScale(d.trust_factor) + ";'>" + d3.format(".2f")(d.trust_factor) + "</span></div>";
    });

    vis.svg.call(vis.toolTip);

    var transitionDuration = 0;

    var bars = vis.svg.selectAll('.bar')
        .data(vis.displayData, function(d) {
            return d.domain;
        });

    bars.enter()
        .append('rect')
        .attr('class', 'bar')
        .on('mouseover', function(d) {
            vis.toolTip.show(d);
            if (vis.sortParam !== "link_count") {
                d3.select("#point-" + d.index).attr("class", "scatter-point selected");
            }
        })
        .on('mouseout', function(d) {
            vis.toolTip.hide(d);
            if (vis.sortParam !== "link_count") {
                d3.select("#point-" + d.index).attr("class", "scatter-point");
            }
        })
        .merge(bars)
        .transition()
        .duration(transitionDuration)
        .attr('x', function(d) {
            return vis.xScale(d.domain);
        })
        .attr('y', function(d) {
            return vis.yScale(d[vis.sortParam]);
        })
        .attr('height', function(d) {
            return vis.height - vis.yScale(d[vis.sortParam]);
        })
        .attr('width', vis.xScale.bandwidth())
        .attr("fill", function(d) {
            return trustColorScale(d.trust_factor);
        });

    bars.exit().remove();

    vis.svg.select(".x-axis").transition().duration(transitionDuration).call(vis.xAxis)
        .selectAll("text")
        .attr("dy", "-.2em")
        .attr("dx", "-.9em")
        .attr("transform", "rotate(-60)")
        .style("text-anchor", "end");
    vis.svg.select(".y-axis").transition().duration(transitionDuration).call(vis.yAxis);
};