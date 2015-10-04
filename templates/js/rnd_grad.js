function runmain(){
  // Define variable colors
	var back = ['#00ff22', '#abff00', '#fffe00', '#ffb800', '#ff0a00', '#ff0099', '#f200ff', '#7100ff', '#0019ff', '#00e3ff'];
	
	$('#hero').each(function() {
		
		// First random color
		var rand1 = back[Math.floor(Math.random() * back.length)];
		// Second random color
		var rand2 = back[Math.floor(Math.random() * back.length)];
		
		var grad = $(this);
		
		// Convert Hex color to RGB
		function convertHex(hex,opacity){
		    hex = hex.replace('#','');
		    r = parseInt(hex.substring(0,2), 16);
		    g = parseInt(hex.substring(2,4), 16);
		    b = parseInt(hex.substring(4,6), 16);
			
			// Add Opacity to RGB to obtain RGBA
		    result = 'rgba('+r+','+g+','+b+','+opacity/100+')';
		    return result;
		}
		
		// Gradient rules

		grad.css('background-color', convertHex(rand1,100) );
		grad.css("background-image", "-webkit-gradient(linear, left top, left bottom, color-stop(0%,"+ convertHex(rand1,100) +"), color-stop(100%,"+ convertHex(rand2,100) +"))");
		grad.css("background-image", "-webkit-linear-gradient(top,  "+ convertHex(rand1,100) +" 0%,"+ convertHex(rand2,100) +" 100%)");
		grad.css("background-image", "-o-linear-gradient(top, "+ convertHex(rand1,100) +" 0%,"+ convertHex(rand2,100) +" 100%)");
		grad.css("background-image", "-ms-linear-gradient(top, "+ convertHex(rand1,100) +" 0%,"+ convertHex(rand2,100) +" 100%)");
		grad.css("background-image", "linear-gradient(to bottom, "+ convertHex(rand1,100) +" 0%,"+ convertHex(rand2,100) +" 100%)");
		grad.css("filter", "progid:DXImageTransform.Microsoft.gradient( startColorstr='"+ convertHex(rand1,100) +"', endColorstr='"+ convertHex(rand2,100) +"',GradientType=0 )");
        

	});
	};