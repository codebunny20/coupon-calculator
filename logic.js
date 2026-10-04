const calculatorForm = document.querySelector('.calculator-form');
const settingsButton = document.getElementById('settings');
const settingsModal = document.getElementById('settings-modal');
const closeSettingsButton = document.getElementById('close-settings');
const viewHistoryButton = document.getElementById('view-history-btn');
const historyModal = document.getElementById('history-modal');
const closeHistoryButton = document.getElementById('close-history');
const historyList = document.getElementById('history-list');
const historyError = document.getElementById('history-error');
const themeToggle = document.getElementById('theme-toggle');
const themeLabel = document.getElementById('theme-label');
const originalPriceInput = document.querySelector('input[name="original_price"]');
const discountValue = document.getElementById('discount-value');
const quickButtons = document.querySelectorAll('.quick-btn');
const discountAmountOutput = document.getElementById('discount-amount');
const finalPriceOutput = document.getElementById('final-price');
const heroDiscountAmount = document.getElementById('hero-discount-amount');
const heroFinalPrice = document.getElementById('hero-final-price');
const errorOutput = document.getElementById('calc-error');
const multibuyForm = document.querySelector('.multibuy-form');
const multibuyDealType = document.getElementById('multibuy-deal-type');
const multibuyDealConfigs = document.querySelectorAll('.deal-config');
const multibuyRegular = document.getElementById('multibuy-regular');
const multibuyTotal = document.getElementById('multibuy-total');
const multibuySavings = document.getElementById('multibuy-savings');
const multibuyEffective = document.getElementById('multibuy-effective');
const multibuyError = document.getElementById('multibuy-error');

const themeStorageKey = 'coupon-calculator:theme';
let previewDebounceId;
let multibuyPreviewDebounceId;

function openSettingsModal() {
  if (!settingsModal) return;
  settingsModal.hidden = false;
  if (settingsButton) settingsButton.setAttribute('aria-expanded', 'true');
}

function closeSettingsModal() {
  if (!settingsModal) return;
  settingsModal.hidden = true;
  if (settingsButton) settingsButton.setAttribute('aria-expanded', 'false');
}

function setHistoryError(message) {
  if (!historyError) return;
  if (message) {
    historyError.textContent = message;
    historyError.hidden = false;
  } else {
    historyError.textContent = '';
    historyError.hidden = true;
  }
}

function openHistoryModal() {
  if (!historyModal) return;
  historyModal.hidden = false;
}

function closeHistoryModal() {
  if (!historyModal) return;
  historyModal.hidden = true;
}

function formatHistoryTime(value) {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value || 'Unknown time';
  }
  return parsed.toLocaleString();
}

async function deleteHistoryEntry(timestamp) {
  if (!timestamp) return;

  try {
    const response = await fetch('/history/delete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ timestamp }),
    });
    const data = await response.json();

    if (!response.ok || !data.ok || !Array.isArray(data.history)) {
      setHistoryError(data.error || 'Could not delete history item.');
      return;
    }

    renderHistory(data.history);
  } catch (error) {
    setHistoryError('Could not delete history item.');
  }
}

function renderHistory(entries) {
  if (!historyList) return;
  historyList.innerHTML = '';

  if (!entries.length) {
    const emptyItem = document.createElement('li');
    emptyItem.className = 'history-empty';
    emptyItem.textContent = 'No saved history yet.';
    historyList.appendChild(emptyItem);
    return;
  }

  entries.forEach((entry) => {
    const item = document.createElement('li');
    item.className = 'history-item';

    const itemContent = document.createElement('div');
    itemContent.className = 'history-item-content';

    const equation = document.createElement('p');
    equation.className = 'history-equation';
    equation.textContent = entry.equation || 'Equation unavailable';

    const meta = document.createElement('p');
    meta.className = 'history-meta';
    meta.textContent = formatHistoryTime(entry.timestamp);

    const deleteButton = document.createElement('button');
    deleteButton.type = 'button';
    deleteButton.className = 'history-delete';
    deleteButton.textContent = 'Delete';
    deleteButton.setAttribute('aria-label', `Delete history item for ${formatHistoryTime(entry.timestamp)}`);
    deleteButton.addEventListener('click', () => deleteHistoryEntry(entry.timestamp));

    itemContent.appendChild(equation);
    itemContent.appendChild(meta);
    item.appendChild(itemContent);
    item.appendChild(deleteButton);
    historyList.appendChild(item);
  });
}

async function loadHistory() {
  setHistoryError('');
  try {
    const response = await fetch('/history');
    const data = await response.json();
    if (!data.ok || !Array.isArray(data.history)) {
      setHistoryError('Could not load history.');
      renderHistory([]);
      return;
    }
    renderHistory(data.history);
  } catch (error) {
    setHistoryError('Could not load history.');
    renderHistory([]);
  }
}

function applyTheme(theme) {
  const normalizedTheme = theme === 'dark' ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', normalizedTheme);

  if (themeToggle) {
    const isDark = normalizedTheme === 'dark';
    themeToggle.checked = isDark;
    themeToggle.setAttribute('aria-pressed', isDark ? 'true' : 'false');
    themeToggle.setAttribute('aria-label', isDark ? 'Switch to light theme' : 'Switch to dark theme');
    if (themeLabel) {
      themeLabel.textContent = isDark ? 'Dark mode' : 'Light mode';
    }
  }
}

function getInitialTheme() {
  let savedTheme = null;
  try {
    savedTheme = localStorage.getItem(themeStorageKey);
  } catch (error) {
    savedTheme = null;
  }

  if (savedTheme === 'light' || savedTheme === 'dark') {
    return savedTheme;
  }

  return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

applyTheme(getInitialTheme());

if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
    const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
    applyTheme(nextTheme);
    try {
      localStorage.setItem(themeStorageKey, nextTheme);
    } catch (error) {
      // Ignore storage errors.
    }
  });
}

if (settingsButton) {
  settingsButton.addEventListener('click', () => {
    openSettingsModal();
  });
}

if (closeSettingsButton) {
  closeSettingsButton.addEventListener('click', () => {
    closeSettingsModal();
  });
}

if (viewHistoryButton) {
  viewHistoryButton.addEventListener('click', async () => {
    openHistoryModal();
    await loadHistory();
  });
}

if (closeHistoryButton) {
  closeHistoryButton.addEventListener('click', () => {
    closeHistoryModal();
  });
}

if (settingsModal) {
  settingsModal.addEventListener('click', (event) => {
    const target = event.target;
    if (target && target.closest && target.closest('[data-close-settings="true"]')) {
      closeSettingsModal();
    }
  });
}

if (historyModal) {
  historyModal.addEventListener('click', (event) => {
    const target = event.target;
    if (target && target.closest && target.closest('[data-close-history="true"]')) {
      closeHistoryModal();
    }
  });
}

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && settingsModal && !settingsModal.hidden) {
    closeSettingsModal();
  }
  if (event.key === 'Escape' && historyModal && !historyModal.hidden) {
    closeHistoryModal();
  }
});

// Keep the user's scroll position after server-side form submit reloads the page.
// const scrollKey = 'coupon-calculator:scrollY';
// const savedScrollY = sessionStorage.getItem(scrollKey);
// if (savedScrollY !== null) {
//   window.scrollTo(0, Number(savedScrollY) || 0);
//   sessionStorage.removeItem(scrollKey);
// }

// if (calculatorForm) {
//   calculatorForm.addEventListener('submit', () => {
//     sessionStorage.setItem(scrollKey, String(window.scrollY));
//   });
// }

function clampPercent(value) {
  const numeric = Number(value) || 0;
  return Math.min(100, Math.max(0, numeric));
}

quickButtons.forEach((button) => {
  button.addEventListener('click', () => {
    if (!discountValue) return;
    const current = clampPercent(discountValue.value || 0);
    const step = Number(button.dataset.step || 0);
    const nextValue = clampPercent(current + step);
    discountValue.value = nextValue;
    discountValue.dispatchEvent(new Event('input', { bubbles: true }));
  });
});

function hasCompleteInputs() {
  if (!originalPriceInput || !discountValue) return false;
  return originalPriceInput.value.trim() !== '' && discountValue.value.trim() !== '';
}

async function requestCalculation(endpoint) {
  if (!calculatorForm) return;

  const formData = new FormData(calculatorForm);

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      body: formData,
    });
    const data = await response.json();

    if (data.ok) {
      if (discountAmountOutput) discountAmountOutput.textContent = data.discount_amount;
      if (finalPriceOutput) finalPriceOutput.textContent = data.final_price;
      if (heroDiscountAmount) heroDiscountAmount.textContent = data.discount_amount;
      if (heroFinalPrice) heroFinalPrice.textContent = data.final_price;
      if (errorOutput) {
        errorOutput.textContent = '';
        errorOutput.hidden = true;
      }
    } else if (errorOutput) {
      errorOutput.textContent = data.error || 'Could not calculate right now.';
      errorOutput.hidden = false;
    }
  } catch (error) {
    if (errorOutput) {
      errorOutput.textContent = 'Could not calculate right now.';
      errorOutput.hidden = false;
    }
  }
}

function queueLivePreview() {
  if (!hasCompleteInputs()) {
    if (errorOutput) {
      errorOutput.textContent = '';
      errorOutput.hidden = true;
    }
    return;
  }

  window.clearTimeout(previewDebounceId);
  previewDebounceId = window.setTimeout(() => {
    requestCalculation('/preview');
  }, 150);
}

function setMultibuyError(message) {
  if (!multibuyError) return;
  if (message) {
    multibuyError.textContent = message;
    multibuyError.hidden = false;
  } else {
    multibuyError.textContent = '';
    multibuyError.hidden = true;
  }
}

function setMultibuyConfigVisibility() {
  if (!multibuyDealType || !multibuyDealConfigs.length) return;
  const selectedDeal = multibuyDealType.value;

  multibuyDealConfigs.forEach((config) => {
    const isActive = config.dataset.deal === selectedDeal;
    config.hidden = !isActive;

    const inputs = config.querySelectorAll('input');
    inputs.forEach((input) => {
      input.disabled = !isActive;
    });
  });
}

function hasCompleteMultibuyInputs() {
  if (!multibuyForm || !multibuyDealType) return false;

  const unitPrice = multibuyForm.querySelector('input[name="unit_price"]');
  const quantity = multibuyForm.querySelector('input[name="quantity"]');
  if (!unitPrice || !quantity) return false;

  if (unitPrice.value.trim() === '' || quantity.value.trim() === '') {
    return false;
  }

  const selectedDeal = multibuyDealType.value;
  if (selectedDeal === 'buy_x_get_y_free') {
    const buyQty = multibuyForm.querySelector('input[name="buy_qty"]:not([disabled])');
    const freeQty = multibuyForm.querySelector('input[name="free_qty"]:not([disabled])');
    return Boolean(buyQty && freeQty && buyQty.value.trim() && freeQty.value.trim());
  }

  if (selectedDeal === 'x_for_y_items') {
    const bundleSize = multibuyForm.querySelector('input[name="bundle_size"]:not([disabled])');
    const payForQty = multibuyForm.querySelector('input[name="pay_for_qty"]:not([disabled])');
    return Boolean(bundleSize && payForQty && bundleSize.value.trim() && payForQty.value.trim());
  }

  const bundleSize = multibuyForm.querySelector('input[name="bundle_size"]:not([disabled])');
  const bundlePrice = multibuyForm.querySelector('input[name="bundle_price"]:not([disabled])');
  return Boolean(bundleSize && bundlePrice && bundleSize.value.trim() && bundlePrice.value.trim());
}

async function requestMultibuyCalculation(endpoint) {
  if (!multibuyForm) return;
  const formData = new FormData(multibuyForm);

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      body: formData,
    });
    const data = await response.json();

    if (!data.ok) {
      setMultibuyError(data.error || 'Could not calculate this deal.');
      return;
    }

    if (multibuyRegular) multibuyRegular.textContent = data.regular_total;
    if (multibuyTotal) multibuyTotal.textContent = data.deal_total;
    if (multibuySavings) multibuySavings.textContent = data.savings;
    if (multibuyEffective) multibuyEffective.textContent = data.effective_unit_price;
    setMultibuyError('');
  } catch (error) {
    setMultibuyError('Could not calculate this deal.');
  }
}

function queueMultibuyPreview() {
  if (!hasCompleteMultibuyInputs()) {
    setMultibuyError('');
    return;
  }

  window.clearTimeout(multibuyPreviewDebounceId);
  multibuyPreviewDebounceId = window.setTimeout(() => {
    requestMultibuyCalculation('/multibuy/preview');
  }, 150);
}

if (calculatorForm) {
  calculatorForm.addEventListener('input', queueLivePreview);
  calculatorForm.addEventListener('change', queueLivePreview);

  calculatorForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    await requestCalculation('/calculate');
  });

  calculatorForm.addEventListener('reset', () => {
    if (discountAmountOutput) discountAmountOutput.textContent = '$0.00';
    if (finalPriceOutput) finalPriceOutput.textContent = '$0.00';
    if (heroDiscountAmount) heroDiscountAmount.textContent = '$0.00';
    if (heroFinalPrice) heroFinalPrice.textContent = '$0.00';
    if (errorOutput) {
      errorOutput.textContent = '';
      errorOutput.hidden = true;
    }
  });
}

if (multibuyDealType) {
  setMultibuyConfigVisibility();
  multibuyDealType.addEventListener('change', () => {
    setMultibuyConfigVisibility();
    queueMultibuyPreview();
  });
}

if (multibuyForm) {
  multibuyForm.addEventListener('input', queueMultibuyPreview);
  multibuyForm.addEventListener('change', queueMultibuyPreview);

  multibuyForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    await requestMultibuyCalculation('/multibuy/calculate');
  });

  multibuyForm.addEventListener('reset', () => {
    window.setTimeout(() => {
      setMultibuyConfigVisibility();
      if (multibuyRegular) multibuyRegular.textContent = '$0.00';
      if (multibuyTotal) multibuyTotal.textContent = '$0.00';
      if (multibuySavings) multibuySavings.textContent = '$0.00';
      if (multibuyEffective) multibuyEffective.textContent = '$0.00';
      setMultibuyError('');
    }, 0);
  });
}
