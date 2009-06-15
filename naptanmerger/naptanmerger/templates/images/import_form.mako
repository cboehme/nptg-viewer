<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">

<html>
<head>
	<title>NaPTAN Merger</title>

	<link rel="icon" type="image/png" href="site-icon.png">

	<link rel="stylesheet" href="base.css" type="text/css">
</head>

<body>
	<h1>Image import</h1>
	<form action="${h.url_for("importdata", "images")}" method="post" enctype="multipart/form-data">
		<input type="file" name="image"><br>
		<input type="submit" value="Upload image">
	</form>
</body>
</html>
