<script>

	$(".file-upload").on('change', function () { 
	    
	    var fullPath = $(this).val();
	    
	    var filename = fullPath.replace(/^.*[\\\/]/, '');

	    $("#upload-info").html(filename);
	    
	});
	
</script>