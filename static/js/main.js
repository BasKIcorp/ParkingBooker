// Main JavaScript functionality for parking reservation system

function initializeBookingForm() {
    // Initialize new date/time selection
    initializeDateTimeSelection();
    // Initialize phone input formatting
    initializePhoneFormatting();
    // Initialize form validation
    initializeFormValidation();
}

function initializeDateTimeSelection() {
    const startDateInput = document.getElementById('booking_start_date');
    const startTimeInput = document.getElementById('booking_start_time');
    const endDateInput = document.getElementById('booking_end_date');
    const endTimeInput = document.getElementById('booking_end_time');
    const selectedTimeDisplay = document.getElementById('selectedTimeDisplay');
    const submitBtn = document.getElementById('submitBtn');

    function pad2(n) { return n < 10 ? '0' + n : n; }
    function roundToNextHour(date) {
        let d = new Date(date);
        d.setSeconds(0, 0);
        if (d.getMinutes() > 0) {
            d.setHours(d.getHours() + 1);
            d.setMinutes(0);
        }
        return d;
    }

    function forceZeroMinutes(input) {
        if (input.value && input.value.length === 5) {
            let [h, m] = input.value.split(':');
            if (m !== '00') {
                input.value = pad2(h) + ':00';
            }
        }
    }

    function updateTimeLimits() {
        // Ограничения для времени начала (start)
        const todayStr = (new Date()).toISOString().slice(0, 10);
        startTimeInput.step = 3600;
        endTimeInput.step = 3600;
        startTimeInput.min = '00:00';
        startTimeInput.max = '23:00';
        endTimeInput.min = '00:00';
        endTimeInput.max = '23:00';
        if (startDateInput.value === todayStr) {
            // min = ближайший следующий час
            let now = roundToNextHour(new Date());
            startTimeInput.min = pad2(now.getHours()) + ':00';
        }
        // Ограничения для времени конца (end)
        if (startDateInput.value && endDateInput.value && startDateInput.value === endDateInput.value) {
            if (startTimeInput.value) {
                let h = parseInt(startTimeInput.value.split(':')[0]);
                let minEnd = pad2(h + 1) + ':00';
                endTimeInput.min = minEnd;
            } else {
                endTimeInput.min = '01:00';
            }
        } else {
            endTimeInput.min = '00:00';
        }
    }

    function handleTimeInput(e) {
        forceZeroMinutes(e.target);
        updateTimeLimits();
        updateSelectedTimeDisplay();
    }

    startDateInput.addEventListener('change', function() {
        updateTimeLimits();
        // Если дата конца совпадает с началом, выставить минуты в 00
        forceZeroMinutes(startTimeInput);
        forceZeroMinutes(endTimeInput);
        updateSelectedTimeDisplay();
    });
    startTimeInput.addEventListener('change', handleTimeInput);
    endDateInput.addEventListener('change', function() {
        updateTimeLimits();
        forceZeroMinutes(endTimeInput);
        updateSelectedTimeDisplay();
    });
    endTimeInput.addEventListener('change', handleTimeInput);

    // Первичная инициализация
    updateTimeLimits();
    forceZeroMinutes(startTimeInput);
    forceZeroMinutes(endTimeInput);
}

function initializePhoneFormatting() {
    const phoneInput = document.getElementById('phone');
    phoneInput.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        // Handle different starting digits
        if (value.startsWith('8')) {
            value = '7' + value.slice(1);
        }
        if (value.startsWith('7') && value.length <= 11) {
            // Format as +7 (XXX) XXX-XX-XX
            let formatted = '+7';
            if (value.length > 1) {
                formatted += ' (' + value.slice(1, 4);
            }
            if (value.length >= 5) {
                formatted += ') ' + value.slice(4, 7);
            }
            if (value.length >= 8) {
                formatted += '-' + value.slice(7, 9);
            }
            if (value.length >= 10) {
                formatted += '-' + value.slice(9, 11);
            }
            e.target.value = formatted;
        } else if (value.length <= 10) {
            // Assume Russian number without country code
            let formatted = '+7';
            if (value.length > 0) {
                formatted += ' (' + value.slice(0, 3);
            }
            if (value.length >= 4) {
                formatted += ') ' + value.slice(3, 6);
            }
            if (value.length >= 7) {
                formatted += '-' + value.slice(6, 8);
            }
            if (value.length >= 9) {
                formatted += '-' + value.slice(8, 10);
            }
            e.target.value = formatted;
        }
        validateForm();
    });
    phoneInput.addEventListener('blur', function(e) {
        validateForm();
    });
    // Prevent non-numeric input except for formatting characters
    phoneInput.addEventListener('keypress', function(e) {
        const allowedChars = /[0-9\+\-\(\)\ ]/;
        if (!allowedChars.test(e.key) && !['Backspace', 'Delete', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
            e.preventDefault();
        }
    });
}

function initializeFormValidation() {
    const form = document.getElementById('bookingForm');
    const inputs = form.querySelectorAll('input[required]');
    
    inputs.forEach(input => {
        input.addEventListener('input', validateForm);
        input.addEventListener('change', validateForm);
    });

    // Initial validation
    validateForm();
}

// validateForm: добавить проверку диапазона дат/времени
function validateForm() {
    const firstName = document.getElementById('first_name').value.trim();
    const lastName = document.getElementById('last_name').value.trim();
    const phone = document.getElementById('phone').value.trim();
    const dataConsent = document.getElementById('data_consent').checked;
    const submitBtn = document.getElementById('submitBtn');
    const phoneInput = document.getElementById('phone');

    const startDate = document.getElementById('booking_start_date').value;
    const startTime = document.getElementById('booking_start_time').value;
    const endDate = document.getElementById('booking_end_date').value;
    const endTime = document.getElementById('booking_end_time').value;

    let valid = true;
    if (!firstName || !lastName || !phone || !dataConsent) valid = false;
    if (!startDate || !startTime || !endDate || !endTime) valid = false;
    if (startDate && startTime && endDate && endTime) {
        const now = new Date();
        const startDT = new Date(startDate + 'T' + startTime);
        const endDT = new Date(endDate + 'T' + endTime);
        if (startDT < now) valid = false;
        if (endDT <= startDT) valid = false;
    } else {
        valid = false;
    }
    // Строгая валидация телефона
    if (phone && !validatePhoneNumber(phone)) {
        valid = false;
        phoneInput.classList.add('is-invalid');
        showFieldError(phoneInput, 'Введите номер в формате +7 (XXX) XXX-XX-XX');
    } else {
        phoneInput.classList.remove('is-invalid');
        hideFieldError(phoneInput);
    }
    submitBtn.disabled = !valid;
}

function validatePhoneNumber(phone) {
    // Remove all non-digit characters
    const phoneDigits = phone.replace(/\D/g, '');
    // Строгий российский формат: +7XXXXXXXXXX
    return /^7\d{10}$/.test(phoneDigits);
}

function showFieldError(field, message) {
    // Remove existing error
    hideFieldError(field);
    
    // Add error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

function hideFieldError(field) {
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
}

// Utility functions
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit', 
        year: 'numeric'
    });
}

function formatTime(hour) {
    return `${String(hour).padStart(2, '0')}:00`;
}

function updateSelectedTimeDisplay() {
    const startDateVal = document.getElementById('booking_start_date').value;
    const startTimeVal = document.getElementById('booking_start_time').value;
    const endDateVal = document.getElementById('booking_end_date').value;
    const endTimeVal = document.getElementById('booking_end_time').value;
    const selectedTimeDisplay = document.getElementById('selectedTimeDisplay');
    if (startDateVal && startTimeVal && endDateVal && endTimeVal) {
        const startDT = new Date(startDateVal + 'T' + startTimeVal);
        const endDT = new Date(endDateVal + 'T' + endTimeVal);
        if (endDT > startDT) {
            const startDateFormatted = startDT.toLocaleDateString('ru-RU', {day: '2-digit', month: '2-digit', year: 'numeric'});
            const endDateFormatted = endDT.toLocaleDateString('ru-RU', {day: '2-digit', month: '2-digit', year: 'numeric'});
            const startTimeFormatted = startTimeVal;
            const endTimeFormatted = endTimeVal;
            selectedTimeDisplay.innerHTML = `
                <div>
                    <i class="fas fa-calendar-check me-2"></i>
                    <strong>${startDateFormatted} ${startTimeFormatted}</strong><br>
                    <span>—</span><br>
                    <strong>${endDateFormatted} ${endTimeFormatted}</strong>
                </div>
            `;
            selectedTimeDisplay.classList.add('has-selection');
        } else {
            selectedTimeDisplay.innerHTML = '<span class="text-danger">Время конца должно быть позже времени начала</span>';
            selectedTimeDisplay.classList.remove('has-selection');
        }
    } else {
        selectedTimeDisplay.innerHTML = '<div class="text-muted">Выберите дату и время начала и конца</div>';
        selectedTimeDisplay.classList.remove('has-selection');
    }
    updateFinalPrice();
}

function updateFinalPrice() {
    const startDate = document.getElementById('booking_start_date').value;
    const startTime = document.getElementById('booking_start_time').value;
    const endDate = document.getElementById('booking_end_date').value;
    const endTime = document.getElementById('booking_end_time').value;
    const finalPriceBlock = document.getElementById('finalPrice');
    const finalPriceValue = document.getElementById('finalPriceValue');
    let pricePerHour = window.hourlyPrice;
    if (!pricePerHour) {
        pricePerHour = Number(document.body.dataset.hourlyPrice) || 0;
    }
    if (startDate && startTime && endDate && endTime) {
        const startDT = new Date(startDate + 'T' + startTime);
        const endDT = new Date(endDate + 'T' + endTime);
        if (endDT > startDT) {
            // Только целые часы между start и end
            let hours = (endDT - startDT) / (1000 * 60 * 60);
            finalPriceValue.textContent = hours * pricePerHour;
            finalPriceBlock.style.display = '';
            return;
        }
    }
    finalPriceValue.textContent = '0';
    finalPriceBlock.style.display = 'none';
}

// Handle form submission
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('bookingForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            // Add loading state
            const submitBtn = document.getElementById('submitBtn');
            const originalText = submitBtn.innerHTML;
            
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Обработка...';
            submitBtn.disabled = true;
            
            // Form will submit naturally, this just provides user feedback
        });
    }
});

// Auto-refresh availability every 5 minutes
setInterval(function() {
    // Only refresh if user hasn't made a selection
    if (!selectedDate) {
        window.location.reload();
    }
}, 5 * 60 * 1000);

// Initialize when DOM is ready (only if not already initialized)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        if (typeof initializeBookingForm === 'function') {
            initializeBookingForm();
        }
    });
} else {
    // DOM is already ready
    if (typeof initializeBookingForm === 'function') {
        initializeBookingForm();
    }
}
