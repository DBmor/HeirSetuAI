// ---- state ----
let currentMode = 'login';     // 'login' | 'register'
let currentRole = 'candidate'; // 'candidate' | 'company'

const roleThumb = document.getElementById('roleThumb');
const roleCandidateBtn = document.getElementById('roleCandidateBtn');
const roleCompanyBtn = document.getElementById('roleCompanyBtn');
const nameField = document.getElementById('nameField');
const nameLabel = document.getElementById('nameLabel');
const nameInput = document.getElementById('nameInput');
const websiteField = document.getElementById('websiteField');
const emailLabel = document.getElementById('emailLabel');
const submitBtn = document.getElementById('submitBtn');
const googleLabel = document.getElementById('googleLabel');
const formError = document.getElementById('formError');
const authForm = document.getElementById('authForm');

function setMode(mode) {
  currentMode = mode;
  document.querySelectorAll('.mode-tab').forEach(t => t.classList.toggle('active', t.dataset.mode === mode));

  const isRegister = mode === 'register';
  nameField.classList.toggle('hidden', !isRegister);
  nameInput.required = isRegister;
  websiteField.classList.toggle('hidden', !(isRegister && currentRole === 'company'));

  submitBtn.textContent = isRegister
    ? (currentRole === 'company' ? 'Create company account' : 'Create account')
    : 'Log in';
  googleLabel.textContent = isRegister ? 'Sign up with Google' : 'Continue with Google';
  formError.classList.add('hidden');
}

function setRole(role) {
  currentRole = role;
  roleThumb.classList.toggle('company', role === 'company');
  roleCandidateBtn.classList.toggle('active', role === 'candidate');
  roleCompanyBtn.classList.toggle('active', role === 'company');

  nameLabel.textContent = role === 'company' ? 'Company name' : 'Full name';
  nameInput.placeholder = role === 'company' ? 'e.g. Acme Technologies Pvt. Ltd.' : 'e.g. Bhavika Dhamecha';
  emailLabel.textContent = role === 'company' ? 'Official work email' : 'Email';

  // website field only makes sense for company + register mode
  websiteField.classList.toggle('hidden', !(currentMode === 'register' && role === 'company'));

  submitBtn.textContent = currentMode === 'register'
    ? (role === 'company' ? 'Create company account' : 'Create account')
    : 'Log in';
}

authForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  formError.classList.add('hidden');

  const formData = new FormData(authForm);
  const payload = {
    role: currentRole,
    email: formData.get('email'),
    password: formData.get('password'),
  };
  if (currentMode === 'register') {
    payload.name = formData.get('name');
    if (currentRole === 'company') payload.website = formData.get('website');
  }

  const endpoint = currentMode === 'register' ? '/auth/register' : '/auth/login';
  submitBtn.disabled = true;
  submitBtn.textContent = 'Please wait…';

  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (!res.ok) {
      formError.textContent = data.message || 'Something went wrong. Please try again.';
      formError.classList.remove('hidden');
      return;
    }

    // HttpOnly cookie is set server-side by set_access_cookies
    window.location.href = data.redirect || (data.role === 'company' ? '/company/dashboard' : '/candidate/home');
  } catch (err) {
    formError.textContent = 'Network error — please check your connection and try again.';
    formError.classList.remove('hidden');
  } finally {
    submitBtn.disabled = false;
    setMode(currentMode);
  }
});

function continueWithGoogle() {
  // role is passed as a query param so the callback knows which account type to create
  window.location.href = `/auth/google/login?role=${currentRole}`;
}

// init
setMode('login');
setRole('candidate');
