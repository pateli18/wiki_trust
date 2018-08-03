function generateLegend() {
    var margin = { top: 0, right: 60, bottom: 0, left: 60};

    var width = 280 - margin.left - margin.right;
    var height = 40 - margin.top - margin.bottom;

    var svg = d3.select("#legend-container")
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom);

    var legendContainer = svg.append('g')
        .attr('transform', "translate(" + margin.left + "," + margin.top + ")");

    var legend = d3.legendColor()
        .shapeWidth(30)
        .cells(5)
        .orient('horizontal')
        .scale(trustColorScale);

    svg.append("text")
        .text("High Alpha")
        .attr("text-anchor", "end")
        .attr("class", "legend-label")
        .attr("x", width + margin.left + margin.right)
        .attr("y", height / 3.5);

    svg.append("text")
        .text("Low Alpha")
        .attr("text-anchor", "start")
        .attr("class", "legend-label")
        .attr("x", 0)
        .attr("y", height / 3.5);

    legendContainer.call(legend);
}

function initiateAutoComplete() {
    $("#search-site").autocomplete({
        source: domainData.map(function(d) { return {label:d.domain, index:d.index}; }),
        select: function(event, ui) {
            $("#search-site").val(ui.item.label);
            searchParam.id = ui.item.index;
            searchParam.label = ui.item.label;
            initiateSearch(searchParam.id, searchParam.label);
        }
    })
        .data( "ui-autocomplete" )._renderItem = function( ul, item ) {
            console.log(item);
        return $( '<li>' )
            .append( '<div class="search-result"><span class="search-name">' + item.label + '</span></div>' )
            .appendTo( ul );
    };

    $('[data-toggle="tooltip"]').tooltip();
}

function initiateSearch(id, domain) {
    $("#search-clear").show();
    selectedChart.searchChart(id, domain);
}

function clearSearch() {
    $("#search-clear").hide();
    $("#search-site").val('');
    selectedChart.clearSearch();
    barDomainFilters = [0, zoomThreshold];
    searchParam.id = null;
    searchParam.label = null;
}