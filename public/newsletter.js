// Newsletter signup handler for notu.us
// Loaded from splash page and lesson plans

async function handleSubscribe(e) {
  const form = e.target.closest('form');
  if (!form) return;
  const emailInput = form.querySelector('input[type="email"]');
  const email = emailInput.value;
  if (!email || !email.includes('@')) {
    alert('Please enter a valid email address.');
    return;
  }
  const btn = form.querySelector('button');
  const success = form.parentElement.querySelector('.newsletter-success');
  btn.textContent = 'Sending...';
  btn.disabled = true;
  try {
    const res = await fetch('https://email-worker.nasirullah-mohammad.workers.dev/subscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, source: 'notu.us' })
    });
    if (res.ok) {
      success.classList.add('show');
      emailInput.value = '';
    } else {
      alert('Something went wrong. Try again or email us at studio@mohikontok.com');
    }
  } catch {
    alert('Network error. Please try again or email us at studio@mohikontok.com');
  }
  btn.textContent = 'Subscribe →';
  btn.disabled = false;
}