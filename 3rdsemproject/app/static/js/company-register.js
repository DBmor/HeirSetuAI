const form = document.getElementById('companyRegistrationForm');
const panels = [...document.querySelectorAll('.step-panel')];
const progressItems = [...document.querySelectorAll('.progress li')];
const stepNumber = document.getElementById('stepNumber');
const progressFill = document.getElementById('progressFill');
const backButton = document.getElementById('backButton');
const nextButton = document.getElementById('nextButton');
const validationMessage = document.getElementById('validationMessage');
let currentStep = 1;

// Basic patterns used to check common form values.
const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const phonePattern = /^\+?[0-9\s-]{10,16}$/;
const urlPattern = /^https?:\/\/[^\s]+$/i;
const corporateIdPattern = /^[A-Za-z0-9\-/]{6,30}$/;
const allowedFileTypes = ['application/pdf', 'image/jpeg', 'image/png'];
const maxFileSize = 5 * 1024 * 1024;

// Mark every label containing a required control with a visible asterisk.
document.querySelectorAll('#companyRegistrationForm label').forEach(label => {
  if (label.querySelector('[required]')) label.classList.add('required-label');
});

function setFieldError(field, message) {
  // Show a visible message because hidden uploads and checkboxes cannot use a popup reliably.
  validationMessage.textContent = message;
  validationMessage.style.display = 'block';
  field.focus({ preventScroll: true });
  validationMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function validateField(field) {
  // Validate text, email, phone, OTP, ID and URL fields by their input name.
  const value = field.value.trim();
  const name = field.name;

  if (field.required && (field.type === 'checkbox' ? !field.checked : !value)) {
    setFieldError(field, 'This field is required.');
    return false;
  }
  if (value && (name === 'official_email' || name === 'company_email') && !emailPattern.test(value)) {
    setFieldError(field, 'Enter a valid email address.');
    return false;
  }
  if (value && ['phone', 'company_phone'].includes(name) && !phonePattern.test(value)) {
    setFieldError(field, 'Enter a valid phone number.');
    return false;
  }
  if (value && ['email_otp', 'phone_otp'].includes(name) && !/^\d{6}$/.test(value)) {
    setFieldError(field, 'OTP must contain exactly 6 digits.');
    return false;
  }
  if (value && name === 'corporate_id' && !corporateIdPattern.test(value)) {
    setFieldError(field, 'Enter a valid CIN, GST or PAN number.');
    return false;
  }
  if (value && ['website', 'linkedin'].includes(name) && !urlPattern.test(value)) {
    setFieldError(field, 'URL must start with http:// or https://.');
    return false;
  }
  if (value && ['representative_name', 'company_name'].includes(name) && value.length < 2) {
    setFieldError(field, 'Name must contain at least 2 characters.');
    return false;
  }
  return true;
}

function validateFiles(panel) {
  // Registration requires every verification document and limits each file to 5 MB.
  for (const field of panel.querySelectorAll('input[type="file"]')) {
    const file = field.files[0];
    if (!file) {
      if (currentStep === 3) {
        setFieldError(field, 'Please upload this document.');
        return false;
      }
      continue;
    }
    if (!allowedFileTypes.includes(file.type)) {
      setFieldError(field, 'Only PDF, JPG or PNG files are allowed.');
      return false;
    }
    if (file.size > maxFileSize) {
      setFieldError(field, 'File size must be 5 MB or less.');
      return false;
    }
  }
  return true;
}

function showStep(step) {
  // Display one panel and update the progress indicator.
  currentStep = step;
  validationMessage.textContent = '';
  validationMessage.style.display = 'none';
  panels.forEach(panel => panel.classList.toggle('active', Number(panel.dataset.panel) === step));
  progressItems.forEach(item => {
    const itemStep = Number(item.dataset.step);
    item.classList.toggle('active', itemStep === step);
    item.classList.toggle('complete', itemStep < step);
  });
  stepNumber.textContent = step;
  progressFill.style.width = `${((step - 1) / 4) * 100}%`;
  backButton.hidden = step === 1 || step === 5;
  nextButton.hidden = step === 5;
  nextButton.innerHTML = step === 4 ? 'Complete registration <span>→</span>' : 'Continue <span>→</span>';
}

function validateCurrentStep() {
  // Stop the user on the current step until all its fields are valid.
  const panel = panels[currentStep - 1];
  const fields = [...panel.querySelectorAll('input:not([type="file"]), select, textarea')];
  for (const field of fields) {
    if (!validateField(field) || !field.checkValidity()) {
      if (!validationMessage.textContent) {
        validationMessage.textContent = field.validationMessage || 'Please check this field.';
        validationMessage.style.display = 'block';
      }
      return false;
    }
  }
  if (!validateFiles(panel)) return false;
  if (currentStep === 4 && form.password.value !== form.confirm_password.value) {
    setFieldError(form.confirm_password, 'Passwords do not match.');
    return false;
  }
  if (currentStep === 4 && !/(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}/.test(form.password.value)) {
    setFieldError(form.password, 'Password must be 8+ characters with uppercase, lowercase and a number.');
    return false;
  }
  return true;
}

nextButton.addEventListener('click', () => {
  // Move forward only after the current step passes validation.
  if (validateCurrentStep() && currentStep < 5) showStep(currentStep + 1);
});
backButton.addEventListener('click', () => showStep(Math.max(1, currentStep - 1)));

document.querySelectorAll('input[type="file"]').forEach(input => {
  // Show the selected file name inside its upload area.
  input.addEventListener('change', () => {
    const label = input.closest('label');
    const text = label.querySelector('.drop-zone, .upload-mini span');
    if (input.files[0] && text) text.innerHTML = `✓ ${input.files[0].name}`;
  });
});

showStep(1);
