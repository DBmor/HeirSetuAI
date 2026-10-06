const form = document.getElementById('companyRegistrationForm');
const panels = [...document.querySelectorAll('.step-panel')];
const progressItems = [...document.querySelectorAll('.progress li')];
const stepNumber = document.getElementById('stepNumber');
const progressFill = document.getElementById('progressFill');
const backButton = document.getElementById('backButton');
const nextButton = document.getElementById('nextButton');
const validationMessage = document.getElementById('validationMessage');
let currentStep = 1;
let otpVerified = { email: false, phone: false };

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
  validationMessage.textContent = '✗ ' + message;
  validationMessage.style.display = 'block';
  validationMessage.style.color = '#b42318';
  validationMessage.style.borderColor = '#f0b8b8';
  validationMessage.style.background = '#fff4f4';
  field.focus({ preventScroll: true });
  validationMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function setFieldSuccess(message) {
  validationMessage.textContent = '✓ ' + message;
  validationMessage.style.display = 'block';
  validationMessage.style.color = '#2e7d32';
  validationMessage.style.borderColor = '#c8e6c9';
  validationMessage.style.background = '#f1f8e9';
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
        validationMessage.textContent = '✗ ' + (field.validationMessage || 'Please check this field.');
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
  if (currentStep === 4 && form.password.value.length < 8) {
    setFieldError(form.password, 'Password must be at least 8 characters.');
    return false;
  }
  return true;
}

async function submitStep() {
  // Submit current step data to backend API
  if (!validateCurrentStep()) return false;

  try {
    const formData = new FormData(form);
    const endpoint = `/company/register/step${currentStep}`;
    
    const response = await fetch(endpoint, {
      method: 'POST',
      body: formData
    });

    const data = await response.json();

    if (data.success) {
      if (currentStep === 1) {
        // Move to OTP verification for step 1
        setFieldSuccess('OTP sent to your email and phone. Please check.');
        return 'verify_otp';
      } else if (currentStep < 5) {
        setFieldSuccess(data.message || 'Step completed successfully');
        setTimeout(() => {
          showStep(data.next_step);
        }, 1000);
        return true;
      } else {
        // Final submission
        showSuccessResult(data);
        return true;
      }
    } else {
      const errorMsg = data.message || data.errors ? Object.values(data.errors).flat()[0] : 'Error processing request';
      setFieldError(form, errorMsg);
      return false;
    }
  } catch (error) {
    setFieldError(form, `Network error: ${error.message}`);
    return false;
  }
}

async function verifyOTPs() {
  // Verify OTPs for step 1
  const panel = panels[0];
  const email = panel.querySelector('input[name="official_email"]').value;
  const emailOtp = panel.querySelector('input[name="email_otp"]').value;
  const phoneOtp = panel.querySelector('input[name="phone_otp"]').value;

  if (!emailOtp || !phoneOtp) {
    setFieldError(form, 'Please enter both OTPs.');
    return false;
  }

  try {
    const response = await fetch('/company/register/verify-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: email,
        email_otp: emailOtp,
        phone_otp: phoneOtp
      })
    });

    const data = await response.json();

    if (data.success) {
      otpVerified = data.results;
      setFieldSuccess('OTP verified successfully!');
      setTimeout(() => {
        showStep(2);
      }, 1500);
      return true;
    } else {
      setFieldError(form, data.message || 'OTP verification failed');
      return false;
    }
  } catch (error) {
    setFieldError(form, `Network error: ${error.message}`);
    return false;
  }
}

function showSuccessResult(data) {
  // Update step 5 (result panel) with response data
  const resultPanel = panels[4];
  const appIdElement = resultPanel.querySelector('.result-grid div:nth-child(1) b');
  const statusElement = resultPanel.querySelector('.result-grid div:nth-child(2) b');
  
  if (appIdElement) appIdElement.textContent = data.application_id;
  if (statusElement) statusElement.textContent = data.status.replace(/_/g, ' ').toUpperCase();
  
  showStep(5);
  setFieldSuccess('Registration submitted successfully! Check your email for updates.');
}

nextButton.addEventListener('click', async () => {
  // Move forward based on step
  if (currentStep === 1) {
    // Step 1: Validate then verify OTPs
    if (validateCurrentStep()) {
      const otpResult = await verifyOTPs();
      // Next button click for step 1 will trigger OTP verification instead
      // After OTP verification, user can proceed to step 2
    }
  } else {
    // Other steps: Just submit and move to next
    if (validateCurrentStep()) {
      await submitStep();
    }
  }
});

backButton.addEventListener('click', () => {
  if (currentStep > 1) showStep(Math.max(1, currentStep - 1));
});

document.querySelectorAll('input[type="file"]').forEach(input => {
  // Show the selected file name inside its upload area.
  input.addEventListener('change', () => {
    const label = input.closest('label');
    const text = label.querySelector('.drop-zone, .upload-mini span');
    if (input.files[0] && text) {
      const file = input.files[0];
      const fileSize = (file.size / (1024 * 1024)).toFixed(2);
      text.innerHTML = `✓ ${file.name} (${fileSize}MB)`;
    }
  });
});

// Add OTP auto-focus for better UX
document.querySelectorAll('input[name="email_otp"], input[name="phone_otp"]').forEach(input => {
  input.addEventListener('input', (e) => {
    if (e.target.value.length === 6) {
      // OTP complete, check if both are filled
      const panel = panels[0];
      const emailOtp = panel.querySelector('input[name="email_otp"]').value;
      const phoneOtp = panel.querySelector('input[name="phone_otp"]').value;
      if (emailOtp.length === 6 && phoneOtp.length === 6) {
        // Both OTPs ready, highlight the verify option or auto-show next button
        setFieldSuccess('Both OTPs received. Click Continue to verify.');
      }
    }
  });
});

showStep(1);
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
