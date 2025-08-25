<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale = 1.0">
<meta http-equiv="X-UA-Compatible" content="ie=edge">
<title>WAVE</title>

<!-- Font Icon -->
<link rel="stylesheet"
	href="fonts/material-icon/css/material-design-iconic-font.min.css">

<!-- Main css -->
<link rel="stylesheet" href="css/style.css">
</head>
<body>

<input type="hidden" id="status" value="<%= request.getAttribute("status") %>">

	<div class="main">

		<!-- Sign up form -->
		<section class="signup">
			<div class="container">
				<div class="signup-content">
					<div class="signup-form">
						<h2 class="form-title">Add Product</h2>
					
						<form method="post" action="addproductsdata" class="register-form"
							id="register-form">
							<div class="form-group">
								<label for="id"><i class="zmdi zmdi-lock-outline"></i></label>
								<input type="text" name="id" id="id"
									placeholder="Product Id" / required>
							</div>
							<div class="form-group">
								<label for="name"><i
									class="zmdi zmdi-account material-icons-name"></i></label> <input
									type="text" name="name" id="name" placeholder="Product Name" / required>
							</div>
							<div class="form-group">
								<label for="integer-input"><i class="zmdi zmdi-email"></i></label> <input
									type="number" name="price" id="integer-input" placeholder="Price" / required>
							</div>
							<div class="form-group">
								<label for="gender"><i class="zmdi zmdi-lock-outline"></i></label>
								<input type="text" name="gender" id="gender"
									placeholder="Gender" / required>
							</div>
							<div class="form-group">
								<label for="integer-input"><i class="zmdi zmdi-lock-outline"></i></label>
								<input type="number" name="size" id="integer-input"
									placeholder="Size" / required>
							</div>
							<div class="form-group">
								<label for="integer-input"><i class="zmdi zmdi-lock-outline"></i></label>
								<input type="number" name="quantity" id="integer-input"
									placeholder="Quantity" / required>
							</div>
							
							
							<div class="form-group">
								<label for="description"><i class="zmdi zmdi-lock-outline"></i></label>
								<input type="text" name="description" id="description"
									placeholder="Description" / required>
							</div>
							
							
							<div class="form-group form-button">
								<input type="submit" name="signup" id="signup"
									class="form-submit" value="Register" />
									
								<input type="reset" name="cancel" id="cancel"
									class="form-submit" value="cancel" />
									
								<a href = 'ProductList'>Product List</a>
							</div>
							
						</form>
					</div>
					
				</div>
			</div>
		</section>


	</div>
	<!-- JS -->
	<script src="vendor/jquery/jquery.min.js"></script>
	<script src="js/main.js"></script>
	<script src = "http://unpkg.com/sweetalert/dist/sweetalert.min.js">
	</script>
	<link rel = "stylesheet" herf="alert/dist/sweetalert.css">
	
	<script type="text/javascript">
	
	var status = document.getElementById("status").value;
	if(status == "success"){
		swal("Congrats", "Products data successfully entered", "success");
	}
	
	</script>



</body>
<!-- This templates was made by Colorlib (https://colorlib.com) -->
</html>