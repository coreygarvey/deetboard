<script>

	$("form input[class='file-upload']").change(function () { 
	    // Handle the click event here
	    
	    var fullPath = $(this).val();
	    
	    var filename = fullPath.replace(/^.*[\\\/]/, '');

	    $("#upload-file-info").html(filename);
	});
	
</script>