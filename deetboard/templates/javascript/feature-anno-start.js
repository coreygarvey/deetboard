<script>
	// Annotatinos should be stored in a more programatic way to
	//  allow for other types beyond expert and other
	var annotationsList = [];
	var annotationsJsonString = unescape("{{annotations_json | safe | escapejs}}");
	var annotationsJson = JSON.parse(annotationsJsonString);

	console.log("annotationsJson");
	console.log(annotationsJson);

	// Divide and conquer
	var expertAnnosList = [];
	var otherAnnosList = [];



	var expertAnnos = annotationsJson[0];
	var otherAnnos = annotationsJson[1];

	annotationsList.push(expertAnnosList);
	annotationsList.push(otherAnnosList);

	for(i=0; i<expertAnnos.length; i++){
		var annotationParsed = JSON.parse(expertAnnos[i]);
		annotationsList[0].push(annotationParsed);
	}

	for(i=0; i<otherAnnos.length; i++){
	    var annotationParsed = JSON.parse(otherAnnos[i]);
	    annotationsList[1].push(annotationParsed);
	}


	anno.addPlugin('PSQL', { base_url: 'http://127.0.0.1:8000/annotations/', media_url: 'http://127.0.0.1:8000/media/', annotations: annotationsList });
	anno.setProperties({
	  outline: '#0066ff',
	  outline_width: '3',
	  hi_outline: '#e60000',
	  hi_outline_width: '5'
	});
	// Show only expert annotations
</script>