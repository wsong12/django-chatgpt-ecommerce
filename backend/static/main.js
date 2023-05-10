 // Used to add a spinner to submit buttons

var temp_button_text;
function CustomFormSubmitPost(e) {
    var el = $(e);
    temp_button_text = el.text()
    el.attr('disabled', 'disabled').text("").append('<class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>Loading...');
    var loading = document.getElementById('loading_info');
    loading.append("Scraping the data from shopping websites and generating analysis...")
};
function CustomFormSubmitResponse(e) {
    var el = $(e);
    el.removeAttr('disabled').text(temp_button_text);
    //$('.return').append("{{data}}");
};

function getSubmitButton(form){
    return form.find(":submit")
}


                    
var DemoFunctions = function(){
	
	"use strict"
	
    var basicForm = function (){
        var form = $('#basicform')
        var submitButton = getSubmitButton(form)
        form.submit(function(event){
            event.preventDefault();
            CustomFormSubmitPost(submitButton);
            var formData = form.serialize()
			$.ajax({
				url: form.attr("action"),
				method: form.attr("method"),
				data: formData,
				success: function(json){
					CustomFormSubmitResponse(submitButton);
					var WordCount = json["word_count"]
                    WordCount = WordCount.replace(/'/g, '"') //replacing all ' with "
                    WordCount = JSON.parse(WordCount)
                    var price_range_count=json["price_range_sales"]
                    price_range_count = price_range_count.replace(/'/g, '"') //replacing all ' with "
                    price_range_count = JSON.parse(price_range_count)
                    var word_order_count=json["word_order_count"]
                    word_order_count = word_order_count.replace(/'/g, '"') //replacing all ' with "
                    word_order_count = JSON.parse(word_order_count)
                

                    var chatgpt_response_1=json["chatgpt_response_1"]
                    var chatgpt_response_2=json["chatgpt_response_2"]
                    $("#wordcloud").html("");
                    $("#loading_info").html("");
                    const width = 1000;
                    const height = 500;

                    //const color = d3.scale.ordinal(d3.schemeCategory10);
                    var fill = d3.scale.category20();
                    // Define fill function
                    function fill(d, i) {
                      return color(i);
                    }

                    // Create the wordcloud layout
                    d3.layout.cloud()
                        .size([width, height])
                        .words(WordCount.map(d => ({text: d.word, size: 10+ d.normalized_count * 7})))
                        .padding(18)
                        .rotate(() =>0)
                        .fontSize(d => d.size)
                        .on("end", draw)
                        .start();

                    // Draw the wordcloud
                    function draw(WordCount) {
                    d3.select("#wordcloud").append("svg")
                            .attr("width", width)
                            .attr("height", height)
                            .attr("class", "wordcloud")
                            .append("g")
                        // without the transform, words words would get cutoff to the left and top, they would
                        // appear outside of the SVG area
                            .attr("transform", "translate(200,190)")
                            .selectAll("text")
                            .data(WordCount)
                            .enter()
                            .append("text")
                            .style("-webkit-text-stroke-width", "1px")
                            .style("-webkit-text-stroke-color", "black")
                            .style("fill", function(d, i) { return fill(i); })
                            .style("font-size", function(d) { return d.size + "px"; })
                            .attr("text-anchor", "start")
                            .attr("transform", function(d) {
                                return "translate(" + [Math.abs(d.x), d.y] + ")rotate(" + d.rotate + ")";
                            })
                            .text(function(d) { return d.text; })
                            .on("click", function (d, i){
                             window.open(d.url, "_self");
                    });

                    //create charts
                    function createPareto(){
                        var dps = [];
                        var yValue, yTotal = 0, yPercent = 0;

                        for(var i = 0; i < chart.data[0].dataPoints.length; i++)
                            yTotal += chart.data[0].dataPoints[i].y;

                        for(var i = 0; i < chart.data[0].dataPoints.length; i++){
                            yValue = chart.data[0].dataPoints[i].y;
                            yPercent += (yValue / yTotal * 100);
                            dps.push({label: chart.data[0].dataPoints[i].label, y: yPercent});
                        }
                        
                        chart.addTo("data",{type:"line", yValueFormatString: "0.##\"%\"", dataPoints: dps});
                        chart.data[1].set("axisYType", "secondary", false);
                        chart.axisY[0].set("maximum", yTotal);
                        chart.axisY2[0].set("maximum", 100);
                    };

                    var chart = new CanvasJS.Chart("chartContainer1", {
                        title:{
                            text: "Key Word VS Order Counts"
                        },
                        axisY: {
                            title: "Number of Orders",
                            lineColor: "#4F81BC",
                            tickColor: "#4F81BC",
                            labelFontColor: "#4F81BC"
                        },
                        axisY2: {
                            title: "Percent",
                            suffix: "%",
                            lineColor: "#C0504E",
                            tickColor: "#C0504E",
                            labelFontColor: "#C0504E"
                        },
                        data: [{
                            type: "column",
                            dataPoints: word_order_count
                    }]
                    });
                    chart.render();
                    createPareto(); 
                    var chatdiv1 = document.getElementById('chatgpt1');
                    chatdiv1.append(chatgpt_response_1)
                    var chatdiv2 = document.getElementById('chatgpt2');
                    chatdiv2.append(chatgpt_response_2)               
                                        

                    var chart = new CanvasJS.Chart("chartContainer2", {
                        animationEnabled: true,
                        exportEnabled: true,
                        theme: "light1", // "light1", "light2", "dark1", "dark2"
                        title:{
                            text: "Price range VS order counts"
                        },
                        axisY: {
                          includeZero: false
                        },
                        data: [{
                            type: "column", //change type to bar, line, area, pie, etc
                            //indexLabel: "{y}", //Shows y value on all Data Points
                            indexLabelFontColor: "#5A5757",
                            indexLabelFontSize: 16,
                            indexLabelPlacement: "outside",
                            dataPoints: price_range_count
                        }]
                    });
                    chart.render();

                    
                                                   
                }
				},
				error: function(json){
					CustomFormSubmitResponse(submitButton);
					console.log(json.status + ": " + json.responseText);
				}
			})
        });
    };

    var basicImageForm = function (){
        var form = $('#basicimageform')
        var submitButton = getSubmitButton(form)
        form.submit(function(event){
            event.preventDefault();
            CustomFormSubmitPost(submitButton);
            var formData = form.serialize()
			$.ajax({
				url: form.attr("action"),
				method: form.attr("method"),
				data: formData,
				success: function(json){
					CustomFormSubmitResponse(submitButton);
					var image = json["data"]
                    $('.images').remove();
                    $('.result').append(
                        "<img class='images' height='200' width='200' src="+image+">"
                        );

				},
				error: function(json){
					CustomFormSubmitResponse(submitButton);
					console.log(json.status + ": " + json.responseText);
				}
			})
        });
    };

	/* Function ============ */
	return {
		init:function(){
			basicForm();
            basicImageForm();
		},
	}
	
}();

/* Document.ready Start */	
jQuery(document).ready(function() {
    'use strict';
	DemoFunctions.init();
	
});

$(function() {
    // This function gets cookie with a given name
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    $.ajaxSetup({
        beforeSend: function(json, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                json.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
})
