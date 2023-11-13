	/* When eye is clicked, password input type is changed to text and vice versa to make it visible/invisible, respectively, and the eye type changes to the other one to show what the next click does*/
	function togglePasswordVisibility() {
		const passwordInput = document.getElementById('id_password');
		const passwordToggle = document.querySelector('.password-toggle');
		var type = document.getElementById("id_password").type;
		if (passwordInput.type === 'password') {
		  passwordInput.type = 'text';
		  passwordToggle.classList.add('active');
		} else {
		  passwordInput.type = 'password';
		  passwordToggle.classList.remove('active');
		}
	}
	function toggleConfirmPasswordVisibility() {
		const passwordInput = document.getElementById('id_confirmationPassword');
		const passwordToggle = document.querySelector('.password-toggle2');
		var type = document.getElementById("id_confirmationPassword").type;
		if (passwordInput.type === 'password') {
		  passwordInput.type = 'text';
		  passwordToggle.classList.add('active');
		} else {
		  passwordInput.type = 'password';
		  passwordToggle.classList.remove('active');
		}
	}