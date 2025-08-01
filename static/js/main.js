// Main JavaScript functionality for parking reservation system

function initializeBookingForm() {
    try {
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
    } catch (e) {
        console.error('Ошибка при инициализации формы бронирования:', e);
    }
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
    try {
        const form = document.getElementById('bookingForm');
        const submitBtn = document.getElementById('submitBtn');
        
        if (!form || !submitBtn) {
            console.warn('Форма или кнопка отправки не найдены');
            return;
        }
        
        form.addEventListener('input', function() {
            try {
                if (validateForm()) {
                    submitBtn.disabled = false;
                } else {
                    submitBtn.disabled = true;
                }
            } catch (e) {
                console.error('Ошибка при валидации формы:', e);
            }
        });
        
        form.addEventListener('submit', function(e) {
            try {
                if (!validateForm()) {
                    e.preventDefault();
                    showValidationNotification(['Пожалуйста, заполните все обязательные поля корректно']);
                }
            } catch (e) {
                console.error('Ошибка при отправке формы:', e);
                e.preventDefault();
            }
        });
    } catch (e) {
        console.error('Ошибка при инициализации валидации формы:', e);
    }
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
            if (!field) {
                console.warn('Поле не найдено:', fieldId);
                return; // Пропускаем если поле не найдено
            }
            
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
                
                // Дополнительная проверка на случай, если label все еще null
                if (!label) {
                    console.warn('Label не найден для поля:', fieldId);
                }
                
                // Получаем текст label или используем fallback с дополнительными проверками
                let fieldName = fieldId; // fallback
                if (label && label.textContent && typeof label.textContent === 'string') {
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
    if (!field || !field.parentNode) {
        console.warn('showFieldError: поле или его родитель не найдены');
        return;
    }
    
    hideFieldError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    
    try {
        field.parentNode.appendChild(errorDiv);
        field.classList.add('error');
    } catch (e) {
        console.error('Ошибка при добавлении ошибки поля:', e);
    }
}

function hideFieldError(field) {
    if (!field || !field.parentNode) return;
    
    try {
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
        field.classList.remove('error');
    } catch (e) {
        console.error('Ошибка при скрытии ошибки поля:', e);
    }
}

function showValidationNotification(errors) {
    if (!errors || errors.length === 0) return;
    
    try {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.validation-notification');
        existingNotifications.forEach(notification => {
            try {
                notification.remove();
            } catch (e) {
                console.warn('Ошибка при удалении уведомления:', e);
            }
        });
        
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
    } catch (e) {
        console.error('Ошибка при создании уведомления:', e);
    }
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        try {
            if (notification && notification.parentNode) {
                notification.remove();
            }
        } catch (e) {
            console.warn('Ошибка при автоматическом удалении уведомления:', e);
        }
    }, 5000);
    
    // Close button functionality
    try {
        const closeBtn = notification.querySelector('.close-notification');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                try {
                    notification.remove();
                } catch (e) {
                    console.warn('Ошибка при закрытии уведомления:', e);
                }
            });
        }
    } catch (e) {
        console.warn('Ошибка при настройке кнопки закрытия:', e);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    try {
        // Попытка инициализации сразу
        initializeBookingForm();
        
        // Если элементы не найдены, попробуем еще раз через небольшую задержку
        setTimeout(() => {
            try {
                const form = document.getElementById('bookingForm');
                if (!form) {
                    console.warn('Форма не найдена, повторная попытка инициализации...');
                    initializeBookingForm();
                }
            } catch (e) {
                console.error('Ошибка при повторной инициализации:', e);
            }
        }, 100);
        
        // Финальная попытка через 1 секунду
        setTimeout(() => {
            try {
                const form = document.getElementById('bookingForm');
                if (!form) {
                    console.error('Форма не найдена после всех попыток');
                }
            } catch (e) {
                console.error('Ошибка при финальной проверке формы:', e);
            }
        }, 1000);
    } catch (e) {
        console.error('Ошибка при инициализации приложения:', e);
    }
});

// Make functions globally available
window.updatePriceCalculation = updatePriceCalculation;
window.calculateAndDisplayPrice = calculateAndDisplayPrice;
