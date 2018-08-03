ForceVis = function(_parentElement, _data) {
    this.parentElement = _parentElement;
    this.data = _data;
    this.displayData = _data;

    this.initVis();
};

ForceVis.prototype.initVis = function() {
    var vis = this;
    vis.margin = {top: 10, right: 10, bottom: 50, left: 10};

    vis.width = $("#" + vis.parentElement).width() - vis.margin.left - vis.margin.right;
    vis.height = $("#" + vis.parentElement).height() - vis.margin.top - vis.margin.bottom;

    // SVG drawing area
    vis.svg = d3.select("#" + vis.parentElement).append("svg")
        .attr("width", vis.width + vis.margin.left + vis.margin.right)
        .attr("height", vis.height + vis.margin.top + vis.margin.bottom)
        .append("g")
        .attr("transform", "translate(" + vis.margin.left + "," + vis.margin.top + ")");

    vis.linkContainer = vis.svg.append("g");
    vis.nodeContainer = vis.svg.append("g");

    var simulationDistance = $("#" + vis.parentElement).height() * .75;
    var simulationCharge = $("#" + vis.parentElement).height() * -.15;

    vis.simulation = d3.forceSimulation()
        .force("link", d3.forceLink()
            .id(function(d) { return d.domain; })
            .distance(function(d) { return simulationDistance / d.value; }))
        .force("charge", d3.forceManyBody()
            .strength(function(d) { return simulationCharge;}))
        .force("center", d3.forceCenter(vis.width / 2, vis.height / 2));

    vis.nodeRange = [3, 15];

    vis.nodeScaler = d3.scaleLog()
        .range(vis.nodeRange)
        .domain(d3.extent(vis.data.nodes, function(d) {
            return d.link_count;
        }));

    vis.toolTip = d3.tip()
        .attr('class', 'd3-tip')
        .offset([-8, 0]);

    vis.wrangleData();
};

ForceVis.prototype.wrangleData = function() {
    var vis = this;

    vis.diplayData = vis.data;

    domainData.sort(function(a, b) {
        return b.count - a.count;
    });

    domainData.forEach(function(d, i) {
       d.index = i;
    });

    vis.updateData();
};

ForceVis.prototype.updateData = function() {
    var vis = this;

    var link = vis.linkContainer.selectAll(".link")
        .data(vis.displayData.links, function(d) {
            return d.source + '-' + d.target;
        });

    link.exit().remove();

    link = link.enter().append("line")
        .attr("class", "link")
        .merge(link);

    vis.toolTip.html(function(d) {
        var spacing = "   ";
        return "<div class='tipRow'><span class='tipLabel'>Domain</span>" + spacing  + "<span class='tipValue'><a href=" + d.domain + ">" + d.domain + "</a></span></div>"
            + "<div class='tipRow'><span class='tipLabel'>Citations</span>" + spacing  + "<span class='tipValue'>" + d3.format(",")(d.link_count) + "</span></div>"
            + "<div class='tipRow'><span class='tipLabel'>Alexa Rank</span>" + spacing  + "<span class='tipValue'>" + d3.format(",")(d.trust_factor_ordinal_rank) + "</span></div>"
            + "<div class='tipRow'><span class='tipLabel'>Alexa Links Into</span>" + spacing  + "<span class='tipValue'>" + d3.format(",")(d.alexa_linksincount) + "</span></div>"
            + "<div class='tipRow'><span class='tipLabel'>Trust Alpha</span>" + spacing  + "<span class='tipValue' style='color: " + trustColorScale(d.trust_factor) + ";'>" + d3.format(".2f")(d.trust_factor) + "</span></div>";
    });

    vis.svg.call(vis.toolTip);

    var node = vis.nodeContainer.selectAll(".node")
        .data(vis.displayData.nodes, function(d) {
            return d.domain;
        });

    node.exit().remove();

    node = node.enter().append("circle")
        .attr("class", "node")
        .attr("r", function (d) {
            return vis.nodeScaler(d.link_count);
        })
        .on("mouseover", vis.toolTip.show)
        .on("mouseout", vis.toolTip.hide)
        .merge(node)
        .attr("fill", function(d) {
            return trustColorScale(d.trust_factor);
        });

    vis.simulation.nodes(vis.displayData.nodes).on("tick", ticked);
    vis.simulation.force("link").links(vis.displayData.links);
    vis.simulation.alpha(1).alphaTarget(0).restart();

    function ticked() {

        var radius = vis.nodeRange[1];

        node.attr("cx", function(d) { return d.x = Math.max(radius, Math.min(vis.width - radius, d.x)); })
            .attr("cy", function(d) { return d.y = Math.max(radius, Math.min(vis.height - radius, d.y)); });

        link.attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });
    }
};
