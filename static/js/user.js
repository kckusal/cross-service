const LoginForm = document.getElementById('login-form');
const RegisterForm = document.getElementById('register-form');

function clearLoginForm() {
    LoginForm.elements.namedItem('username').value="";
    LoginForm.elements.namedItem('password').value="";
}

function clearRegisterForm() {
    const fields = RegisterForm.elements;

    fields.namedItem('first_name').value = "";
    fields.namedItem('last_name').value = "";
    fields.namedItem('phone').value = "";
    fields.namedItem('address').value = "";
    fields.namedItem('bio').value = "";
    fields.namedItem('available')[0].checked = false;
    fields.namedItem('available')[1].checked = false;

    fields.namedItem('email').value = "";
    fields.namedItem('password').value = "";
    fields.namedItem('confirm_password').value = "";
}