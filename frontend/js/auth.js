// API Base URL
const API_BASE_URL = 'http://localhost:5000/api';

// Show error message
function showError(message) {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    } else {
        alert(message);
    }
}

// Sign Up Handler
const signupForm = document.getElementById('signup-form');
if (signupForm) {
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = {
            username: document.getElementById('username').value,
            email: document.getElementById('email').value,
            password: document.getElementById('password').value,
            full_name: document.getElementById('full_name').value,
            phone_number: document.getElementById('phone_number').value
        };
        
        const confirmPassword = document.getElementById('confirm_password').value;
        
        // Validate passwords match
        if (formData.password !== confirmPassword) {
            showError('Passwords do not match!');
            return;
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/auth/signup`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert('Registration successful! Please sign in.');
                window.location.href = 'signin.html';
            } else {
                showError(data.message || 'Registration failed');
            }
        } catch (error) {
            console.error('Error:', error);
            showError('Network error. Please try again.');
        }
    });
}

// Sign In Handler
const signinForm = document.getElementById('signin-form');
if (signinForm) {
    signinForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = {
            username: document.getElementById('username').value,
            password: document.getElementById('password').value
        };
        
        try {
            const response = await fetch(`${API_BASE_URL}/auth/signin`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Store token and user data
                localStorage.setItem('token', data.token);
                localStorage.setItem('user', JSON.stringify(data.user));
                
                // Redirect based on user type
                if (data.user.user_type === 'admin') {
                    window.location.href = 'admin.html';
                } else {
                    window.location.href = 'index.html';
                }
            } else {
                showError(data.message || 'Login failed');
            }
        } catch (error) {
            console.error('Error:', error);
            showError('Network error. Please try again.');
        }
    });
}
