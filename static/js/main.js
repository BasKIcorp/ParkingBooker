// Main JavaScript functionality for parking reservation system

function initializeBookingForm() {
    // Проверяем, что все необходимые элементы загружены
    const requiredElements = [
        'bookingForm',
        'first_name',
        'last_name',
        'phone',
        'start_date',
        'end_date',
        'data_consent'
    ];
    
    const missingElements = requiredElements.filter(id => !document.getElementById(id));
    if (missingElements.length > 0) {
        console.warn('Не найдены элементы:', missingElements);
        return;
    }
    
    // Initialize date selection
    initializeDateSelection();
    // Initialize phone input formatting
    initializePhoneFormatting();
    // Initialize form validation
    initializeFormValidation();
    // Initialize vehicle type selection
    initializeVehicleTypeSelection();
}

function initializeVehicleTypeSelection() {
    const isMinibusCheckbox = document.getElementById('is_minibus');
    const vehicleTypeHidden = document.getElementById('vehicle_type');
    const carTariffs = document.getElementById('carTariffs');
    const minibusTariffs = document.getElementById('minibusTariffs');
    
    function updateVehicleType() {
        if (isMinibusCheckbox.checked) {
            vehicleTypeHidden.value = 'minibus';
            carTariffs.style.display = 'none';
            minibusTariffs.style.display = 'block';
        } else {
            vehicleTypeHidden.value = 'car';
            carTariffs.style.display = 'block';
            minibusTariffs.style.display = 'none';
        }
        updatePriceCalculation();
    }
    
    isMinibusCheckbox.addEventListener('change', updateVehicleType);
    
    // Initial setup
    updateVehicleType();
}

function initializeDateSelection() {
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    const isMinibusCheckbox = document.getElementById('is_minibus');
    const submitBtn = document.getElementById('submitBtn');

    function updateDateLimits() {
        const todayStr = (new Date()).toISOString().slice(0, 10);
        
        // Ограничения для даты выезда
        if (startDateInput.value) {
            endDateInput.min = startDateInput.value;
        }
        
        // Если дата заезда сегодня, то выезд минимум завтра
        if (startDateInput.value === todayStr) {
            const tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            endDateInput.min = tomorrow.toISOString().slice(0, 10);
        }
    }

    function updatePriceCalculation() {
        if (startDateInput.value && endDateInput.value) {
            const startDate = new Date(startDateInput.value);
            const endDate = new Date(endDateInput.value);
            const vehicleType = isMinibusCheckbox.checked ? 'minibus' : 'car';
            
            if (endDate > startDate) {
                const daysDiff = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));
                calculateAndDisplayPrice(daysDiff, vehicleType);
            }
        }
    }

    startDateInput.addEventListener('change', function() {
        updateDateLimits();
        updatePriceCalculation();
    });
    
    endDateInput.addEventListener('change', function() {
        updatePriceCalculation();
    });

    // Первичная инициализация
    updateDateLimits();
}

function initializePhoneFormatting() {
    const phoneInput = document.getElementById('phone');
    phoneInput.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        
        // Если номер начинается с 8, заменяем на 7
        if (value.startsWith('8')) {
            value = '7' + value.substring(1);
        }
        
        // Если номер 10 цифр и не начинается с 7 или 8, добавляем 7 в начало
        if (value.length === 10 && !value.startsWith('7') && !value.startsWith('8')) {
            value = '7' + value;
        }
        
        // Форматируем номер только если он начинается с 7
        if (value.length > 0 && value.startsWith('7')) {
            if (value.length <= 3) {
                value = '+7 (' + value.substring(1);
            } else if (value.length <= 6) {
                value = '+7 (' + value.substring(1, 4) + ') ' + value.substring(4);
            } else if (value.length <= 8) {
                value = '+7 (' + value.substring(1, 4) + ') ' + value.substring(4, 7) + '-' + value.substring(7);
            } else if (value.length <= 10) {
                value = '+7 (' + value.substring(1, 4) + ') ' + value.substring(4, 7) + '-' + value.substring(7, 9) + '-' + value.substring(9);
            } else {
                value = '+7 (' + value.substring(1, 4) + ') ' + value.substring(4, 7) + '-' + value.substring(7, 9) + '-' + value.substring(9, 11);
            }
        } else if (value.length > 0) {
            // Если номер не начинается с 7, оставляем как есть
            value = value;
        }
        
        e.target.value = value;
    });
}

function updatePriceCalculation() {
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    const isMinibusCheckbox = document.getElementById('is_minibus');
    
    if (startDateInput.value && endDateInput.value) {
        const startDate = new Date(startDateInput.value);
        const endDate = new Date(endDateInput.value);
        const vehicleType = isMinibusCheckbox.checked ? 'minibus' : 'car';
        
        if (endDate > startDate) {
            const daysDiff = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));
            calculateAndDisplayPrice(daysDiff, vehicleType);
        }
    }
}

function calculateAndDisplayPrice(totalDays, vehicleType) {
    const finalPriceBlock = document.getElementById('finalPrice');
    const totalDaysSpan = document.getElementById('totalDays');
    const vehicleTypeDisplay = document.getElementById('vehicleTypeDisplay');
    const dailyPriceSpan = document.getElementById('dailyPrice');
    const finalPriceValue = document.getElementById('finalPriceValue');
    
    // Get settings from data attributes or use defaults
    const dailyPrice1_25 = 350; // 1-25 сутки
    const dailyPrice26_plus = 150; // 26+ сутки
    const minibusPrice = 700; // Микроавтобус
    
    let totalPrice = 0;
    let dailyPriceText = '';
    
    if (vehicleType === 'minibus') {
        totalPrice = minibusPrice * totalDays;
        dailyPriceText = `${minibusPrice} ₽`;
        vehicleTypeDisplay.textContent = 'Микроавтобус';
    } else {
        if (totalDays <= 25) {
            totalPrice = dailyPrice1_25 * totalDays;
            dailyPriceText = `${dailyPrice1_25} ₽`;
        } else {
            const first25Days = dailyPrice1_25 * 25;
            const remainingDays = dailyPrice26_plus * (totalDays - 25);
            totalPrice = first25Days + remainingDays;
            dailyPriceText = `${dailyPrice1_25} ₽ (1-25) + ${dailyPrice26_plus} ₽ (26+)`;
        }
        vehicleTypeDisplay.textContent = 'Легковой автомобиль';
    }
    
    totalDaysSpan.textContent = totalDays;
    dailyPriceSpan.textContent = dailyPriceText;
    finalPriceValue.textContent = `${totalPrice} ₽`;
    finalPriceBlock.style.display = 'block';
}

function initializeFormValidation() {
    const form = document.getElementById('bookingForm');
    const submitBtn = document.getElementById('submitBtn');
    
    if (!form || !submitBtn) return;
    
    form.addEventListener('input', function() {
        if (validateForm()) {
            submitBtn.disabled = false;
        } else {
            submitBtn.disabled = true;
        }
    });
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Clear previous errors
        clearAllFieldErrors();
        
        // Basic client-side validation
        const clientErrors = validateForm();
        if (!clientErrors) {
            showValidationNotification(['Пожалуйста, заполните все обязательные поля корректно']);
            return;
        }
        
        // Show loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Отправка...</span>';
        
        // Prepare form data
        const formData = new FormData(form);
        
        // Send AJAX request
        fetch(form.action, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Success - redirect to success page
                window.location.href = data.redirect_url;
            } else {
                // Show server-side errors
                showServerErrors(data.errors, data.field_errors);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showValidationNotification(['Произошла ошибка при отправке формы. Попробуйте еще раз.']);
        })
        .finally(() => {
            // Reset button state
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-calendar-check"></i><span>Забронировать</span>';
        });
    });
}

function validateForm() {
    try {
        const requiredFields = [
            'first_name',
            'last_name', 
            'phone',
            'start_date',
            'end_date'
        ];
        
        const errors = [];
        
        // Check required fields
        requiredFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (!field) return; // Пропускаем если поле не найдено
            
            const fieldValue = field.value || '';
            if (!fieldValue.trim()) {
                // Находим label для поля, учитывая структуру HTML
                let label = field.previousElementSibling;
                
                // Если предыдущий элемент не label, ищем label в родительском элементе
                if (!label || label.tagName !== 'LABEL') {
                    const parentGroup = field.closest('.form-group');
                    if (parentGroup) {
                        label = parentGroup.querySelector('label[for="' + fieldId + '"]');
                    }
                }
                
                // Получаем текст label или используем fallback с дополнительными проверками
                let fieldName = fieldId; // fallback
                if (label && label.textContent) {
                    fieldName = label.textContent.replace('*', '').trim();
                }
                
                errors.push(`${fieldName} обязательно для заполнения`);
                showFieldError(field, 'Это поле обязательно для заполнения');
            } else {
                hideFieldError(field);
            }
        });
        
        // Validate phone number
        const phoneField = document.getElementById('phone');
        if (phoneField && phoneField.value && !validatePhoneNumber(phoneField.value)) {
            errors.push('Неверный формат номера телефона');
            showFieldError(phoneField, 'Введите номер в формате +7 (XXX) XXX-XX-XX');
        }
        
        // Validate dates
        const startDate = document.getElementById('start_date');
        const endDate = document.getElementById('end_date');
        if (startDate && endDate && startDate.value && endDate.value) {
            try {
                const start = new Date(startDate.value);
                const end = new Date(endDate.value);
                const today = new Date();
                today.setHours(0, 0, 0, 0);
                
                if (start < today) {
                    errors.push('Дата заезда не может быть в прошлом');
                    showFieldError(startDate, 'Выберите дату не ранее сегодняшнего дня');
                }
                
                if (end <= start) {
                    errors.push('Дата выезда должна быть позже даты заезда');
                    showFieldError(endDate, 'Дата выезда должна быть позже даты заезда');
                }
            } catch (e) {
                console.warn('Ошибка при валидации дат:', e);
            }
        }
        
        // Check consent
        const consentCheckbox = document.getElementById('data_consent');
        if (!consentCheckbox || !consentCheckbox.checked) {
            errors.push('Необходимо согласие на обработку данных');
        }
        
        return errors.length === 0;
    } catch (e) {
        console.error('Ошибка в validateForm:', e);
        return false;
    }
}

function validatePhoneNumber(phone) {
    if (!phone || typeof phone !== 'string') return false;
    
    // Remove all non-digit characters
    const digits = phone.replace(/\D/g, '');
    
    // Russian phone patterns - более гибкие
    const patterns = [
        /^7\d{10}$/,     // +7XXXXXXXXXX
        /^8\d{10}$/,     // 8XXXXXXXXXX
        /^\d{10}$/,      // XXXXXXXXXX (assume Russian)
        /^\d{11}$/       // 11 цифр (с кодом страны)
    ];
    
    return patterns.some(pattern => pattern.test(digits));
}

function showFieldError(field, message) {
    if (!field) return;
    
    hideFieldError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    
    if (field.parentNode) {
        field.parentNode.appendChild(errorDiv);
        field.classList.add('error');
    }
}

function hideFieldError(field) {
    if (!field || !field.parentNode) return;
    
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
    field.classList.remove('error');
}

function showValidationNotification(errors) {
    if (!errors || errors.length === 0) return;
    
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.validation-notification');
    existingNotifications.forEach(notification => notification.remove());
    
    // Create new notification
    const notification = document.createElement('div');
    notification.className = 'validation-notification error';
    notification.innerHTML = `
        <div class="notification-content">
            <h4>Ошибки в форме:</h4>
            <ul>
                ${errors.map(error => `<li>${error}</li>`).join('')}
            </ul>
            <button type="button" class="close-notification">&times;</button>
        </div>
    `;
    
    if (document.body) {
        document.body.appendChild(notification);
    }
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
    
    // Close button functionality
    const closeBtn = notification.querySelector('.close-notification');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            notification.remove();
        });
    }
}

function showServerErrors(errors, fieldErrors) {
    // Show general errors
    if (errors && errors.length > 0) {
        showValidationNotification(errors);
    }
    
    // Show field-specific errors
    if (fieldErrors) {
        Object.keys(fieldErrors).forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                showFieldError(field, fieldErrors[fieldId]);
            }
        });
    }
}

function clearAllFieldErrors() {
    const errorElements = document.querySelectorAll('.field-error');
    errorElements.forEach(error => error.remove());
    
    const errorFields = document.querySelectorAll('.error');
    errorFields.forEach(field => field.classList.remove('error'));
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Попытка инициализации сразу
    initializeBookingForm();
    
    // Если элементы не найдены, попробуем еще раз через небольшую задержку
    setTimeout(() => {
        const form = document.getElementById('bookingForm');
        if (!form) {
            console.warn('Форма не найдена, повторная попытка инициализации...');
            initializeBookingForm();
        }
    }, 100);
    
    // Финальная попытка через 1 секунду
    setTimeout(() => {
        const form = document.getElementById('bookingForm');
        if (!form) {
            console.error('Форма не найдена после всех попыток');
        }
    }, 1000);
});

// Make functions globally available
window.updatePriceCalculation = updatePriceCalculation;
window.calculateAndDisplayPrice = calculateAndDisplayPrice;
